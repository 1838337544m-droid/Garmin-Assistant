# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Sync, literature retrieval and a saved next-day running recommendation."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .history import HistoryStore
from .readiness import assess
from .research import REVIEWED, CLASSIC_MODELS, atomic_json, update_research
from .sync import SyncManager, local_today
from .menu import FUNCTION_MENU
from .athlete_profile import load_profile
from .prescription import build_prescription, classify_activity, SESSION_SPORTS
from uuid import uuid4
from .report_ui import render_dashboard
from .distance_context import distance_context


class TrainingWorkflow:
    def __init__(self, service, folder, report_folder=None):
        self.service, self.folder = service, folder.resolve()
        self.report_folder = report_folder.resolve() if report_folder else self.folder/'reports'
        self.store = HistoryStore(self.folder/'history.sqlite3')

    def sync(self, days=93, full=False):
        return SyncManager(self.service,self.store).run(days=days,full=full)

    def assess_session(self, session_sport=None, session_intent=None, subjective=None,
                       swimming_safety=None, **kwargs):
        profile=load_profile(self.folder)
        if not profile:
            raise ValueError('Set a primary sport profile before requesting a multisport prescription.')
        sport=session_sport or profile['primary_sport']
        if sport not in SESSION_SPORTS or session_intent not in {None,'recovery','base','quality','skills'}:
            raise ValueError('Unsupported sport or intent')
        result=self.tomorrow(subjective=subjective, _save=False, _sport=sport, **kwargs)
        history=self.store.load((date.fromisoformat(result['as_of'])-timedelta(days=92)).isoformat(),result['as_of'])
        result.update({'primary_sport':profile['primary_sport'],'session_sport':sport,
                       'prescription':build_prescription(profile,sport,result,history.get('activities',[]),
                                                         session_intent,swimming_safety)})
        result.update(schema_version=1,session_intent=session_intent,
                      profile_effective_at=profile['profile_effective_at'],goal=profile['goal'])
        for key in ('model_application','classic_models','training_logic','suggested_easy_minutes'):
            result.pop(key,None)
        result['recommendation']=result['prescription']['session_action']
        result['decision']=result['prescription']['prescription_status']
        result['quality_session_eligible']=result['decision']=='quality_candidate'
        path=self.report_folder/f"session_{result['target_date']}_{sport}_{uuid4().hex}.json"
        path.parent.mkdir(parents=True,exist_ok=True)
        result.update(report_json=str(path),report_markdown=str(path.with_suffix('.md')))
        result['report_html']=str(path.with_suffix('.html'))
        atomic_json(path,result)
        path.with_suffix('.md').write_text(render_session_report(result),encoding='utf-8')
        path.with_suffix('.html').write_text(render_dashboard(result),encoding='utf-8')
        return result

    def tomorrow(self, as_of=None, subjective=None, planned_km=None, sync_first=True, research_refresh=True, force_research=False, _save=True, _sport=None, progress=None):
        as_of=as_of or local_today()
        if date.fromisoformat(as_of).isoformat()!=as_of or as_of>local_today():
            raise ValueError('as_of must be a valid nonfuture YYYY-MM-DD')
        if sync_first:
            if as_of!=local_today():raise ValueError('Historical analysis must use sync_first=False')
            if progress: progress('syncing')
            synced=self.sync()
            synced={**synced,'fresh':synced['status']=='ok'}
        else:
            synced={**(self.store.latest() or {}),'fresh':False,'analysis_sync_skipped':True}
        start=(date.fromisoformat(as_of)-timedelta(days=92)).isoformat()
        history=self.store.load(start,as_of)
        if _sport and _sport!='running':
            history={**history,'activities':[]}
        # Optional offline path never checks PubMed.
        if progress: progress('research')
        evidence=(update_research(self.folder,as_of,force=force_research) if research_refresh else
                  {'status':'reviewed_only','rules_reviewed_on':'2026-10-28','reviewed_sources':REVIEWED,
                   'checked_on':None,'candidates':[],'error':'Research discovery skipped'})
        if progress: progress('analyzing')
        result=assess(history,as_of,subjective=subjective,planned_km=planned_km,sync_ok=synced['fresh'])
        if _sport in (None,'running'):
            result['distance_comparison']=distance_context(planned_km,result['metrics']['longest_run_30d_km'],as_of,synced['fresh'])
        result.update({'source':'Garmin official Personal API','sync':synced,'research':evidence,
                       'classic_models':CLASSIC_MODELS,'function_menu':FUNCTION_MENU,
                       'generated_at':datetime.now(timezone.utc).isoformat()})
        result['model_application']=[
            {'model_id':'fitness_fatigue','interpretation':f"近期负荷：7 日跑量 {result['metrics']['running_km_7d']} 公里；结合 HRV、睡眠和静息心率，当前判断为 {result['decision']}。这是定性判断，并非拟合出的适能/疲劳分数。"},
            {'model_id':'intensity_distribution','interpretation':'当前恢复筛查只支持决定是否降级训练；未根据心率区间完整计算个人极化/金字塔比例，不声称已完成该模型的定量评估。'},
            {'model_id':'daniels','interpretation':'目前优先使用谈话强度选择轻松跑；阈值/间歇配速需近期能力测试与恢复信息，目标 6:00/km 不直接作为训练配速。'},
        ]
        if not _save:
            if _sport!='running':
                result['metrics']={k:v for k,v in result['metrics'].items() if k not in
                    {'longest_run_30d_km','runs_28d','running_km_7d','hard_or_long_sessions_last_2_calendar_days'}}
            return result
        folder=self.report_folder;folder.mkdir(parents=True,exist_ok=True)
        json_path=folder/f"readiness_{result['target_date']}.json"
        markdown_path=json_path.with_suffix('.md')
        result.update({'report_json':str(json_path),'report_markdown':str(markdown_path)})
        atomic_json(json_path,result)
        markdown_path.write_text(render_report(result),encoding='utf-8')
        markdown_path.with_suffix('.html').write_text(render_dashboard(result),encoding='utf-8')
        return result


