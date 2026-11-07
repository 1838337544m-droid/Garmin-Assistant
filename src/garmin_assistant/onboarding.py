"""Bilingual first-use prompt and localized presentation. Garmin payloads stay untouched."""
from functools import wraps
from .config import load_settings, save_settings
from .goals import SPORTS

WELCOME_TEXT=('欢迎首次使用佳明助手！\nWelcome to Garmin Assistant!\n\n'
              '请选择语言 / Please choose your language:\n1. 中文\n2. English')


def welcome(settings=None):
    settings=settings or load_settings()
    required=settings.language is None
    return {'language':settings.language,'language_selection_required':required,
            'message':WELCOME_TEXT if required else ('欢迎回来，佳明助手已准备就绪。' if settings.language=='zh' else 'Welcome back. Garmin Assistant is ready.'),
            'choices':[{'id':1,'label':'中文','language':'zh'},{'id':2,'label':'English','language':'en'}],
            'goal': settings.goal if not required else None,
            'goal_selection_required': not required and settings.goal is None,
            'goal_sports': [{'sport': sport, 'label': labels[settings.language=='en']} for sport,labels in SPORTS.items()] if not required else [],
            'next_step':'Reply 1/中文 or 2/English; the AI must call garmin_set_language with zh or en. Do not interpret the first number as a core-menu action until language is selected.' if required else None}


def choose_language(value):
    aliases={'1':'zh','中文':'zh','chinese':'zh','zh':'zh','2':'en','english':'en','en':'en'}
    language=aliases.get(value.strip().casefold())
    if not language:raise ValueError('Choose 1/中文 or 2/English')
    settings=save_settings(load_settings(),language=language)
    return settings


LEGACY_MENU_EN={
    1:('Sync data','Fill the interval since the previous sync and report gaps.'),
    2:("Assess tomorrow's training",'Sync first, then assess recovery and recent running against your goal.'),
    3:('View activities and details','Browse a date range or inspect one activity.'),
    4:('View sleep, heart rate and HRV','Read available health data for a selected date.'),
    5:('Compare steps, stress and Body Battery','Read date ranges for comparison.'),
    6:('Update running and rehabilitation research','Discover recent papers with citations and appraisal status.'),
    7:('View sync status and function menu','Check freshness or show the supported functions.'),
}

MENU_EN={
    1:LEGACY_MENU_EN[1],
    2:('Training progress and current status','Review 30-day activity frequency and metrics, plus 90-day health trends.'),
    3:('Fatigue and recovery','Compare personal trends, reported fatigue and soreness, and recent training volume.'),
    4:('Tomorrow’s training plan','Choose swimming, cycling or running, then set a target distance and time.'),
}

FLAG_EN={
    'hrv_trend_low':'The recent 2–3-night HRV mean is at least 15% below the personal reference; treat this as a recovery cue.',
    'sleep_short':'Latest sleep is short relative to the configured screening threshold or personal reference. Reassess tomorrow morning.',
    'resting_hr_high':'Resting heart rate on the last complete day is at least 7 bpm above the personal reference.',
    'recent_hard_or_long':'A harder or longer run occurred today or yesterday; prioritize an easy day.',
    'single_run_jump':'Planned distance exceeds 110% of the longest run in the last 30 days. This observational cue is not an individual injury probability or safety boundary.',
    'subjective_fatigue':'Reported fatigue is elevated; reduce training stress.',
    'pain_reported':'Pain was reported. Avoid quality training; stop if symptoms worsen and seek assessment if they persist.',
}

SOURCE_EN={
    'readiness2026':'Interpret subjective fatigue, sleep, stress and soreness alongside objective measures and individual references; do not clear training from one score.',
    'hrv2026':'Use multi-day HRV trends and individual references. Optimal thresholds and baseline strategies are not universally agreed.',
    'sleep2026':'Consider sleep duration and the personal reference; allow recovery and do not infer tonight\'s sleep from today\'s data.',
    'distance2025':'Review single-session distance relative to the longest run in the previous 30 days. Observational associations are not individual risk predictions or universal safety guarantees.',
    'rehab2024':'After tibial bone stress injury, return-to-running assessment includes symptoms, pain-free walking and professional review. This is not a universal rehabilitation prescription.',
    'intensity2025':'Match intensity distribution to training level; do not assume polarized training always outperforms pyramidal training or guarantees the fastest progress.',
    'fitness_fatigue':'Training produces both fitness and fatigue. Use the framework qualitatively; no personal response parameters or race-time predictions have been fitted.',
    'intensity_distribution':'Keep most training recoverable and individualize quality work. A rigid 80/20 split is not prescribed to every runner.',
    'daniels':'Distinguish easy, marathon-pace, threshold, interval and repetition purposes. Current training paces require current ability, not only a target result.',
}


