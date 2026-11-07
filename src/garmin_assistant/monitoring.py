"""Descriptive training trends and a transparent, personal recovery screen."""
from collections import defaultdict
from datetime import date, timedelta
from statistics import median, quantiles

from .readiness import number, object_or_empty

SPORTS = {
    'swimming': ('游泳', 'swimming'),
    'cycling': ('自行车', 'cycling'),
    'running': ('跑步', 'running'),
}
RECOVERY_SOURCES = [
    {'id': 'kellmann2018', 'title': 'Recovery and Performance in Sport: Consensus Statement', 'year': 2018,
     'url': 'https://pubmed.ncbi.nlm.nih.gov/29345524/'},
    {'id': 'saw2016', 'title': 'Monitoring the athlete training response', 'year': 2016,
     'url': 'https://pubmed.ncbi.nlm.nih.gov/26423706/'},
    {'id': 'bellenger2016', 'title': 'Monitoring Athletic Training Status Through Autonomic Heart Rate Regulation', 'year': 2016,
     'url': 'https://pubmed.ncbi.nlm.nih.gov/26888648/'},
    {'id': 'cycling2025', 'title': 'Individual training prescribed by heart rate variability, heart rate and well-being scores in experienced cyclists',
     'year': 2025, 'url': 'https://pubmed.ncbi.nlm.nih.gov/41028151/'},
]


def activity_kind(row):
    kind = object_or_empty(row.get('activityType')).get('typeKey')
    return kind if isinstance(kind, str) and kind else 'unknown'


def sport_family(kind):
    if 'swim' in kind:
        return 'swimming'
    if 'cycl' in kind or 'bik' in kind:
        return 'cycling'
    if 'running' in kind or kind in ('run', 'virtual_run'):
        return 'running'
    return kind


def activities_between(history, first, last):
    start, end = first.isoformat(), last.isoformat()
    return [row for row in history.get('activities', [])
            if row.get('isMultiSportParent') is not True and start <= str(row.get('startTimeLocal', ''))[:10] <= end]


def measure(rows, key, factor=1):
    return [row[key] * factor for row in rows if number(row.get(key)) and row[key] > 0]


def rounded_median(values):
    return round(median(values), 2) if values else None


def activity_totals(rows):
    distances = measure(rows, 'distance', .001)
    durations = measure(rows, 'duration', 1 / 60)
    heart_rates = measure(rows, 'averageHR')
    return {
        'sessions': len(rows), 'days_with_activity': len({row['startTimeLocal'][:10] for row in rows}),
        'distance_km_recorded': round(sum(distances), 2) if distances else None,
        'distance_sessions': len(distances),
        'duration_min_recorded': round(sum(durations), 1) if durations else None,
        'duration_sessions': len(durations),
        'median_session_avg_hr_bpm': rounded_median(heart_rates), 'heart_rate_sessions': len(heart_rates),
    }


def performance(rows, family):
    pairs = [(row['distance'], row['duration']) for row in rows
             if number(row.get('distance')) and row['distance'] > 0
             and number(row.get('duration')) and row['duration'] > 0]
    if family == 'running':
        values, unit = [seconds * 1000 / meters for meters, seconds in pairs], 'seconds/km'
    elif family == 'swimming':
        values, unit = [seconds * 100 / meters for meters, seconds in pairs], 'seconds/100m'
    elif family == 'cycling':
        values, unit = [meters * 3.6 / seconds for meters, seconds in pairs], 'km/h'
    else:
        return None
    return {'median': rounded_median(values), 'unit': unit, 'sessions': len(values)}


def health_series(history, first, last):
    first, last = first.isoformat(), last.isoformat()
    series = {key: {} for key in ('hrv_ms', 'resting_hr_bpm', 'sleep_hours', 'daily_spo2_pct', 'sleep_spo2_pct')}

    def add(metric, day, value, divisor=1):
        if isinstance(day, str) and first <= day <= last and number(value) and value > 0:
            if 'spo2' not in metric or value <= 100:
                series[metric][day] = value / divisor

    for row in history.get('daily_summaries', []):
        day = row.get('calendarDate')
        add('resting_hr_bpm', day, object_or_empty(row.get('heartRate')).get('restingValue'))
        add('daily_spo2_pct', day, object_or_empty(row.get('pulseOx')).get('avgValue'))
    for row in history.get('sleep_summaries', []):
        day = row.get('calendarDate')
        add('sleep_hours', day, row.get('sleepTimeSeconds'), 3600)
        add('sleep_spo2_pct', day, row.get('averageSpO2Value'))
    for row in history.get('hrv_summaries', []):
        add('hrv_ms', row.get('calendarDate'), row.get('lastNightAvg'))
    return series


