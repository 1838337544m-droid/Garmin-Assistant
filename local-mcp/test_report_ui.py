from report_ui import render_dashboard


def test_dashboard_escapes_text_and_filters_unsafe_source_links():
    html=render_dashboard({'goal':'<script>alert(1)</script>', 'research':{'reviewed_sources':[
        {'url':'javascript:alert(1)','title':'unsafe'}]}})
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html
    assert 'javascript:' not in html
    assert '未提供' in html


def test_multisport_workflow_saves_html(tmp_path):
    from athlete_profile import save_profile
    from training import TrainingWorkflow
    from pathlib import Path
    save_profile(tmp_path,'cycling','基础耐力')
    result=TrainingWorkflow(None,tmp_path).assess_session('cycling',sync_first=False,research_refresh=False)
    html=Path(result['report_html']).read_text(encoding='utf-8')
    assert '能力处方总结' in html
    assert '基础耐力' in html
    assert 'id="sport"' in html
