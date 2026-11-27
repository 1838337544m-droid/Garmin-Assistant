# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Sport-specific quantities from explicitly saved personal easy-training settings.

These are arithmetic planning aids, not newly inferred physiological zones.
Pace inputs are seconds per km (running) or per 100 m (swimming).
"""
import math
import re
from datetime import date

SPORTS = {'running', 'cycling', 'swimming', 'climbing'}
LIMITS = {'minutes': (1, 240), 'distance': (1, 10000), 'hr_low': (30, 230),
          'hr_high': (30, 230), 'pace_fast': (30, 1800), 'pace_slow': (30, 1800),
          'watts_low': (1, 1000), 'watts_high': (1, 1000),
          'speed_low': (1, 80), 'speed_high': (1, 80), 'reps': (1, 100), 'rest': (0, 1800)}
FIELDS = {'running': {'minutes','hr_low','hr_high','pace_fast','pace_slow'},
          'cycling': {'minutes','hr_low','hr_high','watts_low','watts_high','speed_low','speed_high'},
          'swimming': {'distance','reps','rest','pace_fast','pace_slow'},
          'climbing': {'minutes','grade','reps','rest'}}


def validate_targets(value):
    if not isinstance(value, dict) or set(value)-SPORTS:
        raise ValueError('Unsupported sport settings')
    for sport, settings in value.items():
        if not isinstance(settings, dict) or set(settings)-FIELDS[sport]:
            raise ValueError('Invalid sport settings')
        for k, v in settings.items():
            if k == 'grade':
                if not isinstance(v, str) or not v.strip() or len(v)>80:
                    raise ValueError('Invalid grade')
            elif (type(v) not in (int, float) or not math.isfinite(v) or
                  not LIMITS[k][0]<=v<=LIMITS[k][1] or (k=='reps' and v!=int(v))):
                raise ValueError('Invalid training number')
        for low, high in [('hr_low','hr_high'),('pace_fast','pace_slow'),
                          ('watts_low','watts_high'),('speed_low','speed_high')]:
            if (low in settings) != (high in settings):
                raise ValueError('Enter both ends of the range')
            if low in settings and settings[low]>settings[high]:
                raise ValueError('Range is reversed')
    return value


def pace(seconds):
    seconds = round(seconds)
    return f'{seconds//60}:{seconds%60:02d}'


def validate_race(plan):
    if plan is None: return None
    if not isinstance(plan,dict) or type(plan.get('enabled')) is not bool:
        raise ValueError('Invalid race plan')
    if set(plan)-{'enabled','name','sport','date','distance_km','goal_minutes','elevation_m','priority','notes'}:
        raise ValueError('Invalid race field')
    if not plan['enabled']: return {'enabled':False}
    if plan.get('sport') not in SPORTS or not isinstance(plan.get('date'),str):
        raise ValueError('Set race sport and date')
    date.fromisoformat(plan['date'])
    if len(plan['date'])!=10: raise ValueError('Use YYYY-MM-DD')
    for key,limit in [('name',100),('notes',500)]:
        if not isinstance(plan.get(key,''),str) or len(plan.get(key,''))>limit:
            raise ValueError('Invalid race description')
    if plan.get('priority','B') not in {'A','B','C'}: raise ValueError('Invalid priority')
    for key,limit in [('distance_km',2000),('goal_minutes',100000),('elevation_m',30000)]:
        if key in plan and (type(plan[key]) not in (int,float) or not math.isfinite(plan[key]) or
                            not (0 if key=='elevation_m' else 0.001)<=plan[key]<=limit):
            raise ValueError('Invalid race number')
    return plan


def race_context(plan,sport,target_date,metrics=None):
    plan=validate_race(plan)
    if not plan or not plan['enabled']: return []
    days=(date.fromisoformat(plan['date'])-date.fromisoformat(target_date)).days
    rows=[('比赛计划',f'{plan.get("name") or "未命名赛事"} · {plan["date"]} · '+
           (f'距建议训练日 {days} 天' if days>0 else '建议训练日为比赛日' if days==0 else f'已结束 {-days} 天')),
          ('赛事优先级',{'A':'A · 主要目标赛','B':'B · 次要比赛','C':'C · 体验或练习赛'}[plan.get('priority','B')])]
    rows.append(('比赛项目',{'running':'跑步','cycling':'骑车','swimming':'游泳','climbing':'攀岩'}[plan['sport']]))
    distance=plan.get('distance_km'); minutes=plan.get('goal_minutes')
    rows.append(('赛道信息',f'{distance:g} 公里' if distance else '距离未填写'))
    if 'elevation_m' in plan:
        rows[-1]=(rows[-1][0],rows[-1][1]+f' · 爬升 {plan["elevation_m"]:g} 米；平均配速不能代表坡段强度')
    if distance and minutes:
        if plan['sport']=='running': value=f'{pace(minutes*60/distance)}/km'
        elif plan['sport']=='swimming':value=f'{pace(minutes*6/distance)}/100m'
        elif plan['sport']=='cycling':value=f'{distance*60/minutes:.1f} km/h'
        else:value=f'{minutes:g} 分钟目标'
        rows.append(('比赛理论目标',value+'（仅目标换算，不作为当天训练区间或完赛预测）'))
    if days<0: text='这是过去赛事，不能作为即将参赛的依据；先确认赛后酸痛、损伤与恢复，再安排下一阶段。'
    elif plan['sport']!=sport:text='比赛与本次训练项目不同，不换算专项负荷；当前训练仅作交叉训练参考，需保留比赛专项恢复。'
    elif days==0:text='建议训练日为比赛日；本页轻松训练数值不构成比赛处方。先复核症状、赛道与补给；恢复不足时不以目标成绩覆盖安全判断。'
    elif days<=7:text='比赛临近：不补课、不临时增加长距离或陌生刺激；当前仅支持轻松训练方向，结合既有减量计划和症状复核。'
    else:text='比赛尚有准备时间；以稳定、可恢复的专项训练为主。距离、爬升和目标成绩用于识别需求，当前数据不足以自动生成完整周期计划。'
    rows.append(('备赛分析',text))
    if plan['sport']=='running' and sport=='running' and days>=0:
        longest=(metrics or {}).get('longest_run_30d_km')
        rows.append(('专项准备度',f'已记录近30天最长跑 {longest:g} 公里'+
                     (f'，赛事 {distance:g} 公里；'+('比赛距离超过近期已记录最长跑，不建议临近比赛突击补量。' if distance>longest else '近期有覆盖比赛距离的记录，但这不代表比赛强度已准备就绪。') if distance else '；赛事距离尚未填写。')
                     if type(longest) in (int,float) else '缺少近30天最长跑记录，无法核对比赛距离准备度；不能据此预测完赛。'))
    if plan.get('notes'): rows.append(('赛事备注',plan['notes']))
    return rows


def session_targets(sport, goal, settings, suggested_minutes=None):
    validate_targets({sport:settings})
    rows=[]
    def add(label, text): rows.append((label,text))
    def pair(low, high, unit):
        return f'{settings[low]:g}–{settings[high]:g} {unit}（个人已保存区间）' if low in settings else '待设置个人轻松训练区间；不从目标心率推算'
    minutes=settings.get('minutes')
    if sport=='running' and suggested_minutes:
        minutes=min(minutes,suggested_minutes) if minutes else suggested_minutes
    if sport in {'running','cycling','climbing'}:
        add('建议时长', f'{minutes:g} 分钟'+('（恢复筛查上限内）' if sport=='running' else '（个人计划，需结合专项耐受复核）') if minutes else '待设置该项目单次轻松训练时长')
    if sport in {'running','cycling'}:
        add('训练心率',pair('hr_low','hr_high','bpm'))
    if sport=='running':
        add('轻松配速', f'{pace(settings["pace_fast"])}–{pace(settings["pace_slow"])}/km（个人已保存区间）' if 'pace_fast' in settings else '待设置个人轻松配速；保持完整交谈，不使用比赛目标配速替代')
        add('建议距离', f'{minutes*60/settings["pace_slow"]:.1f}–{minutes*60/settings["pace_fast"]:.1f} 公里（由时长和个人轻松配速换算，以先到时长为准）' if minutes and 'pace_fast' in settings else '待补充个人轻松配速后，按建议时长换算公里数')
        match=re.search(r'(\d+(?:\.\d+)?)\s*(?:公里|km)\D{0,12}?(\d+(?:\.\d+)?)\s*(?:分钟|min)',goal,re.I)
        if match and float(match[1])>0 and float(match[2])>0:
            add('理论目标配速',f'{pace(float(match[2])*60/float(match[1]))}/km（目标时间÷距离换算的平均比赛配速；不代表当前能力或日常训练强度）')
    elif sport=='cycling':
        add('骑行功率',pair('watts_low','watts_high','W'))
        add('平路速度参考',pair('speed_low','speed_high','km/h'))
        add('预计距离',f'{minutes*settings["speed_low"]/60:.1f}–{minutes*settings["speed_high"]/60:.1f} 公里（个人平路速度换算；坡度、风和室内骑行不适用）' if minutes and 'speed_low' in settings else '待设置时长与个人平路速度；室内骑行优先看时长和功率')
    elif sport=='swimming':
        distance=settings.get('distance'); reps=settings.get('reps')
        add('总距离',f'{distance:g} 米（个人轻松训练计划，非能力测试）' if distance else '待设置个人可耐受的轻松游总米数')
        add('分组',f'{reps:g} × {distance/reps:g} 米（需适配泳池长度）' if distance and reps else '待设置总米数和组数；不自动推断泳池长度')
        add('组间休息',f'{settings["rest"]:g} 秒（个人计划；呼吸未恢复可延长）' if 'rest' in settings else '待设置；呼吸未恢复不要开始下一组')
        add('游泳配速',f'{pace(settings["pace_fast"])}–{pace(settings["pace_slow"])}/100m（个人已保存区间）' if 'pace_fast' in settings else '待设置个人轻松游每100米配速；不套用跑步心率')
    elif sport=='climbing':
        add('技术路线',settings.get('grade','待设置已熟悉且可轻松完成的路线等级；保留原分级体系'))
        add('路线数量',f'{settings["reps"]:g} 条/次（个人计划；动作变形或指痛即停止）' if 'reps' in settings else '待设置轻松技术路线条数；不安排极限尝试')
        add('路线间休息',f'{settings["rest"]:g} 秒（个人计划；握力未恢复应延长）' if 'rest' in settings else '待设置；握力恢复后再开始，不用心率推断指部恢复')
    return rows
