import pytest
from garmin_local.session_targets import validate_targets, session_targets


def test_running_separates_race_goal_from_easy_training():
    rows = dict(session_targets('running', '10 公里跑进 50 分钟 心率 145',
        {'minutes': 30, 'pace_fast': 360, 'pace_slow': 420, 'hr_low': 125, 'hr_high': 140}, 25))
    assert '5:00/km' in rows['理论目标配速']
    assert '6:00–7:00/km' in rows['轻松配速']
    assert '125–140' in rows['训练心率']
    assert '3.6–4.2' in rows['建议距离']
    assert '25' in rows['建议时长']


def test_missing_personal_zone_does_not_invent_hr_from_goal():
    rows = dict(session_targets('running', '10公里50分钟 心率145', {}, 20))
    assert '待设置' in rows['训练心率']
    assert '待设置' in rows['轻松配速']
    assert '5:00/km' in rows['理论目标配速']


def test_each_sport_uses_its_own_units_and_no_running_metrics():
    cycling = dict(session_targets('cycling', '', {'minutes':30,'watts_low':90,'watts_high':120}, 15))
    assert '90–120 W' in cycling['骑行功率']
    assert '轻松配速' not in cycling
    swimming = dict(session_targets('swimming', '', {'distance':800,'reps':8,'rest':30,'pace_fast':120,'pace_slow':150}, 15))
    assert '8 × 100' in swimming['分组']
    assert '/100m' in swimming['游泳配速']
    climbing = dict(session_targets('climbing', '', {'grade':'5.8','reps':4,'rest':180}, 15))
    assert '5.8' in climbing['技术路线']
    assert not any('心率' in k or '配速' in k for k in climbing)


@pytest.mark.parametrize('settings', [{'running':{'hr_low':150,'hr_high':130}},
    {'running':{'minutes':float('nan')}}, {'swimming':{'reps':2.5}},
    {'running':{'pace_fast':300}}, {'other':{}}, {'climbing':{'grade':'x'*81}}])
def test_invalid_settings_rejected(settings):
    with pytest.raises(ValueError): validate_targets(settings)


def test_safety_gates_suppress_numeric_dose():
    from garmin_local.prescription import build_prescription
    p = {'primary_sport':'running','goal':'10公里50分钟',
         'sport_targets':{'running':{'minutes':30,'hr_low':120,'hr_high':140}}}
    r = build_prescription(p,'running',{'decision':'avoid_running'},[])
    assert not r.get('session_targets')
