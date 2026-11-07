"""Sync, literature retrieval and a saved next-day running recommendation."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .history import HistoryStore
from .readiness import assess
from .research import REVIEWED, CLASSIC_MODELS, atomic_json, update_research
from .sync import SyncManager, local_today
from .menu import core_menu
from .monitoring import recovery_status, render_monitoring_report, tomorrow_plan, training_status
from .goals import validate_goal
from zoneinfo import ZoneInfo


class TrainingWorkflow:
    def __init__(self, service, folder, report_folder=None, settings=None):
        self.service, self.folder = service, folder.resolve()
        self.report_folder = report_folder.resolve() if report_folder else self.folder/'reports'
        self.store = HistoryStore(self.folder/'history.sqlite3')
        self.settings=settings

    def sync(self, days=93, full=False):
        result=SyncManager(self.service,self.store).run(days=days,full=full,current_date=self._today())
        if self.settings:
            from .menu import MenuStore
            result['function_menu']=MenuStore(self.folder/'menu-preferences.json').view()['function_menu']
        result['restore_command']='显示原有功能菜单'
        return result

    def _today(self):
        return datetime.now(ZoneInfo(self.settings.timezone)).date().isoformat() if self.settings else local_today()

    def _monitoring_inputs(self):
        today = self._today()
        sync = self.sync()
        start = (date.fromisoformat(today) - timedelta(days=92)).isoformat()
        history = self.store.load(start, today)
        language = (self.settings.language if self.settings else None) or 'zh'
        return today, {**sync, 'fresh': sync['status'] == 'ok'}, history, language

    def _save_monitoring_report(self, result, sync, language, prefix):
        from .menu import MenuStore

        result.update({'sync': sync, 'language': language, 'source': 'Garmin Personal API',
                       'function_menu': MenuStore(self.folder / 'menu-preferences.json').view()['function_menu']})
        self.report_folder.mkdir(parents=True, exist_ok=True)
        stem = f"{prefix}_{result.get('target_date', result['as_of'])}"
        markdown_path = self.report_folder / f'{stem}.md'
        if language == 'en':
            from .onboarding import localize_result
            result = localize_result(result, language)
        markdown_path.write_text(render_monitoring_report(result), encoding='utf-8')
        # Resolve the written file so other apps can open it outside Store Python.
        markdown_path = markdown_path.resolve(strict=True)
        json_path = markdown_path.with_suffix('.json')
        result.update({'report_json': str(json_path), 'report_markdown': str(markdown_path)})
        atomic_json(json_path, result)
        return result

    def training_status(self):
        today, sync, history, language = self._monitoring_inputs()
        return self._save_monitoring_report(training_status(history, today, language), sync, language, 'training_status')

    def recovery_status(self, subjective=None):
        today, sync, history, language = self._monitoring_inputs()
        result = recovery_status(history, today, subjective, sync['fresh'], language)
        result['research'] = update_research(self.folder, today)
        return self._save_monitoring_report(result, sync, language, 'recovery_status')

    def plan_tomorrow(self, sport, distance_km, minutes, subjective=None):
        validate_goal(sport, distance_km, minutes)
        today, sync, history, language = self._monitoring_inputs()
        result = tomorrow_plan(history, today, sport, distance_km, minutes, subjective, sync['fresh'], language)
        result['research'] = update_research(self.folder, today)
        return self._save_monitoring_report(result, sync, language, f'tomorrow_{sport}')

    def tomorrow(self, as_of=None, subjective=None, planned_km=None, sync_first=True, research_refresh=True, force_research=False):
        operation_today=self._today()
        as_of=as_of or operation_today
        if date.fromisoformat(as_of).isoformat()!=as_of or as_of>operation_today:
            raise ValueError('as_of must be a valid nonfuture YYYY-MM-DD')
        if sync_first:
            if as_of!=operation_today:raise ValueError('Historical analysis must use sync_first=False')
            synced=self.sync()
            synced={**synced,'fresh':synced['status']=='ok'}
        else:
            synced={**(self.store.latest() or {}),'fresh':False,'analysis_sync_skipped':True}
        start=(date.fromisoformat(as_of)-timedelta(days=92)).isoformat()
        history=self.store.load(start,as_of)
        # Optional offline path never checks PubMed.
        evidence=(update_research(self.folder,as_of,force=force_research) if research_refresh else
                  {'status':'reviewed_only','rules_reviewed_on':'2026-10-28','reviewed_sources':REVIEWED,
                   'checked_on':None,'candidates':[],'error':'Research discovery skipped'})
        result=assess(history,as_of,subjective=subjective,planned_km=planned_km,sync_ok=synced['fresh'],
                      goal=self.settings.goal if self.settings and self.settings.goal_sport == 'running' else None)
        result.update({'source':'Garmin official Personal API','sync':synced,'research':evidence,
                       'classic_models':CLASSIC_MODELS,'function_menu':core_menu(),
                       'generated_at':datetime.now(timezone.utc).isoformat()})
        if self.settings:
            from .menu import MenuStore
            result['function_menu']=MenuStore(self.folder/'menu-preferences.json').view()['function_menu']
        result['timezone']=self.settings.timezone if self.settings else 'UTC'
        result['language']=self.settings.language if self.settings else 'zh'
        result['model_application']=[
            {'model_id':'fitness_fatigue','interpretation':f"近期负荷：7 日跑量 {result['metrics']['running_km_7d']} 公里；结合 HRV、睡眠和静息心率，当前判断为 {result['decision']}。这是定性判断，并非拟合出的适能/疲劳分数。"},
            {'model_id':'intensity_distribution','interpretation':'当前恢复筛查只支持决定是否降级训练；未根据心率区间完整计算个人极化/金字塔比例，不声称已完成该模型的定量评估。'},
            {'model_id':'daniels','interpretation':f"目前优先使用谈话强度选择轻松跑；阈值/间歇配速需近期能力测试与恢复信息，目标比赛均速（{result['goal']['race_pace']}）不直接作为训练配速。"},
        ]
        if result['language']=='en':
            from .onboarding import localize_result
            result=localize_result(result,'en')
        folder=self.report_folder;folder.mkdir(parents=True,exist_ok=True)
        json_path=folder/f"readiness_{result['target_date']}.json"
        markdown_path=json_path.with_suffix('.md')
        result.update({'report_json':str(json_path),'report_markdown':str(markdown_path)})
        atomic_json(json_path,result)
        markdown_path.write_text(render_report(result),encoding='utf-8')
        return result


def render_report(r):
    if r.get('language')=='en':return render_english_report(r)
    labels={'avoid_running':'暂不跑步','insufficient_data':'信息不足，暂不安排强度课',
            'recovery':'优先恢复','easy_only':'只考虑轻松训练','easy_if_well':'无不适时可考虑轻松跑'}
    lines=[f"# {r['target_date']} 跑步建议",'',f"数据来源：Garmin；分析日期：{r['as_of']}（{r.get('timezone','UTC')}）。",
           '', f"目标：{r['goal']['distance_km']:g} 公里，{r['goal']['target']}；比赛均速 {r['goal']['race_pace']}。",
           '',f"**结论：{labels[r['decision']]}。**",'',r['recommendation'],
           '', '这是明日预建议。今晚的睡眠和明天身体状态尚未知，明早同步后需要复评。',
           '', '## 判断线索','']
    lines.extend([f"- {f['reason']}（依据：{f['evidence_id']}）" for f in r['flags']] or ['- 暂未发现已设定的恢复不足线索；这不等于医学放行。'])
    lines+=['','## 个人数据','', '| 指标 | 数值 |','|---|---|']
    metric_labels={'hrv_baseline':'个人 HRV 基线（Garmin 原始值）','hrv_baseline_days':'HRV 基线有效天数',
                   'hrv_recent_mean':'最近 2–3 晚 HRV 平均值','latest_sleep_hours':'最新睡眠（小时）',
                   'sleep_baseline_hours':'个人睡眠中位数（小时）','resting_hr_baseline':'个人静息心率基线（次/分）',
                   'last_complete_day_resting_hr':'上一完整日静息心率（次/分）','longest_run_30d_km':'近 30 天最长单次跑步（公里）',
                   'runs_28d':'近 28 天跑步次数','running_km_7d':'最近 7 个日历日跑量（公里，今天未结束）',
                   'hard_or_long_sessions_last_2_calendar_days':'今天/昨天较强或较长跑步次数'}
    lines.extend(f"| {metric_labels.get(k,k)} | {v if v is not None else '缺失'} |" for k,v in r['metrics'].items())
    lines+=['','## 数据限制','',f"- 本次同步：{r['sync'].get('status','未同步')}；本次数据确认更新：{r['sync']['fresh']}。",
            '- 今天日汇总未结束；静息心率使用上一完整日。',
            f"- 缺项：{', '.join(r['missing']) or '无'}。",'- subjective_check 表示尚未确认疼痛、疾病、疲劳、步行痛、局部骨痛、胸痛及晕厥情况。',
            '- 程序的 HRV、睡眠及心率筛查阈值未经个体验证；不表示伤病概率、诊断或 Garmin 训练准备度。',
            '', '## 向个人跑步目标推进','']
    lines.extend('- '+s for s in r['training_logic'])
    lines+=['','## 经典训练模型与本次应用','']
    applications={a['model_id']:a['interpretation'] for a in r.get('model_application',[])}
    for model in r.get('classic_models',[]):
        lines += [f"- [{model['name']}]({model['url']})（{model['year']}）：{model['application']}",
                  f"  本次：{applications.get(model['id'],'见训练建议。')}"]
    lines+=['','## 明早复评','']+['- '+s for s in r['morning_recheck']]
    lines+=['','## 已核验依据','',f"规则文献核验日期：{r['research'].get('rules_reviewed_on')}。"]
    lines+=['']+[f"- [{s['title']}]({s['url']})（{s['year']}；{s['type']}）：{s['application']}" for s in r['research']['reviewed_sources']]
    lines+=['','## 联网文献更新','',f"状态：{r['research']['status']}；上次成功检索日期：{r['research'].get('checked_on') or '无'}。",
            '新检索论文属于候选资料，未完成质量评估，不会自动改写训练规则；检索范围不是全部文献。','']
    lines += [f"- [{s.get('title','论文')}]({s.get('url','https://pubmed.ncbi.nlm.nih.gov/')})（{s.get('publication_date','日期未知')}；待评估）" for s in r['research'].get('candidates',[])]
    interval=r['sync'].get('interval',{})
    lines+=['','## 间隔数据补齐','',f"上次完整同步截至：{interval.get('previous_sync_end') or '首次同步/未知'}；本次需补齐：{interval.get('gap_start') or '无新增日历日'} 至 {interval.get('gap_end') or '—'}。",
            f"间隔同步完成：{interval.get('gap_fetch_completed',False)}；新增运动记录：{interval.get('new_activity_records','未知')}。",
            '', '## 功能菜单','']
    lines += [f"{item.get('id',i)}. **{item['command']}**：{item['description']}" for i,item in enumerate(r.get('function_menu',[]),1)]
    lines+=['','如需恢复全部核心菜单，输入：**显示原有功能菜单**。']
    return '\n'.join(lines)+'\n'


def render_english_report(r):
    lines=[f"# Running advice for {r['target_date']}",'',
        f"Source: Garmin. Assessment date: {r['as_of']} ({r.get('timezone','UTC')}).",'',
        f"Goal: {r['goal']['distance_km']:g} km, {r['goal']['target']}. Target race pace: {r['goal']['race_pace']}.",'',
        f"**Decision: {r['decision']}**",'',r['recommendation'],'',
        "This is provisional advice. Tonight's sleep and tomorrow's symptoms are not yet known. Recheck in the morning.",'',
        '## Recovery cues','']
    lines += [f"- {f['reason']} (source: {f['evidence_id']})" for f in r['flags']] or ['- No configured recovery flag was detected; this is not medical clearance.']
    lines += ['','## Personal data','','| Metric | Value |','|---|---|']
    lines += [f"| {k} | {v if v is not None else 'Missing'} |" for k,v in r['metrics'].items()]
    lines += ['','## Limitations','',f"- Fresh complete sync: {r['sync'].get('fresh',False)}.",
        f"- Missing information: {', '.join(r['missing']) or 'None'}.",
        '- subjective_check means pain, illness, fatigue and other symptom checks have not been confirmed.',
        '- Today is incomplete. Resting heart rate uses the last complete day.',
        '- These screening thresholds are coaching heuristics, not validated personal injury probabilities or Garmin Training Readiness.',
        '', '## Training logic','']+['- '+s for s in r['training_logic']]
    lines += ['','## Classic frameworks','',
        '- Fitness–fatigue: interpret training stress alongside recovery; no personal model parameters or race-time predictions have been fitted.',
        '- Intensity distribution: keep most training recoverable; a full personal polarized/pyramidal time-in-zone calculation has not been performed.',
        '- Daniels: distinguish easy, threshold and interval purposes; do not derive current training pace or VDOT from a target race result.','']
    lines += [f"- [{m['title']}]({m['url']}) ({m['year']})" for m in r.get('classic_models',[])]
    lines += ['','## Reviewed references','']+[f"- [{s['title']}]({s['url']}) ({s['year']}; {s['type']})" for s in r['research']['reviewed_sources']]
    lines += ['','## Recent research discovery','',f"Status: {r['research']['status']}. Last successful search: {r['research'].get('checked_on') or 'None'}.",
        'Newly retrieved papers require appraisal and do not automatically change training rules. This is not an exhaustive review.','']
    lines += [f"- [{s.get('title','Paper')}]({s.get('url','https://pubmed.ncbi.nlm.nih.gov/')}) ({s.get('publication_date','Unknown date')}; not appraised)" for s in r['research'].get('candidates',[])]
    lines += ['','## Morning recheck','']+['- '+s for s in r['morning_recheck']]
    interval=r['sync'].get('interval',{})
    lines += ['','## Interval synchronization','',f"Gap: {interval.get('gap_start')} to {interval.get('gap_end')}; completed: {interval.get('gap_fetch_completed',False)}.",
        '', '## Function menu','']
    lines += [f"{item['id']}. **{item['command']}**: {item['description']}" for item in r.get('function_menu',[])]
    lines += ['','To restore core items 1–7, say: **Show original function menu / 显示原有功能菜单**.']
    return '\n'.join(lines)+'\n'