def localize_result(result,language):
    if not isinstance(result,dict):return result
    out={**result,'language':language,'language_selection_required':False}
    if language!='en':return out
    if 'function_menu' in out:
        translations=LEGACY_MENU_EN if out.get('menu_variant')=='legacy' else MENU_EN
        out['function_menu']=[{**item,'command':translations[item['id']][0],'description':translations[item['id']][1]}
            if item.get('id') in translations else dict(item) for item in out['function_menu']]
    if 'restore_command' in out:out['restore_command']='Show original function menu / 显示原有功能菜单'
    if 'note' in out and 'function_menu' in out:out['note']='Hiding affects menu display only. Core tools remain available; custom items are user-authored prompt workflows.'
    if 'flags' in out:out['flags']=[{**f,'reason':FLAG_EN.get(f['code'],f['reason'])} for f in out['flags']]
    if 'recommendation' in out and 'sport' not in out:
        minutes=out.get('suggested_easy_minutes',0)
        out['recommendation']={
            'avoid_running':'Do not run tomorrow. Address reported illness or pain first; walking pain or focal bone pain needs professional assessment.',
            'insufficient_data':"There is not enough current data to assess tomorrow's running. Fill the missing records; do not schedule a hard session on this basis.",
            'recovery':'Prioritize recovery tomorrow. If free of pain and illness, consider comfortable walking or gentle activity; postpone hard running.',
            'easy_only':f'If free of pain and illness, consider about {minutes} minutes of conversational easy running. Stop if uncomfortable; postpone intervals and long runs.',
            'easy_if_well':f'If the morning recheck is normal and you are free of pain and illness, consider about {minutes} minutes of easy running. No configured under-recovery cue was detected.',
        }[out['decision']]
        # Preserve the higher-priority urgent advice rather than replacing it with generic pain advice.
        if result.get('urgent_symptoms'):
            out['recommendation']='Chest pain or fainting was reported. Stop exercise and seek medical care promptly; ongoing or severe symptoms require emergency care.'
        out['quality_note']='Even if eligible for quality training, reassess sleep, fatigue and symptoms tomorrow morning and consider the weekly plan.'
        out['morning_recheck']=["Sync last night's sleep and HRV",'Confirm no pain, illness or unusual fatigue','Warm up easily; reduce or stop if uncomfortable']
        out['training_logic']=['Keep most training conversational and easy; target race pace is not automatically easy-training pace.',
            'Build a consistent, recoverable routine before adding limited quality sessions. Avoid stacking harder days.',
            'Time to your goal depends on current ability; wearable data cannot guarantee the fastest completion date.']
    if 'sync' in out:out['sync']=localize_result(out['sync'],language)
    if out.get('goal') and 'race_pace' in out['goal']:out['goal']={**out['goal'],'race_pace':out['goal']['race_pace'].replace('略快于 ','faster than ')}
    if 'classic_models' in out:
        out['classic_models']=[{**m,'name':m['title'],'application':SOURCE_EN.get(m['id'],m['application'])} for m in out['classic_models']]
    if 'reviewed_sources' in out:
        out['reviewed_sources']=[{**s,'application':SOURCE_EN.get(s['id'],s['application'])} for s in out['reviewed_sources']]
    if 'research' in out:
        research=out['research']
        out['research']={**research,'reviewed_sources':[{**s,'application':SOURCE_EN.get(s['id'],s['application'])} for s in research.get('reviewed_sources',[])]}
    if 'model_application' in out:
        metrics=out.get('metrics',{})
        out['model_application']=[{'model_id':'fitness_fatigue','interpretation':f"Seven-day running distance: {metrics.get('running_km_7d')} km. Interpret with recovery signals; decision: {out.get('decision')}. This is qualitative, not a fitted fitness/fatigue score."},
            {'model_id':'intensity_distribution','interpretation':'The recovery screen helps decide whether to reduce training. A full personal intensity-distribution calculation was not performed.'},
            {'model_id':'daniels','interpretation':'Use conversational effort for easy running. Quality-training paces require current ability and recovery information; target race pace is not an automatic training prescription.'}]
    if 'heuristics' in out:out['heuristics']={**out['heuristics'],'note':'Pragmatic coaching thresholds, not validated personal optima or injury probabilities.'}
    return out


def language_guard(function):
    """First tool use asks for a language before any health/research operation."""
    @wraps(function)
    def wrapped(*args,**kwargs):
        settings=load_settings()
        if settings.language is None:return welcome(settings)
        return localize_result(function(*args,**kwargs),settings.language)
    return wrapped