def health_overview(history, as_of):
    end = date.fromisoformat(as_of) - timedelta(days=1)
    start = end - timedelta(days=89)
    recent_start = end - timedelta(days=6)
    cutoff = recent_start.isoformat()
    metrics = {}
    for name, dates in health_series(history, start, end).items():
        baseline = [value for day, value in dates.items() if day < cutoff]
        recent = [value for day, value in dates.items() if day >= cutoff]
        latest_day = max(dates, default=None)
        band = quantiles(baseline, n=4, method='inclusive')[::2] if len(baseline) >= 21 else None
        usable = band is not None and len(recent) >= 3 and latest_day >= (end - timedelta(days=2)).isoformat()
        recent_median = median(recent) if recent else None
        comparison = 'insufficient_data'
        if usable:
            comparison = ('below_personal_band' if recent_median < band[0] else
                          'above_personal_band' if recent_median > band[1] else 'within_personal_band')
        metrics[name] = {
            'observed_days': len(dates), 'missing_days': 90 - len(dates), 'median_90d': rounded_median(list(dates.values())),
            'baseline_days': len(baseline), 'baseline_median': rounded_median(baseline),
            'baseline_middle_50pct': [round(x, 2) for x in band] if band else None,
            'recent_days': len(recent), 'recent_median': rounded_median(recent),
            'latest_date': latest_day, 'latest_value': round(dates[latest_day], 2) if latest_day else None,
            'comparison': comparison,
        }
    return {'start_date': start.isoformat(), 'end_date': end.isoformat(), 'recent_start': cutoff,
            'baseline_end': (recent_start - timedelta(days=1)).isoformat(), 'metrics': metrics}


def training_status(history, as_of, language):
    end = date.fromisoformat(as_of)
    start = end - timedelta(days=29)
    current = activities_between(history, start, end)
    prior = activities_between(history, start - timedelta(days=30), start - timedelta(days=1))
    grouped, previous = defaultdict(list), defaultdict(list)
    for row in current:
        grouped[sport_family(activity_kind(row))].append(row)
    for row in prior:
        previous[sport_family(activity_kind(row))].append(row)
    sports = []
    for family in sorted(grouped.keys() | previous.keys(), key=lambda key: (-len(grouped.get(key, [])), key)):
        rows, earlier = grouped.get(family, []), previous.get(family, [])
        by_type = []
        for kind in sorted({activity_kind(row) for row in rows}):
            same_type = [row for row in rows if activity_kind(row) == kind]
            prior_type = [row for row in earlier if activity_kind(row) == kind]
            by_type.append({'type': kind, **activity_totals(same_type), 'performance': performance(same_type, family),
                            'previous_performance': performance(prior_type, family)})
        sports.append({'sport': family, **activity_totals(rows), 'sessions_per_week': round(len(rows) * 7 / 30, 1),
                       'previous_30d': activity_totals(earlier), 'by_activity_type': by_type})
    note = ('训练量与同类活动的配速或速度变化属于记录趋势。路线、天气、泳池条件和强度不同都会影响对比，判断训练成效需要条件相近的表现测试。'
            if language == 'zh' else 'Volume and same-type pace or speed changes describe recorded trends. Routes, weather, pool conditions and effort affect comparisons. Assess training effects with comparable performance tests.')
    return {'as_of': as_of, 'activity_window': {'start_date': start.isoformat(), 'end_date': as_of,
            'previous_start_date': (start - timedelta(days=30)).isoformat(),
            'previous_end_date': (start - timedelta(days=1)).isoformat()},
            'sports': sports, 'body_status': health_overview(history, as_of), 'interpretation': note}


