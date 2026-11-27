from datetime import datetime, timezone, timedelta
from garmin_local.dashboard_defaults import save_defaults,load_defaults


def test_saved_state_does_not_become_fresh_on_repeated_analysis(tmp_path):
    now=datetime(2026,11,25,tzinfo=timezone.utc)
    body={'session_sport':'running','planned_km':5,'subjective':{'pain_0_10':0}}
    first,subjective,_=save_defaults(tmp_path,body,now)
    assert subjective==body['subjective']
    again,subjective,_=save_defaults(tmp_path,body,now+timedelta(days=2))
    assert again['state_recorded_at']==first['state_recorded_at']
    assert subjective=={}
    assert load_defaults(tmp_path)['planned_km']==5
    assert load_defaults(tmp_path)['subjective']=={'pain_0_10':0}


def test_explicit_confirmation_renews_without_retyping(tmp_path):
    body={'session_sport':'swimming','subjective':{},'swimming_safety':{'shoulder_pain':False,'swimming_alone':False}}
    now=datetime(2026,11,25,tzinfo=timezone.utc)
    save_defaults(tmp_path,body,now)
    _,_,swim=save_defaults(tmp_path,{**body,'state_confirmed':True},now+timedelta(days=2))
    assert swim==body['swimming_safety']


def test_editing_one_field_does_not_refresh_other_old_fields(tmp_path):
    now=datetime(2026,11,25,tzinfo=timezone.utc)
    body={'session_sport':'running','subjective':{'pain_0_10':0,'fatigue_0_10':2}}
    save_defaults(tmp_path,body,now)
    edited={**body,'subjective':{'pain_0_10':0,'fatigue_0_10':5}}
    _,current,_=save_defaults(tmp_path,edited,now+timedelta(days=2))
    assert current=={'fatigue_0_10':5}


def test_sport_quantities_and_race_remain_saved_without_retyping(tmp_path):
    body={'session_sport':'running','sport_targets':{'running':{'hr_low':120,'hr_high':140}},
          'race_plan':{'enabled':True,'name':'10K','sport':'running','date':'2026-12-01','distance_km':10}}
    save_defaults(tmp_path,body)
    again,_,_=save_defaults(tmp_path,{'session_sport':'cycling'})
    assert again['sport_targets']==body['sport_targets']
    assert again['race_plan']==body['race_plan']


def test_explicit_test_result_is_remembered_and_can_be_cleared(tmp_path):
    benchmark={'date':'2026-11-20','kind':'race','distance_km':10,'time_minutes':55}
    save_defaults(tmp_path,{'session_sport':'running','running_benchmark':benchmark})
    again,_,_=save_defaults(tmp_path,{'session_sport':'running'})
    assert again['running_benchmark']==benchmark
    cleared,_,_=save_defaults(tmp_path,{'session_sport':'running','running_benchmark':None})
    assert cleared['running_benchmark'] is None
