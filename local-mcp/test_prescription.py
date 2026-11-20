from prescription import build_prescription, classify_activity


SAFE = {'decision': 'easy_if_well', 'missing': [], 'flags': []}


def test_cross_training_names_primary_capacity_without_claiming_running_work():
    result = build_prescription({'primary_sport': 'running', 'goal': '10 km'}, 'cycling', SAFE, [])
    assert result['prescription_status'] in {'easy', 'base'}
    assert '交叉训练' in result['capacity_summary']
    assert '跑步专项训练' not in result['capacity_summary']


def test_unknown_activity_and_climbing_never_enable_quality_candidate():
    assert classify_activity({'activityType': {'typeKey': 'mystery'}}) == 'unknown'
    result = build_prescription({'primary_sport': 'climbing', 'goal': '技术'}, 'climbing', SAFE, [])
    assert result['prescription_status'] != 'quality_candidate'
    assert '指力' in result['evidence_boundary']


def test_swimming_requires_shoulder_and_alone_answers():
    result = build_prescription({'primary_sport': 'swimming', 'goal': '耐力'}, 'swimming', SAFE, [])
    assert result['prescription_status'] == 'recover'
    assert '肩痛' in result['evidence_boundary']


def test_unsafe_swimming_answers_force_recovery():
    for answers in ({'shoulder_pain': True, 'swimming_alone': False},
                    {'shoulder_pain': False, 'swimming_alone': True}):
        r=build_prescription({'primary_sport':'swimming'},'swimming',SAFE,[],swimming_safety=answers)
        assert r['prescription_status']=='recover'
