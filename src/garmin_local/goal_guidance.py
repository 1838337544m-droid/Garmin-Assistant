# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Auditable goal gap, load warnings, and a conditional consolidation microcycle.

No race prediction, fitted VDOT, copied book schedules or automatic goal changes.
The seven-day allocation is an engineering fallback, not a validated optimal plan.
"""
from datetime import date, timedelta
from statistics import median
import math
import re

from .prescription import classify_activity
from .session_targets import pace

CHECKED_ON='2026-11-27'
SOURCES=[
    {'id':'daniels4','title':"Daniels’ Running Formula, 4th ed.",'date':'2022',
     'url':'https://us.humankinetics.com/products/daniels-running-formula-4th-edition',
     'quality':'经典教练理论；本次核对出版社介绍与目录，未核对全书配速表。',
     'application':'区分训练目的、当前能力和目标强度；不冒充已计算个人VDOT。'},
    {'id':'pfitzinger4','title':'Advanced Marathoning, 4th ed.','date':'2026',
     'url':'https://us.humankinetics.com/products/advanced-marathoning-4th-edition',
     'quality':'经典马拉松训练体系；出版社介绍与目录，不是个体随机试验证据。',
     'application':'分阶段准备、负荷与恢复协调；不将书中马拉松课表套给10公里或其他运动。'},
    {'id':'tid2025','title':'Training intensity distribution: individual-participant network meta-analysis','date':'2025-03',
     'url':'https://pubmed.ncbi.nlm.nih.gov/39888556/',
     'quality':'13项研究、348人；已核对PubMed摘要，未复核所有原始试验；女性较少。',
     'application':'训练分布需考虑训练水平；不能宣称极化或金字塔对所有人更优。'},
    {'id':'tid2026','title':'Effects of Different Training-Intensity Distribution Models: Bayesian Network Meta-Analysis','date':'2026-07',
     'url':'https://pubmed.ncbi.nlm.nih.gov/42171506/',
     'quality':'网络荟萃分析；已核对摘要；比较的可信区间跨零，排序不等于确定优效。',
     'application':'不以模型排名自动开出高强度比例；先结合项目、水平与恢复。'},
    {'id':'distance2025','title':'How much running is too much? A 5200-person cohort study','date':'2025-07-07',
     'url':'https://doi.org/10.1136/bjsports-2024-109380',
     'quality':'5205名成人跑者的观察研究，自报损伤；不能证明因果或计算个人受伤概率。',
     'application':'单次距离相对近30天最长跑明显上升时提示复核；110%不是安全界线，也不是每周递增规则。'},
]


def positive(value):
    return type(value) in (int,float) and math.isfinite(value) and value>0


def validate_benchmark(value):
    if value is None or value=={}: return None
    if not isinstance(value,dict) or set(value)-{'date','distance_km','time_minutes','kind'}:
        raise ValueError('Invalid benchmark')
    if value.get('kind') not in {'race','time_trial'}:
        raise ValueError('Benchmark must be a race or time trial')
    d=value.get('date')
    if not isinstance(d,str) or len(d)!=10 or date.fromisoformat(d).isoformat()!=d:
        raise ValueError('Invalid benchmark date')
    if not positive(value.get('distance_km')) or value['distance_km']>200:
        raise ValueError('Invalid benchmark distance')
    if not positive(value.get('time_minutes')) or value['time_minutes']>10000:
        raise ValueError('Invalid benchmark time')
    return value


def _target(profile,defaults,as_of):
    race=defaults.get('race_plan') or {}
    if race.get('enabled') and race.get('sport')=='running' and race.get('date','')>=as_of:
        return race.get('distance_km'),race.get('goal_minutes'),race.get('date'),'当前跑步赛事'
    m=re.search(r'(\d+(?:\.\d+)?)\s*(?:公里|km)\D{0,12}?(\d+(?:\.\d+)?)\s*(?:分钟|min)',profile.get('goal',''),re.I)
    if m and positive(float(m[1])) and positive(float(m[2])):
        return float(m[1]),float(m[2]),profile.get('goal_date'),'长期目标'
    return None,None,profile.get('goal_date'),'长期目标尚未结构化'


def _history(activities,as_of):
    end=date.fromisoformat(as_of); rows=[]; seen=set()
    for a in activities:
        if classify_activity(a)!='running': continue
        try:d=date.fromisoformat(str(a.get('startTimeLocal',''))[:10])
        except ValueError:continue
        key=str(a.get('activityId') or a.get('startTimeLocal'))
        if key in seen or not end-timedelta(days=27)<=d<=end:continue
        seen.add(key)
        if positive(a.get('duration')) and positive(a.get('distance')):
            rows.append((d,a['duration']/60,a['distance']/1000))
    weeks=[sum(m for d,m,_ in rows if end-timedelta(days=7*i+6)<=d<=end-timedelta(days=7*i)) for i in range(4)]
    return rows,weeks


def build_goal_guidance(profile,sport,defaults,safety,activities):
    original=profile.get('goal','未填写')
    result={'original_goal':original,'gap':None,'load_status':'unknown','original_plan':'未填写原计划距离。',
            'benchmark_note':'尚无近期比赛或测试成绩，日常活动均速不能替代能力测试。',
            'alternative_goal':'先确认当前专项能力与可恢复负荷，再修改成绩目标；不会自动改写已保存目标。',
            'priorities':[],'week_plan':[],
            'sources':[{**s,'checked_on':CHECKED_ON} for s in SOURCES],
            'evidence_scope':'定向核对截至2026-11-27的经典资料及2025–2026相关期刊，不是穷尽检索；新候选论文不会自动改写训练规则。',
            'method':'7日安排为低强度巩固模板：不增加近期总时长、频率或最长距离；不是经典书籍原课表，也不承诺按期达标。'}
    if sport!='running' or profile.get('primary_sport')!='running':
        result['alternative_goal']='本次非长期跑步专项，不换算跑步负荷或套用长跑课表；保留本项目执行指标，需依据该项目的能力测试另行评估目标。'
        result['priorities']=[{'title':'1. 原目标与当前专项边界','items':[('目标',original),('分析',result['alternative_goal'])]},
                              {'title':'2. 更合理的训练与目标建议','items':[('调整',result['alternative_goal'])]}]
        return result
    as_of=safety['as_of']; start=date.fromisoformat(safety['target_date'])
    distance,minutes,deadline,origin=_target(profile,defaults,as_of)
    rows,weeks=_history(activities,as_of)
    weekly_minutes=round(median(weeks),1)
    recent_minutes=round(weeks[0],1)
    frequency=min(4,len({d for d,_,_ in rows})//4,
                  len({d for d,_,_ in rows if d>=date.fromisoformat(as_of)-timedelta(days=6)}))
    longest=safety.get('metrics',{}).get('longest_run_30d_km')
    codes={f.get('code') for f in safety.get('flags',[])}
    planned=safety.get('distance_comparison',{}).get('planned_km')
    overload='single_run_jump' in codes or (positive(planned) and positive(longest) and planned>longest*1.1)
    result['load_status']='overload_warning' if overload else 'review_recovery' if codes else 'no_detected_spike'
    if positive(planned):
        result['original_plan']=f'原计划单次 {planned:g} 公里；'+('超负荷警示（距离激增，待复核，不建议照原距离执行）。' if overload else '尚未检出既定距离激增信号，不等于安全放行。')
    if overload:
        result['original_plan']+=f' 近30天已记录最长跑 {longest:g} 公里。' if positive(longest) else ' 缺少可比较的完整最长跑数据。'
    target=f'{distance:g} 公里 / {minutes:g} 分钟，理论配速 {pace(minutes*60/distance)}/km' if positive(distance) and positive(minutes) else '需要明确目标距离和总分钟数，才能计算差距。'
    first=[('原目标',original),('本次分析目标',origin+'：'+target),('原计划与负荷',result['original_plan']),
           ('近期训练',f'已记录28天 {len(rows)} 次；4个7日时长中位数 {weekly_minutes:g} 分钟，最近7日 {recent_minutes:g} 分钟。未记录的训练不算作零负荷事实。')]
    benchmark=validate_benchmark(defaults.get('running_benchmark'))
    if benchmark:
        age=(date.fromisoformat(as_of)-date.fromisoformat(benchmark['date'])).days
        result['benchmark_note']=f'{benchmark["date"]} · {benchmark["distance_km"]:g} 公里 / {benchmark["time_minutes"]:g} 分钟（用户明确记录的比赛/测试）'
        if age<0:result['benchmark_note']+='；日期晚于分析日，不用于当前能力估计。'
        elif age>42:result['benchmark_note']+='；已过期（产品参考窗口42天，非文献验证阈值），需更新测试后再定成绩目标。'
        elif positive(distance) and abs(benchmark['distance_km']-distance)>0.001:
            result['benchmark_note']+='；不同距离，不外推为已经具备目标距离能力。'
            result['alternative_goal']=f'先把阶段验收设为复核已测试的 {benchmark["distance_km"]:g} 公里 / {benchmark["time_minutes"]:g} 分钟成绩及恢复耐受；原目标作为后续候选。恢复与基础稳定后再评估目标距离，不凭短距离成绩承诺长距离完赛时间。'
        elif positive(distance) and positive(minutes):
            current=benchmark['time_minutes']; gap=current-minutes
            result['gap']={'minutes':round(gap,2),'seconds_per_km':round(gap*60/distance,1),
                           'time_reduction_percent':round(gap/current*100,1)}
            first.append(('量化差距',f'相对该同距离成绩，目标需缩短 {gap:g} 分钟，平均每公里快 {gap*60/distance:g} 秒，耗时减少 {gap/current*100:.1f}%。这只是成绩差，不预测所需周数。' if gap>0 else '已有同距离成绩达到该目标，但仍需核对赛道、天气、恢复与测试可比性。'))
            result['alternative_goal']=f'先以同距离近期 {current:g} 分钟成绩作为复核参考，目标配速参考 {pace(current*60/distance)}/km；原目标保留为进阶目标。若赛道、爬升、热环境或恢复不同，不把该成绩当作保证。' if gap>0 else '保留原目标，先验证可重复性与比赛条件；不要只因一次成绩达标自动提高训练强度。'
    first.append(('当前能力依据',result['benchmark_note']))
    first.append(('当前恢复判断',safety.get('recommendation') or {
        'avoid_running':'停止跑步并先评估伤痛或疾病。','recovery':'优先恢复，暂缓跑步训练。',
        'insufficient_data':'资料不足，先补齐再评估。','easy_only':'当前仅支持低强度方向，需明早复评。',
        'easy_if_well':'当前未见既定恢复警示，但每次执行前仍需复评。'}.get(safety.get('decision'),'需要复核。')))
    if positive(distance) and positive(longest) and distance>longest:
        first.append(('距离耐受差距',f'目标 {distance:g} 公里超过近30天已记录最长跑 {longest:g} 公里；这不是要求每次或赛前必须跑完比赛距离，需结合项目和准备周期复核。'))
    if deadline:
        remaining=(date.fromisoformat(deadline)-date.fromisoformat(as_of)).days
        first.append(('剩余时间',f'{remaining} 天；'+('赛事临近，优先复核既有减量安排，不靠临时补长跑或强度课补差距。' if 0<=remaining<=7 else '不能仅凭成绩差反推出保证达标的训练周数。')))
    first.extend([('需要补齐的能力与条件','先稳定可恢复的有氧训练与专项耐受，再依据近期能力测试安排阈值/专项速度，最后结合赛事进入减量与恢复。缺少阈值或已验证强度区间时，不从目标配速倒推高强度课。'),
                  ('达标条件','确认近期测试可比、训练连续性、症状与恢复趋势，以及可用训练时间；7日后复核执行耐受和缺项，不能把HRV正常等同于比赛目标已达标。')])
    settings=defaults.get('sport_targets',{}).get('running',{})
    blocked=safety.get('decision') in {'avoid_running','recovery','insufficient_data'} or bool(safety.get('missing'))
    blocked=blocked or not safety.get('sync',{}).get('fresh') or safety.get('sync',{}).get('status')!='ok'
    dose=safety.get('suggested_easy_minutes')
    can_plan=not blocked and frequency>0 and recent_minutes>0 and positive(dose) and bool(rows)
    per_run=0
    if can_plan:
        per_run=math.floor(min(dose,settings.get('minutes',dose),median(m for _,m,_ in rows)*0.8,
                               min(recent_minutes,weekly_minutes)/frequency))
        if positive(longest) and 'pace_fast' in settings:
            per_run=min(per_run,math.floor(longest*settings['pace_fast']/60))
    days={1:[0],2:[0,3],3:[0,2,5],4:[0,2,4,6]}.get(frequency,[])
    race=defaults.get('race_plan') or {}
    race_date=race.get('date') if race.get('enabled') and race.get('sport')=='running' and race.get('date','')>=as_of else None
    for i in range(7):
        day=(start+timedelta(days=i)).isoformat()
        item={'date':day,'kind':'review','minutes':0,'action':'休息或舒适日常活动；复核疼痛、疲劳与睡眠，不补课。'}
        if blocked:item['action']='恢复/补齐资料并重新评估；当前不安排跑步剂量。'
        elif race_date and day>=race_date:item['action']='比赛日或赛后专项复评；不把常规轻松跑替代比赛方案，也不预先安排赛后跑量。'
        elif i in days and per_run>=1:
            item.update(kind='easy',minutes=per_run,action=f'轻松跑 {per_run} 分钟，RPE 2–3/10，保持完整交谈；当天同步与症状复评后才执行。')
            if 'pace_fast' in settings:
                item.update(distance_low_km=round(per_run*60/settings['pace_slow'],1),distance_high_km=round(per_run*60/settings['pace_fast'],1))
                item['action']+=f' 约 {item["distance_low_km"]:.1f}–{item["distance_high_km"]:.1f} 公里，{pace(settings["pace_fast"])}–{pace(settings["pace_slow"])}/km（个人轻松区间；到时即停）。'
            else:item['action']+=' 缺个人轻松配速，暂不给出公里数。'
            item['action']+=f' 个人心率区间 {settings["hr_low"]:g}–{settings["hr_high"]:g} bpm。' if 'hr_low' in settings else ' 缺个人心率区间，不用目标心率代替。'
        elif not can_plan:item['action']='缺少连续训练基线或最近7日训练，先确认停训原因与可恢复频率，不自动复制一周跑量。'
        result['week_plan'].append(item)
    first.append(('近期训练安排','下列7日为优先级1的巩固/降负荷起步安排；原计划触发超负荷警示时，保留原案用于比较，执行按下调后的剂量复评，不通过增加强度强行追目标。'))
    if result['gap'] is None and result['alternative_goal'].startswith('先确认') and per_run>0:
        result['alternative_goal']=f'先以未来7日内、恢复复评允许时完成最多 {sum(x["kind"]=="easy" for x in result["week_plan"])} 次、每次 {per_run} 分钟轻松跑作为过程目标；取得有效同距离测试后再讨论成绩目标或延后目标日期，不预设必达时间。'
    second=[('更合理的目标',result['alternative_goal']),('训练调整',
        '先按下列低强度安排巩固；没有增加近期周时长、频率或最长距离。后续进阶须根据执行耐受与新测试单独复核，不自动每周加10%。'),
        ('复核与进阶标准','每次训练无新增或加重的疼痛，次日恢复可接受；同步与症状资料完整。7日后复核能否稳定完成，再讨论增加一种刺激，而非同时加频率、距离和强度。'),
        ('目标修改方式','建议只作为候选，不自动覆盖已保存的目标；由用户确认是否采纳。')]
    result['priorities']=[{'title':'1. 以当前状态追原目标：差距、条件与训练安排','items':first},
                          {'title':'2. 更合理的训练意见与目标修改建议','items':second}]
    return result
