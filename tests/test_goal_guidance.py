from datetime import date, timedelta
import pytest
from garmin_local.goal_guidance import build_goal_guidance, validate_benchmark


def fixture():
    as_of='2026-11-27'
    activities=[]
    for offset in range(1,29,2):
        activities.append({'activityType':{'typeKey':'running'},
            'startTimeLocal':(date.fromisoformat(as_of)-timedelta(days=offset)).isoformat(),
            'distance':5000,'duration':1800})
    profile={'primary_sport':'running','goal':'10公里50分钟'}
    settings={'sport_targets':{'running':{'hr_low':125,'hr_high':140,'pace_fast':360,'pace_slow':420}},
              'running_benchmark':{'date':'2026-11-20','distance_km':10,'time_minutes':55,'kind':'race'}}
    safety={'as_of':as_of,'target_date':'2026-11-28','decision':'easy_if_well',
            'suggested_easy_minutes':24,'missing':[],'flags':[],
            'sync':{'fresh':True,'status':'ok'},'metrics':{'longest_run_30d_km':5}}
    return profile,settings,safety,activities


def test_target_gap_and_alternative_are_quantified_without_changing_saved_goal():
    p,d,r,a=fixture()
    g=build_goal_guidance(p,'running',d,r,a)
    assert g['priorities'][0]['title'].startswith('1.')
    assert g['gap']['seconds_per_km']==30
    assert g['gap']['time_reduction_percent']==9.1
    assert '55' in g['alternative_goal']
    assert p['goal']=='10公里50分钟'
    assert len(g['week_plan'])==7
    assert sum(x.get('minutes',0) for x in g['week_plan'])<=120
    assert all(x.get('kind')!='quality' for x in g['week_plan'])
    assert all(s['url'] and s['checked_on']=='2026-11-27' for s in g['sources'])


def test_overload_keeps_original_candidate_visible_and_supplies_reduced_plan():
    p,d,r,a=fixture()
    r['distance_comparison']={'planned_km':12,'observed_longest_km':5}
    r['flags']=[{'code':'single_run_jump','reason':'距离激增'}]
    g=build_goal_guidance(p,'running',d,r,a)
    assert g['load_status']=='overload_warning'
    assert '12' in g['original_plan'] and '超负荷' in g['original_plan']
    assert any(x.get('minutes',0)>0 for x in g['week_plan'])
    assert all(x.get('distance_high_km',0)<=5 for x in g['week_plan'])


@pytest.mark.parametrize('reason',['avoid_running','recovery','insufficient_data'])
def test_stop_and_missing_states_never_emit_running_dose(reason):
    p,d,r,a=fixture();r['decision']=reason
    g=build_goal_guidance(p,'running',d,r,a)
    assert all(x.get('minutes',0)==0 for x in g['week_plan'])
    assert '50' in g['original_goal']


def test_benchmark_is_not_inferred_from_activity_average_or_stale_result():
    p,d,r,a=fixture();d['running_benchmark']['date']='2026-08-01'
    g=build_goal_guidance(p,'running',d,r,a)
    assert g['gap'] is None
    assert '过期' in g['benchmark_note']
    d['running_benchmark']['date']='2026-11-29'
    assert build_goal_guidance(p,'running',d,r,a)['gap'] is None


def test_different_distance_is_not_extrapolated_as_proven_current_ability():
    p,d,r,a=fixture();d['running_benchmark']['distance_km']=5
    g=build_goal_guidance(p,'running',d,r,a)
    assert g['gap'] is None
    assert '不同距离' in g['benchmark_note']


def test_race_week_does_not_schedule_normal_training_after_race():
    p,d,r,a=fixture()
    d['race_plan']={'enabled':True,'sport':'running','date':'2026-11-30','distance_km':10,'goal_minutes':50}
    g=build_goal_guidance(p,'running',d,r,a)
    assert all(x.get('minutes',0)==0 for x in g['week_plan'] if x['date']>='2026-11-30')


def test_cross_training_never_receives_a_running_schedule():
    p,d,r,a=fixture()
    g=build_goal_guidance(p,'cycling',d,r,a)
    assert g['week_plan']==[]
    assert '不换算' in g['alternative_goal']


@pytest.mark.parametrize('value',[{'date':'2026-02-30','distance_km':10,'time_minutes':50,'kind':'race'},
    {'date':'2026-11-20','distance_km':10,'time_minutes':float('nan'),'kind':'race'},
    {'date':'2026-11-20','distance_km':10,'time_minutes':50,'kind':'easy_run'}])
def test_invalid_benchmark_rejected(value):
    with pytest.raises(ValueError): validate_benchmark(value)


def test_report_shows_priority_order_plan_warning_and_references_safely():
    from garmin_local.report_ui import render_dashboard
    p,d,r,a=fixture()
    p['goal']='10公里50分钟 <img src=x onerror=alert(1)>'
    r['distance_comparison']={'planned_km':12}
    g=build_goal_guidance(p,'running',d,r,a)
    html=render_dashboard({**r,'goal':p['goal'],'goal_guidance':g})
    assert html.index('1. 以当前状态')<html.index('7日条件性训练安排')<html.index('2. 更合理')
    assert '超负荷警示' in html
    assert '39888556' in html and '42171506' in html
    assert '<img src=x' not in html


def test_daily_workflow_saves_the_same_two_priorities_in_html_and_markdown(tmp_path):
    from garmin_local.athlete_profile import save_profile
    from garmin_local.training import TrainingWorkflow
    from pathlib import Path
    save_profile(tmp_path,'running','10公里50分钟')
    r=TrainingWorkflow(None,tmp_path).assess_session('running',sync_first=False,research_refresh=False)
    assert len(r['goal_guidance']['priorities'])==2
    for key in ('report_html','report_markdown'):
        text=Path(r[key]).read_text(encoding='utf-8')
        assert '1. 以当前状态' in text and '2. 更合理' in text
        assert '7日条件性训练安排' in text


def test_missing_symptoms_or_no_recent_training_never_assumes_a_full_week():
    p,d,r,a=fixture();r['missing']=['subjective_check']
    assert all(x.get('minutes',0)==0 for x in build_goal_guidance(p,'running',d,r,a)['week_plan'])
    r['missing']=[]
    a=[x for x in a if x['startTimeLocal']<'2026-11-21']
    assert all(x.get('minutes',0)==0 for x in build_goal_guidance(p,'running',d,r,a)['week_plan'])