def render_session_report(r):
    p=r['prescription']
    lines=[f"# {r['target_date']} 明日训练处方",'',f"长期主项：{r['primary_sport']} · 本次项目：{r['session_sport']}",
           f"目标：{r['goal']}",'',p['session_action'],p['dose'],
           r.get('distance_comparison',{}).get('display_zh',''),'','## 能力处方总结',
           p['capacity_summary'],p['capacity_focus'],'','## 处方依据',
           *[f"- {f['reason']}" for f in r['flags']],
           f"数据来源：Garmin；分析日期：{r['as_of']}（Asia/Dubai）；同步状态：{r['sync'].get('status','未知')}。",
           '','## 未知与安全边界',f"缺项：{', '.join(r['missing']) or '无已知缺项'}",p['evidence_boundary'],
           p['downgrade_rule'],'明早重新同步并确认症状后再执行；本建议不构成医疗放行。',
           '','## 项目记录',f"近期同项目记录：{p.get('same_sport_sessions',0)} 次（仅已识别记录）。",'',
           '## 研究与模型',f"检索状态：{r['research']['status']}；上次成功检索：{r['research'].get('checked_on') or '无'}。",
           '现有检索主要覆盖跑步与恢复；骑车、游泳、攀岩专项剂量尚未核验，因此仅提供保守活动方向，不推断专项能力。',
           f"规则来源核验日期：{r['research'].get('rules_reviewed_on')}；候选论文不自动成为规则。"]
    lines.extend(f"- [{s['title']}]({s['url']})（{s['year']}，仅作为恢复背景）" for s in r['research']['reviewed_sources'])
    return '\n\n'.join(lines)+'\n'


def build_prompt_explanation(result):
    basis=[flag['reason'] for flag in result.get('flags',[])]
    return {
        'basis':'；'.join(basis) if basis else '未发现已设定的恢复不足线索。',
        'uncertainty':'、'.join(result.get('missing',[])) or '无已知缺项。',
        'next_action':(result.get('morning_recheck') or ['明早同步后复评。'])[0],
    }


def render_report(r):
    labels={'avoid_running':'暂不跑步','insufficient_data':'信息不足，暂不安排强度课',
            'recovery':'优先恢复','easy_only':'只考虑轻松训练','easy_if_well':'无不适时可考虑轻松跑'}
    lines=[f"# {r['target_date']} 跑步建议",'',f"数据来源：Garmin；分析日期：{r['as_of']}（Asia/Dubai）。",
           '', '目标：10 公里跑进 60 分钟；比赛均速需略快于 6:00/km。',
           '',f"**结论：{labels[r['decision']]}。**",'',r['recommendation'],
           '',r.get('distance_comparison',{}).get('display_zh',''),
           '', '这是明日预建议。今晚的睡眠和明天身体状态尚未知，明早同步后需要复评。',
           '', '## 判断线索','']
    lines.extend([f"- {f['reason']}（依据：{f['evidence_id']}）" for f in r['flags']] or ['- 暂未发现已设定的恢复不足线索；这不等于医学放行。'])
    explanation=build_prompt_explanation(r)
    lines+=['','## 提示解释与边界','',f"- 本次依据：{explanation['basis']}",
            f"- 未知或不确定：{explanation['uncertainty']}",
            '- 本结论不等于医疗放行、伤病预测或最佳表现保证。局部疼痛、步行痛或其他症状不能被正常的可穿戴指标覆盖。',
            '- 恢复手段不能证明已准备好进行高强度训练，也不能替代负荷调整、症状观察和复评。',
            f"- 下一步：{explanation['next_action']}"]
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
            '', '## 向 10 公里 60 分钟推进','']
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
    lines += [f"{i}. **{item['command']}**：{item['description']}" for i,item in enumerate(r.get('function_menu',[]),1)]
    return '\n'.join(lines)+'\n'
