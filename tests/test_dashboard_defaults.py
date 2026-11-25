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
