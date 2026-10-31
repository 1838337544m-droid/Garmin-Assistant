import concurrent.futures
import json
import os
import subprocess
import sys
from pathlib import Path


def test_client_config_preserves_nonsecret_paths(tmp_path,monkeypatch):
    monkeypatch.setenv('GARMIN_ASSISTANT_KEY_FILE',str(tmp_path/'outside-key'))
    result=subprocess.check_output([sys.executable,'-m','garmin_assistant','client-config'],text=True,encoding='utf-8')
    entry=json.loads(result)['mcpServers']['garmin-assistant']
    assert Path(entry['env']['GARMIN_ASSISTANT_HOME']).resolve()==Path(os.environ['GARMIN_ASSISTANT_HOME']).resolve()
    assert entry['env']['GARMIN_ASSISTANT_KEY_FILE']==str(tmp_path/'outside-key')
    assert 'GARMIN_PERSONAL_API_KEY' not in entry['env']


def test_relative_key_path_becomes_absolute_for_gui_client(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('GARMIN_ASSISTANT_KEY_FILE','keys/personal-key')
    result=subprocess.check_output([sys.executable,'-m','garmin_assistant','client-config'],text=True,encoding='utf-8')
    path=json.loads(result)['mcpServers']['garmin-assistant']['env']['GARMIN_ASSISTANT_KEY_FILE']
    assert Path(path).is_absolute()
    assert Path(path)==(tmp_path/'keys/personal-key').resolve()


def test_cli_unicode_output_works_in_non_utf8_terminal():
    env=dict(os.environ);env['PYTHONIOENCODING']='ascii'
    result=subprocess.check_output([sys.executable,'-m','garmin_assistant','init'],env=env,text=True,encoding='utf-8')
    assert json.loads(result)['title']=='Garmin 助手（API）版本'


def test_concurrent_custom_additions_do_not_lose_ids(tmp_path):
    from garmin_assistant.menu import MenuStore
    path=tmp_path/'preferences.json'
    code='from pathlib import Path; from garmin_assistant.menu import MenuStore; import sys; MenuStore(Path(sys.argv[1])).add(sys.argv[2],"workflow")'
    def add(i):subprocess.check_call([sys.executable,'-c',code,str(path),f'workflow-{i}'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(add,range(16)))
    rows=[r for r in MenuStore(path).view()['function_menu'] if r['id']>=100]
    assert len(rows)==16
    assert sorted(r['id'] for r in rows)==list(range(100,116))


def test_server_status_reloads_timezone_without_mixing_settings():
    code='''
from garmin_assistant.config import load_settings,save_settings
from garmin_assistant.server import garmin_status
save_settings(load_settings(),timezone='Asia/Shanghai')
assert garmin_status()['default_timezone']=='Asia/Shanghai'
'''
    subprocess.check_call([sys.executable,'-c',code])


def test_sync_menu_payload_is_not_shared(tmp_path):
    from garmin_assistant.sync import SyncManager
    from garmin_assistant.history import HistoryStore
    class Empty:
        def query(self,kind,**kwargs):
            data={'data':[]} if kind=='daily_summaries' else {'hrvSummaries':[]} if kind=='hrv_summaries' else []
            return {'status':'no_data','data':data,'fetched_at':'now'}
    manager=SyncManager(Empty(),HistoryStore(tmp_path/'history.sqlite3'))
    first=manager.run(days=1,end_date='2026-10-28')
    try:
        first['function_menu'][0]['command']='mutated'
        assert manager.run(days=1,end_date='2026-10-28')['function_menu'][0]['command']=='同步数据'
    finally:first['function_menu'][0]['command']='同步数据'
