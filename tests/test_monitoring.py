from datetime import date, timedelta

import pytest

from garmin_assistant.monitoring import recovery_status, tomorrow_plan, training_status
from garmin_assistant.training import TrainingWorkflow


AS_OF = '2026-11-07'


def day(ago):
    return (date.fromisoformat(AS_OF) - timedelta(days=ago)).isoformat()


def activity(ago, kind, meters, seconds):
    return {'activityType': {'typeKey': kind}, 'startTimeLocal': day(ago) + 'T06:00:00',
            'distance': meters, 'duration': seconds, 'averageHR': 130}


def test_progress_uses_garmin_pulse_ox_fields_and_separates_sport_contexts():
    history = {
        'daily_summaries': [{'calendarDate': day(1), 'pulseOx': {'avgValue': 96}, 'heartRate': {'restingValue': 51}},
                            {'calendarDate': day(0), 'pulseOx': {'avgValue': 90}}],
        'sleep_summaries': [{'calendarDate': day(1), 'averageSpO2Value': 98, 'sleepTimeSeconds': 27000}],
        'activities': [activity(1, 'lap_swimming', 1000, 1500), activity(2, 'open_water_swimming', 1500, 2400),
                       activity(31, 'lap_swimming', 1000, 1800), activity(3, 'road_biking', 10000, 1800)],
    }
    report = training_status(history, AS_OF, 'zh')
    assert report['sports'][0]['sport'] == 'swimming' and report['sports'][0]['sessions'] == 2
    assert report['sports'][0]['previous_30d']['sessions'] == 1
    pool, open_water = report['sports'][0]['by_activity_type']
    assert pool['performance']['median'] == 150 and pool['previous_performance']['median'] == 180
    assert open_water['previous_performance']['median'] is None
    metrics = report['body_status']['metrics']
    assert metrics['daily_spo2_pct']['median_90d'] == 96 and metrics['daily_spo2_pct']['missing_days'] == 89
    assert metrics['sleep_spo2_pct']['median_90d'] == 98
    assert metrics['hrv_ms']['median_90d'] is None


def healthy_history():
    return {
        'daily_summaries': [{'calendarDate': day(i), 'heartRate': {'restingValue': 52}} for i in range(1, 32)],
        'sleep_summaries': [{'calendarDate': day(i), 'sleepTimeSeconds': 27000} for i in range(1, 32)],
        'hrv_summaries': [{'calendarDate': day(i), 'lastNightAvg': 48} for i in range(1, 32)],
        'activities': [activity(2, 'lap_swimming', 1000, 1800), activity(3, 'road_biking', 20000, 3000),
                       activity(4, 'running', 5000, 1800)],
    }


def test_recovery_requires_subjective_ratings_and_reports_actual_signals():
    history = healthy_history()
    assert recovery_status(history, AS_OF, None, True, 'zh')['status'] == 'insufficient_data'
    for row in history['hrv_summaries'][:7]:
        row['lastNightAvg'] = 30
    result = recovery_status(history, AS_OF, {'fatigue_0_10': 8, 'soreness_0_10': 1}, True, 'en')
    assert result['status'] == 'recovery_caution' and result['cues'] == ['hrv_ms', 'fatigue_0_10']
    assert result['body_status']['metrics']['hrv_ms']['baseline_median'] == 48
    assert result['signal_evidence']['hrv_ms'] in {source['id'] for source in result['sources']}


@pytest.mark.parametrize('sport,distance,minutes,expected,unit', [
    ('swimming', 1, 25, 150, 'seconds/100m'), ('cycling', 20, 50, 24, 'km/h'), ('running', 5, 30, 360, 'seconds/km'),
])
def test_tomorrow_uses_selected_sport_and_requires_fresh_data(sport, distance, minutes, expected, unit):
    symptoms = {'fatigue_0_10': 2, 'soreness_0_10': 0, 'pain_0_10': 0, 'illness': False,
                'chest_pain': False, 'fainting': False, 'pain_with_walking': False, 'focal_bone_pain': False}
    plan = tomorrow_plan(healthy_history(), AS_OF, sport, distance, minutes, symptoms, True, 'en')
    assert plan['decision'] == 'easy_if_well' and plan['recent_sport_30d']['sessions'] == 1
    assert plan['goal']['target_average'] == {'value': expected, 'unit': unit}
    assert tomorrow_plan(healthy_history(), AS_OF, sport, distance, minutes, symptoms, False, 'en')['suggested_easy_minutes'] == 0
    symptoms['fainting'] = True
    assert tomorrow_plan({}, AS_OF, sport, distance, minutes, symptoms, False, 'en')['decision'] == 'stop_and_seek_care'


def test_training_workflow_syncs_once_and_saves_multisport_report(tmp_path, monkeypatch):
    workflow = TrainingWorkflow(None, tmp_path)
    monkeypatch.setattr(workflow, '_today', lambda: AS_OF)
    calls = []
    monkeypatch.setattr(workflow, 'sync', lambda: calls.append('sync') or {'status': 'partial'})
    monkeypatch.setattr('garmin_assistant.training.update_research', lambda *a: {'status': 'cached'})
    plan = workflow.plan_tomorrow('swimming', 1, 30)
    assert calls == ['sync'] and plan['sync']['fresh'] is False
    assert (tmp_path / 'reports' / 'tomorrow_swimming_2026-11-08.md').is_file()
    assert plan['function_menu'][3]['tool'] == 'garmin_plan_tomorrow'


def test_plan_rejects_nonboolean_symptom_input():
    with pytest.raises(ValueError, match='boolean'):
        tomorrow_plan(healthy_history(), AS_OF, 'cycling', 20, 50, {'chest_pain': 1}, True, 'en')
