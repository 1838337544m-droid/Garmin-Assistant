import pytest
from session_targets import validate_race, race_context


def test_race_plan_is_considered_relative_to_training_day():
    plan={'enabled':True,'name':'城市10公里','sport':'running','date':'2026-12-01',
          'distance_km':10,'goal_minutes':50,'elevation_m':100,'priority':'A'}
    rows=dict(race_context(plan,'running','2026-11-28'))
    assert '3 天' in rows['比赛计划']
    assert '5:00/km' in rows['比赛理论目标']
    assert '不补课' in rows['备赛分析']
    assert '100' in rows['赛道信息']


def test_past_and_cross_sport_races_are_not_current_running_targets():
    plan={'enabled':True,'sport':'cycling','name':'骑行','date':'2026-11-27','distance_km':100}
    assert '已结束' in dict(race_context(plan,'running','2026-11-28'))['比赛计划']
    assert '不换算' in dict(race_context(plan,'running','2026-11-26'))['备赛分析']


def test_race_distance_uses_recorded_running_preparation_without_prediction():
    plan={'enabled':True,'sport':'running','date':'2026-12-01','distance_km':42.195}
    rows=dict(race_context(plan,'running','2026-11-28',{'longest_run_30d_km':12}))
    assert '12 公里' in rows['专项准备度']
    assert '不建议' in rows['专项准备度']


@pytest.mark.parametrize('p',[{'enabled':True}, {'enabled':'yes'},
    {'enabled':True,'sport':'running','date':'2026-02-30','name':'x'},
    {'enabled':True,'sport':'running','date':'2026-12-01','name':'x','distance_km':-1}])
def test_invalid_race_rejected(p):
    with pytest.raises(ValueError):validate_race(p)
