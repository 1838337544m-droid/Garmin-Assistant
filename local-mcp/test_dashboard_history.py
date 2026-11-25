import json
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from dashboard import make_server
from dashboard_history import coverage,load_latest,save_latest


def report():
    return {'as_of':'2020-01-01','target_date':'2020-01-02','generated_at':'2020-01-01T12:00:00+00:00',
            'session_sport':'cycling','primary_sport':'running','goal':'测试目标',
            'prescription':{'session_action':'测试建议'},'metrics':{},'flags':[],
            'missing':['current_sleep'],'sync':{'fresh':False,'status':'partial'}}


def test_coverage_distinguishes_missing_stale_and_complete():
    r=report();c=coverage(r,datetime(2026,11,25,tzinfo=timezone.utc))
    assert not c['is_current'] and c['data_state']=='partial'
    assert c['missing']==['缺少最新睡眠记录']
    r.update(as_of='2026-11-25',missing=[],sync={'fresh':True,'status':'ok'})
    assert coverage(r,datetime(2026,11,25,tzinfo=timezone.utc))['data_state']=='complete'


@contextmanager
def serve(workflow,folder):
    server,url=make_server(workflow,folder)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    root=url.split('/?')[0];headers={'X-Dashboard-Key':url.split('key=')[1],'Content-Type':'application/json'}
    try: yield root,headers
    finally: server.shutdown();server.server_close();thread.join()


def test_reopen_restores_report_without_syncing(tmp_path):
    save_latest(tmp_path,report())
    class NoNetwork:
        def assess_session(self,*args,**kwargs): raise AssertionError('Unexpected analysis')
    with serve(NoNetwork(),tmp_path) as (root,headers):
        response=json.load(urlopen(Request(root+'/latest',headers=headers)))
        assert response['has_result'] and not response['coverage']['is_current']
        assert '测试建议' in response['html']


def test_failed_update_keeps_last_result(tmp_path):
    save_latest(tmp_path,report())
    class Offline:
        def assess_session(self,*args,**kwargs): raise OSError('offline')
    with serve(Offline(),tmp_path) as (root,headers):
        data=json.dumps({'primary_sport':'running','session_sport':'cycling','goal':'测试目标'}).encode()
        with pytest.raises(HTTPError) as failed:
            urlopen(Request(root+'/analyze',data=data,headers=headers))
        assert failed.value.code==500
        assert json.load(urlopen(Request(root+'/progress',headers=headers)))['phase']=='failed'
        assert load_latest(tmp_path)['target_date']=='2020-01-02'


def test_empty_or_corrupt_history_does_not_fake_result(tmp_path):
    assert load_latest(tmp_path) is None
    (tmp_path/'latest-dashboard.json').write_text('broken',encoding='utf-8')
    assert load_latest(tmp_path) is None


def test_previous_session_report_is_discovered(tmp_path):
    reports=tmp_path/'reports';reports.mkdir()
    (reports/'session_previous.json').write_text(json.dumps(report()),encoding='utf-8')
    assert load_latest(tmp_path,reports)['target_date']=='2020-01-02'