def recovery_status(history, as_of, subjective, fresh, language):
    body = health_overview(history, as_of)
    if subjective is not None and not isinstance(subjective, dict):
        raise ValueError('Subjective ratings must be an object')
    subject = {name: (subjective or {}).get(name) for name in ('fatigue_0_10', 'soreness_0_10')}
    for value in subject.values():
        if value is not None and (not number(value) or not 0 <= value <= 10):
            raise ValueError('Fatigue and soreness ratings must be 0 to 10')
    signals = {'hrv_ms': ('below_personal_band', 'bellenger2016'),
               'resting_hr_bpm': ('above_personal_band', 'cycling2025'),
               'sleep_hours': ('below_personal_band', 'kellmann2018')}
    evidence = {metric: source for metric, (_, source) in signals.items()}
    missing = [key for key in signals if body['metrics'][key]['comparison'] == 'insufficient_data']
    missing += [key for key, value in subject.items() if value is None]
    if not fresh:
        missing.append('fresh_complete_sync')
    cues = [key for key, (direction, _) in signals.items() if body['metrics'][key]['comparison'] == direction]
    high_subjective = [key for key, value in subject.items() if value is not None and value >= 7]
    cues.extend(high_subjective)
    evidence.update({key: 'saw2016' for key in subject})
    end = date.fromisoformat(as_of)
    load = {'recent_7d': activity_totals(activities_between(history, end - timedelta(days=6), end)),
            'prior_7d': activity_totals(activities_between(history, end - timedelta(days=13), end - timedelta(days=7)))}
    decision = ('recovery_caution' if high_subjective or len(cues) >= 2 else
                'insufficient_data' if missing else 'mixed_signals' if cues else 'no_elevated_signal_detected')
    descriptions = {
        'recovery_caution': ('近期信号提示优先恢复。', 'Recent signals support prioritizing recovery.'),
        'insufficient_data': ('资料不足，暂不能判断当前恢复状态。', 'Available data are insufficient to assess current recovery.'),
        'mixed_signals': ('有单项偏离，请结合主观感受和后续趋势复评。', 'One signal is outside the usual range. Review it alongside how you feel and the next observations.'),
        'no_elevated_signal_detected': ('目前未发现所检查的偏离，仍需结合当天感受。', 'The checked signals show no elevated cue. Consider how you feel on the day.'),
    }
    return {'as_of': as_of, 'status': decision, 'summary': descriptions[decision][language != 'zh'],
            'body_status': body, 'subjective': subject, 'training_volume': load, 'missing': missing,
            'cues': cues, 'signal_evidence': evidence, 'sources': [dict(source) for source in RECOVERY_SOURCES],
            'method': {'baseline_days': 83, 'recent_days': 7, 'min_baseline_observations': 21,
                       'min_recent_observations': 3, 'subjective_caution_0_10': 7,
                       'note': ('个人中间 50% 区间和 7 分自评是本应用的描述与保守提示。训练时长描述训练量，血氧单列。恢复速度需要同类训练后的多次随访。'
                                if language == 'zh' else 'Personal middle-50% bands and the 7/10 rating are descriptive and conservative app rules. Duration describes volume, SpO₂ is contextual, and recovery speed needs repeated comparable post-training observations.')}}


def validate_goal(sport, distance_km, minutes):
    limits = {'swimming': 100, 'cycling': 1000, 'running': 200}
    if sport not in limits or not number(distance_km) or not 0 < distance_km <= limits[sport]:
        raise ValueError('Choose a supported sport and a positive target distance in km')
    if not number(minutes) or not 0 < minutes <= 1440:
        raise ValueError('Target time must be positive and at most 1440 minutes')


