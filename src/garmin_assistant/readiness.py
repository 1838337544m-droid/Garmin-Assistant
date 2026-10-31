"""Explainable training suggestions. Heuristics, not a validated clearance score."""
import math
from datetime import date, timedelta
from statistics import median, mean


def number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)


def object_or_empty(value):
    return value if isinstance(value,dict) else {}


def assess(history, as_of, subjective=None, planned_km=None, sync_ok=True, goal=None):
    day = date.fromisoformat(as_of)
    goal=goal or {'distance_km':10,'minutes':60}
    distance,minutes_goal=goal['distance_km'],goal['minutes']
    if type(distance) not in (int,float) or type(minutes_goal) not in (int,float) or not 0<distance<=200 or not 0<minutes_goal<=1440:
        raise ValueError('Invalid training goal')
    pace_seconds=int(minutes_goal*60/distance)
    subject = dict(subjective or {})
    allowed = {'pain_0_10','fatigue_0_10','illness','pain_with_walking','focal_bone_pain','chest_pain','fainting'}
    if set(subject)-allowed:
        raise ValueError('Unknown subjective field')
    for k,v in subject.items():
        if v is None:continue
        if k in ('pain_0_10','fatigue_0_10'):
            if not number(v) or not 0 <= v <= 10:raise ValueError('Ratings must be 0 to 10')
        elif type(v) is not bool:raise ValueError('Symptom values must be boolean or null')
    if planned_km is not None and (not number(planned_km) or not 0 < planned_km <= 100):
        raise ValueError('planned_km must be positive and at most 100')
    def dated(kind):
        out={}
        for row in history.get(kind,[]):
            d=row.get('calendarDate','')
            try:parsed=date.fromisoformat(d)
            except (TypeError,ValueError):continue
            if day-timedelta(days=93) <= parsed <= day:out[d]=row
        return out
    sleep=dated('sleep_summaries');hrv=dated('hrv_summaries');daily=dated('daily_summaries')
    flags=[];missing=[];metrics={}
    def flag(code,why,source):flags.append({'code':code,'reason':why,'evidence_id':source})
    baseline_days=[(day-timedelta(days=i)).isoformat() for i in range(4,32)]
    hbase=[hrv.get(d,{}).get('lastNightAvg') for d in baseline_days]
    hbase=[v for v in hbase if number(v) and v>0]
    recent_days=[(day-timedelta(days=i)).isoformat() for i in range(3)]
    hrecent=[hrv.get(d,{}).get('lastNightAvg') for d in recent_days]
    hrecent=[v for v in hrecent if number(v) and v>0]
    metrics['hrv_baseline']=median(hbase) if len(hbase)>=14 else None
    metrics['hrv_baseline_days']=len(hbase)
    metrics['hrv_recent_mean']=round(mean(hrecent),1) if len(hrecent)>=2 else None
    current_hrv=hrv.get(as_of,{}).get('lastNightAvg')
    if metrics['hrv_baseline'] is None or metrics['hrv_recent_mean'] is None or not number(current_hrv) or current_hrv<=0:
        missing.append('hrv_current_and_baseline')
    elif metrics['hrv_recent_mean'] < .85*metrics['hrv_baseline']:
        flag('hrv_trend_low','最近 2–3 晚 HRV 平均值较个人基线低至少 15%，作为恢复不足的线索。','hrv2026')
    sleep_seconds=sleep.get(as_of,{}).get('sleepTimeSeconds')
    metrics['latest_sleep_hours']=round(sleep_seconds/3600,2) if number(sleep_seconds) and sleep_seconds>0 else None
    sbase=[sleep.get(d,{}).get('sleepTimeSeconds') for d in baseline_days]
    sbase=[s/3600 for s in sbase if number(s) and s>0]
    metrics['sleep_baseline_hours']=round(median(sbase),2) if len(sbase)>=14 else None
    if metrics['latest_sleep_hours'] is None:missing.append('current_sleep')
    elif metrics['latest_sleep_hours']<6 or (metrics['sleep_baseline_hours'] is not None and metrics['latest_sleep_hours']<metrics['sleep_baseline_hours']-1.5):
        flag('sleep_short','最新睡眠偏短，质量训练应降级并在明早复评。','sleep2026')
    rbase=[object_or_empty(daily.get(d,{}).get('heartRate')).get('restingValue') for d in baseline_days]
    rbase=[v for v in rbase if number(v) and v>0]
    # Today's daily summary is incomplete; compare the last completed calendar day.
    yesterday=(day-timedelta(days=1)).isoformat()
    rlatest=object_or_empty(daily.get(yesterday,{}).get('heartRate')).get('restingValue')
    metrics['resting_hr_baseline']=median(rbase) if len(rbase)>=14 else None
    metrics['last_complete_day_resting_hr']=rlatest if number(rlatest) and rlatest>0 else None
    if metrics['resting_hr_baseline'] is None or metrics['last_complete_day_resting_hr'] is None:
        missing.append('resting_hr_baseline_or_recent')
    elif rlatest>=metrics['resting_hr_baseline']+7:
        flag('resting_hr_high','上一完整日静息心率高于个人基线至少 7 次/分。','readiness2026')
    runs=[]
    for row in history.get('activities',[]):
        d=str(row.get('startTimeLocal',''))[:10]
        try:run_day=date.fromisoformat(d)
        except (ValueError,TypeError):continue
        kind=object_or_empty(row.get('activityType')).get('typeKey') or ''
        if ('running' in kind or kind in ('run','virtual_run')) and day-timedelta(days=34)<=run_day<=day:
            runs.append((run_day,row))
    recent=[r for d,r in runs if d>=day-timedelta(days=27)]
    distances=[r['distance']/1000 for d,r in runs if d>=day-timedelta(days=29) and number(r.get('distance')) and r['distance']>0]
    metrics['longest_run_30d_km']=round(max(distances),2) if distances else None
    metrics['runs_28d']=len(recent)
    metrics['running_km_7d']=round(sum(r['distance']/1000 for d,r in runs if d>=day-timedelta(days=6) and number(r.get('distance'))),2)
    metrics['hard_or_long_sessions_last_2_calendar_days']=sum(
        1 for d,r in runs if d>=day-timedelta(days=1) and
        ((number(r.get('aerobicTrainingEffect')) and r['aerobicTrainingEffect']>=3.5) or
         (number(r.get('anaerobicTrainingEffect')) and r['anaerobicTrainingEffect']>=2) or
         (number(r.get('duration')) and r['duration']>=3600)))
    if metrics['hard_or_long_sessions_last_2_calendar_days']:
        flag('recent_hard_or_long','今天或昨天存在较强/较长跑步训练，优先安排轻松日。','readiness2026')
    if planned_km and distances and planned_km > 1.1*max(distances):
        flag('single_run_jump','计划单次距离超过近 30 天最长跑的 110%；这是观察研究提示，不能视为个人伤病概率或安全界线。','distance2025')
    if subject.get('fatigue_0_10') is not None and subject['fatigue_0_10']>=7:
        flag('subjective_fatigue','主观疲劳较高，应减少训练刺激。','readiness2026')
    if subject.get('pain_0_10') is not None and 0<subject['pain_0_10']<4:
        flag('pain_reported','报告了疼痛；避免质量训练，症状不缓解或运动中加重应停止并评估。','rehab2024')
    required=('pain_0_10','fatigue_0_10','illness','pain_with_walking','focal_bone_pain','chest_pain','fainting')
    if any(subject.get(k) is None for k in required):missing.append('subjective_check')
    if not sync_ok:missing.append('fresh_complete_sync')
    urgent=subject.get('chest_pain') is True or subject.get('fainting') is True
    blocked=(urgent or subject.get('illness') is True or subject.get('pain_with_walking') is True or
             subject.get('focal_bone_pain') is True or (subject.get('pain_0_10') or 0)>=4)
    recovery_codes={'hrv_trend_low','sleep_short','resting_hr_high','subjective_fatigue'}
    recovery_count=sum(f['code'] in recovery_codes for f in flags)
    objective_missing=[m for m in missing if m!='subjective_check']
    if blocked:decision='avoid_running'
    elif objective_missing:decision='insufficient_data'
    elif recovery_count>=2 or (subject.get('fatigue_0_10') or 0)>=8:decision='recovery'
    elif flags:decision='easy_only'
    else:decision='easy_if_well'
    quality=not blocked and not missing and not flags and len(recent)>=8
    durations=[r['duration']/60 for r in recent if number(r.get('duration')) and r['duration']>0]
    minutes=round(min(40,max(10,.8*median(durations)))) if durations else 15
    if decision in ('avoid_running','recovery','insufficient_data'):minutes=0
    text={
        'avoid_running':'明天暂不跑步。先处理伤痛/疾病；步行痛或局部骨痛需专业评估。',
        'insufficient_data':'目前不足以判断明天适合跑步；先补齐最新同步及缺失记录，不安排强度课。',
        'recovery':'明天优先恢复；若无伤痛和生病，可考虑舒适步行或轻度活动，暂缓跑步强度课。',
        'easy_only':f'若无伤痛和生病，明天可考虑约 {minutes} 分钟谈话轻松跑；有不适即停止，暂缓间歇和长距离。',
        'easy_if_well':f'若明早复评正常且无伤痛和生病，可考虑约 {minutes} 分钟轻松跑；当前没有确定恢复不足信号。',
    }[decision]
    if urgent:text='报告胸痛或晕厥：停止运动并及时就医；若症状正在发生或严重，应立即急诊处理。'
    return {'as_of':as_of,'target_date':(day+timedelta(days=1)).isoformat(),'provisional':True,'urgent_symptoms':urgent,
            'decision':decision,'recommendation':text,'quality_session_eligible':quality,
            'quality_note':'即使具备质量课条件，也必须在明早同步后确认睡眠、疲劳和伤痛，再结合周计划决定。',
            'suggested_easy_minutes':minutes,'metrics':metrics,'flags':flags,'missing':missing,
            'goal':{'distance_km':distance,'target':f'under {minutes_goal:g} minutes','minutes':minutes_goal,
                    'race_pace':f'略快于 {pace_seconds//60}:{pace_seconds%60:02d}/km','deadline':None},
            'training_logic':['多数训练保持能说完整句子的轻松强度（约 RPE 2–3/10），不把目标比赛配速当作日常轻松配速。',
                              '先建立稳定、可恢复的跑步频率；恢复正常并且基础足够后再加入少量质量课，避免连续安排。',
                              '达到目标所需周数取决于当前能力，现有数据不足以承诺最快达标时间。'],
            'morning_recheck':['同步昨晚睡眠和 HRV','确认无伤痛、疾病、异常疲劳','轻松热身后再决定是否继续；不适则降级或停止'],
            'method':'Individualized multi-signal coaching heuristics v1; not medical clearance, a validated risk model, or Garmin Training Readiness.',
            'heuristics':{'hrv_recent_vs_baseline':0.85,'minimum_baseline_days':14,'short_sleep_hours':6,
                          'resting_hr_increase_bpm':7,'single_run_review_ratio':1.1,
                          'note':'工程保守筛查阈值，未被所列文献验证为本人的最佳阈值；不预测受伤概率。'}}
