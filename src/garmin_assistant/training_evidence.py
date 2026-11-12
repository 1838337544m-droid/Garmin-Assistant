"""Compute interpretable training stimuli and an adapted HRV-guided decision rule."""
from math import exp, log
from statistics import mean, median, stdev

from .readiness import number

GARMIN_EFFECT = 'https://www8.garmin.com/manuals/webhelp/GUID-E5C62F3F-DCE3-4197-8CA5-E419B2A55D12/EN-US/GUID-7275629E-743A-4658-A284-C84F42A66AE5.html'
HRV_RULE = 'https://doi.org/10.3389/fspor.2025.1578478'


def stimulus(rows, key):
    values = [row[key] for row in rows if number(row.get(key)) and 0 <= row[key] <= 5]
    return {'sessions_with_score': len(values), 'sessions_at_least_3': sum(value >= 3 for value in values),
            'median_score': round(median(values), 1) if values else None}


def recorded_total(rows, key):
    values = [row[key] for row in rows if number(row.get(key)) and row[key] >= 0]
    return {'total': round(sum(values), 1) if values else None, 'sessions_with_value': len(values)}


def matched_speed_change(recent, prior):
    def samples(rows):
        keys = ('averageHR', 'duration', 'distance')
        return [tuple(row[key] for key in keys) for row in rows
                if all(number(row.get(key)) and row[key] > 0 for key in keys)]

    candidates = samples(prior)
    changes = []
    for hr, seconds, distance in samples(recent):
        matches = [index for index, (old_hr, old_seconds, _) in enumerate(candidates)
                   if abs(hr - old_hr) <= 5 and .8 <= seconds / old_seconds <= 1.2]
        if matches:
            best = min(matches, key=lambda index: (abs(hr - candidates[index][0]), abs(seconds - candidates[index][1])))
            _, old_seconds, old_distance = candidates.pop(best)
            changes.append(100 * ((distance / seconds) / (old_distance / old_seconds) - 1))
    return {'pairs': len(changes), 'median_speed_change_pct': round(median(changes), 1) if len(changes) >= 3 else None}


def training_evidence(rows, earlier):
    def vo2_estimates(activities):
        # Keep one estimate per calendar day to avoid weighting double sessions.
        by_day = {}
        for row in sorted(activities, key=lambda item: item['startTimeLocal']):
            value = row.get('vO2MaxValue')
            if number(value) and 0 < value <= 100:
                by_day[row['startTimeLocal'][:10]] = value
        return list(by_day.values())

    recent_vo2, prior_vo2 = vo2_estimates(rows), vo2_estimates(earlier)
    return {
        'aerobic': stimulus(rows, 'aerobicTrainingEffect'),
        'anaerobic': stimulus(rows, 'anaerobicTrainingEffect'),
        'prior_aerobic': stimulus(earlier, 'aerobicTrainingEffect'),
        'prior_anaerobic': stimulus(earlier, 'anaerobicTrainingEffect'),
        'activity_kcal': recorded_total(rows, 'calories'),
        'strength_sets': recorded_total(rows, 'totalSets'),
        'strength_reps': recorded_total(rows, 'totalReps'),
        'vo2max_estimates': {'recent_days': len(recent_vo2), 'prior_days': len(prior_vo2),
                             'recent_median': round(median(recent_vo2), 1) if recent_vo2 else None,
                             'prior_median': round(median(prior_vo2), 1) if prior_vo2 else None,
                             'change': round(median(recent_vo2) - median(prior_vo2), 1)
                             if len(recent_vo2) >= 3 and len(prior_vo2) >= 3 else None},
        'stimulus_source': GARMIN_EFFECT,
    }


def hrv_guided_rule(baseline, recent):
    """Use the published log-scale boundary with nightly rather than morning HRV."""
    output = {'reference': HRV_RULE, 'baseline_samples': len(baseline), 'recent_samples': len(recent),
              'status': 'insufficient_data'}
    if len(baseline) < 21 or len(recent) < 5:
        return output
    logs = [log(value) for value in baseline]
    lower_limit = mean(logs) - .5 * stdev(logs)
    recent_average = mean(log(value) for value in recent)
    output.update({'status': 'below_threshold' if recent_average < lower_limit else 'at_or_above_threshold',
                   'baseline_geomean_ms': round(exp(mean(logs)), 2),
                   'lower_limit_ms': round(exp(lower_limit), 2),
                   'recent_geomean_ms': round(exp(recent_average), 2)})
    return output
