import pytest
from distance_context import distance_context


@pytest.mark.parametrize('planned,observed,synced',[(14,10,True),(14,10,False),(14,None,False),(None,10,True)])
def test_distance_display_preserves_missing_and_coverage(planned,observed,synced):
    r=distance_context(planned,observed,'2026-11-21',synced)
    assert r['planned_km']==planned and r['observed_longest_km']==observed
    assert r['comparable']==(planned is not None and observed is not None)
    assert r['window_start']=='2026-10-23'
    if not synced: assert '仅覆盖已有记录' in r['display_zh']
    if observed is None: assert '无法比较' in r['display_zh']


def test_distance_context_does_not_change_assessment(tmp_path):
    from training import TrainingWorkflow
    from readiness import assess
    from pathlib import Path
    workflow=TrainingWorkflow(None,tmp_path)
    from sync import local_today
    day=local_today()
    r=workflow.tomorrow(as_of=day,planned_km=14,sync_first=False,research_refresh=False)
    original=assess({},day,planned_km=14,sync_ok=False)
    assert r['decision']==original['decision']
    assert r['quality_session_eligible']==original['quality_session_eligible']
    assert '计划距离：14 km' in Path(r['report_markdown']).read_text(encoding='utf-8')