def tomorrow_plan(history, as_of, sport, distance_km, minutes, subjective, fresh, language):
    validate_goal(sport, distance_km, minutes)
    zh = language == 'zh'
    if subjective is not None and not isinstance(subjective, dict):
        raise ValueError('Subjective symptoms must be an object')
    subject = subjective or {}
    symptom_flags = ('illness', 'pain_with_walking', 'focal_bone_pain', 'chest_pain', 'fainting')
    if any(subject.get(key) is not None and type(subject[key]) is not bool for key in symptom_flags):
        raise ValueError('Symptom flags must be boolean or null')
    recovery = recovery_status(history, as_of, subject, fresh, language)
    end = date.fromisoformat(as_of)
    recent = [row for row in activities_between(history, end - timedelta(days=29), end)
              if sport_family(activity_kind(row)) == sport]
    recent_durations = measure(recent, 'duration', 1 / 60)
    missing = [name for name in ('pain_0_10', 'illness', 'chest_pain', 'fainting') if subject.get(name) is None]
    if sport == 'running':
        missing.extend(name for name in ('pain_with_walking', 'focal_bone_pain') if subject.get(name) is None)
    pain = subject.get('pain_0_10')
    if pain is not None and (not number(pain) or not 0 <= pain <= 10):
        raise ValueError('Pain rating must be 0 to 10')
    urgent = subject.get('chest_pain') is True or subject.get('fainting') is True
    blocked = (subject.get('illness') is True or subject.get('pain_with_walking') is True or
               subject.get('focal_bone_pain') is True or (pain is not None and pain > 0))
    duration = 0
    if urgent:
        decision = 'stop_and_seek_care'
        recommendation = ('暂停运动并尽快就医。若胸痛或晕厥正在发生或症状严重，请立即寻求急救。'
                          if zh else 'Stop exercise and seek medical care promptly. Seek emergency care for ongoing or severe chest pain or fainting.')
    elif blocked:
        decision = 'defer_training'
        recommendation = ('明天先暂缓训练，待伤痛或疾病缓解后复评。' if zh else 'Defer training and reassess after the pain or illness improves.')
    elif recovery['status'] == 'recovery_caution':
        decision = 'prioritize_recovery'
        recommendation = ('明天优先恢复，暂缓按目标配速或时长训练。' if zh else 'Prioritize recovery tomorrow and defer target-pace or target-duration training.')
    elif missing or recovery['missing'] or not recent_durations:
        decision = 'insufficient_data'
        recommendation = ('补充症状、恢复数据和该项目近期记录后再定训练。明早重新检查。'
                          if zh else 'Recheck in the morning after filling gaps in symptoms, recovery data and recent history for this sport.')
    else:
        decision = 'easy_if_well'
        duration = max(1, min(40, int(.7 * median(recent_durations))))
        advice = {
            'swimming': ('在熟悉的泳池轻松游，可分短组并充分休息。', 'Swim easily in a familiar pool with short repetitions and ample rest.'),
            'cycling': ('用轻档轻松骑行，可选择室内车或熟悉的平路。', 'Ride easily in a light gear on an indoor bike or familiar flat route.'),
            'running': ('选择熟悉的平路，保持能完整说话的轻松强度。', 'Run on a familiar flat route at a conversational effort.'),
        }
        recommendation = ((f'若明早复评正常，可考虑约 {duration} 分钟轻松训练。' if zh else
                           f'If the morning recheck is normal, consider about {duration} minutes at an easy effort. ')
                          + advice[sport][not zh])
    if sport == 'swimming':
        target_metric = {'value': round(minutes * 6 / distance_km, 2), 'unit': 'seconds/100m'}
    elif sport == 'cycling':
        target_metric = {'value': round(distance_km * 60 / minutes, 2), 'unit': 'km/h'}
    else:
        target_metric = {'value': round(minutes * 60 / distance_km, 2), 'unit': 'seconds/km'}
    return {'as_of': as_of, 'target_date': (end + timedelta(days=1)).isoformat(), 'sport': sport,
            'sport_label': SPORTS[sport][not zh], 'goal': {'distance_km': distance_km, 'minutes': minutes,
            'target_average': target_metric}, 'decision': decision, 'recommendation': recommendation,
            'provisional': True, 'suggested_easy_minutes': duration, 'recent_sport_30d': activity_totals(recent),
            'recovery': recovery, 'missing': missing + recovery['missing'] + ([] if recent_durations else ['recent_sport_duration']),
            'goal_note': ('目标均速或配速用于描述目标。明天的强度以个人恢复和近期同项目记录为依据。'
                          if zh else 'Target pace or speed describes the goal. Tomorrow’s effort depends on personal recovery and recent history in this sport.')}


def render_monitoring_report(result):
    zh = result['language'] == 'zh'

    def local(chinese, english):
        return chinese if zh else english

    def shown(value):
        return local('缺测', 'Unavailable') if value is None else str(value)

    recovery = result.get('recovery', result)
    body = recovery['body_status']
    title = (f"{result['target_date']} {result['sport_label']} " + local('建议', 'plan') if 'sport' in result else
             local('训练效果与身体状态', 'Training progress and current status') if 'sports' in result else local('疲劳与恢复', 'Fatigue and recovery'))
    lines = [f'# {title}', '', local('截至 ', 'As of ') + result['as_of'],
             local('同步完整', 'Sync completed') if result['sync']['fresh'] else local('同步未完整，结果可能缺失或过期。', 'Sync incomplete. Results may be incomplete or stale.'), '']
    if 'sport' in result:
        goal = result['goal']
        metric = goal['target_average']
        lines += [f"{local('目标', 'Goal')} {goal['distance_km']:g} km / {goal['minutes']:g} min ({metric['value']:g} {metric['unit']})", '',
                  result['recommendation'], '', result['goal_note'], '']
    if 'sports' in result:
        window = result['activity_window']
        lines += [f"## {window['start_date']} — {window['end_date']}", '',
                  local('| 项目 | 次数 | 次/周 | 记录时长 (min) | 记录距离 (km) | 心率中位数 (bpm) | 前 30 天次数 |',
                        '| Sport | Sessions | Per week | Recorded minutes | Recorded km | Median HR (bpm) | Prior 30-day sessions |'),
                  '|---|---:|---:|---:|---:|---:|---:|']
        for sport in result['sports']:
            name = SPORTS.get(sport['sport'], (sport['sport'], sport['sport']))[not zh]
            lines.append(f"| {name} | {sport['sessions']} | {sport['sessions_per_week']} | {shown(sport['duration_min_recorded'])} | {shown(sport['distance_km_recorded'])} | {shown(sport['median_session_avg_hr_bpm'])} | {sport['previous_30d']['sessions']} |")
        for sport in result['sports']:
            for activity in sport['by_activity_type']:
                if (metric := activity['performance']) is not None:
                    prior = activity['previous_performance']
                    lines.append(f"\n- {activity['type']} · {shown(metric['median'])} {metric['unit']} ({metric['sessions']} {local('次', 'sessions')}) · {local('前 30 天', 'Prior 30 days')} {shown(prior['median'])} ({prior['sessions']} {local('次', 'sessions')})")
        if not result['sports']:
            lines += ['', local('目前无可用运动记录。', 'No activity records are available.')]
        lines += ['', result['interpretation'], '']
    if 'summary' in recovery:
        lines += [recovery['summary'], '',
                  local('自评疲劳 / 酸痛（0–10）', 'Reported fatigue / soreness (0–10)') + f"  {shown(recovery['subjective']['fatigue_0_10'])} / {shown(recovery['subjective']['soreness_0_10'])}",
                  local('近 7 天 / 前 7 天训练分钟', 'Recorded minutes, recent / prior 7 days') + '  ' + ' / '.join(shown(recovery['training_volume'][period]['duration_min_recorded']) for period in ('recent_7d', 'prior_7d')), '',
                  local('提示指标', 'Recovery cues') + '  ' + (', '.join(recovery['cues']) or local('暂无', 'None recorded')), '', recovery['method']['note'], '']
    labels = {
        'hrv_ms': local('夜间 HRV（ms）', 'Nightly HRV (ms)'), 'resting_hr_bpm': local('静息心率（bpm）', 'Resting HR (bpm)'),
        'sleep_hours': local('睡眠时长（h）', 'Sleep duration (h)'), 'daily_spo2_pct': local('日均血氧（%）', 'Daily SpO₂ (%)'),
        'sleep_spo2_pct': local('睡眠血氧（%）', 'Sleep SpO₂ (%)'),
    }
    trends = {'insufficient_data': local('数据不足', 'Insufficient data'),
              'below_personal_band': local('低于个人区间', 'Below personal band'),
              'above_personal_band': local('高于个人区间', 'Above personal band'),
              'within_personal_band': local('在个人区间内', 'Within personal band')}
    sources = {source['id']: source for source in recovery.get('sources', [])}
    lines += [f"## {body['start_date']} — {body['end_date']}", '',
              local('| 指标 | 覆盖天数 | 90 天中位数 | 个人基线中位数 | 近 7 天中位数 | 近期对比 |',
                    '| Metric | Recorded days | 90-day median | Baseline median | Recent 7-day median | Recent comparison |'), '|---|---:|---:|---:|---:|---|']
    for key, metric in body['metrics'].items():
        comparison = trends[metric['comparison']]
        if source := sources.get(recovery.get('signal_evidence', {}).get(key)):
            comparison += f" [{source['year']}]({source['url']})"
        lines.append(f"| {labels[key]} | {metric['observed_days']}/90 | {shown(metric['median_90d'])} | {shown(metric['baseline_median'])} | {shown(metric['recent_median'])} | {comparison} |")
    lines += ['', local('个人区间采用基线中间 50%，用于展示个人变化。', 'The personal band uses the middle 50% of the baseline observations to describe within-person changes.')]
    if result.get('missing') or recovery.get('missing'):
        lines += ['', local('仍缺信息', 'Missing information') + '  ' + ', '.join(result.get('missing', recovery['missing']))]
    if recovery.get('sources'):
        lines += ['', f"## {local('研究出处', 'Research sources')}", '']
        lines.extend(f"- {source['title']} ({source['year']}). [PubMed]({source['url']})" for source in recovery['sources'])
        research = result.get('research', {})
        lines += ['', local('文献检索状态', 'Literature search status') + f"  {research.get('status', 'unavailable')} · {shown(research.get('checked_on'))}"]
    return '\n'.join(lines) + '\n'
