import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from garmin_assistant.config import load_settings
from garmin_assistant.setup import client_entry, connect_claude, connect_codex, configure


def test_claude_preserves_servers_backs_up_and_has_no_key(tmp_path):
    path=tmp_path/'中文 path'/'claude.json';path.parent.mkdir()
    original='{"mcpServers":{"other":{"command":"other"}},"theme":"dark"}'
    path.write_text(original,encoding='utf-8')
    settings=load_settings()
    backup=connect_claude(path,settings)
    data=json.loads(path.read_text(encoding='utf-8'))
    assert backup.read_text(encoding='utf-8')==original
    assert data['theme']=='dark' and data['mcpServers']['other']=={'command':'other'}
    assert data['mcpServers']['garmin-assistant']==client_entry(settings)
    assert 'GARMIN_PERSONAL_API_KEY' not in str(data)


def test_existing_garmin_requires_replacement_confirmation(tmp_path):
    path=tmp_path/'client.json'
    original='{"mcpServers":{"garmin-assistant":{"command":"old"}}}'
    path.write_text(original,encoding='utf-8')
    with pytest.raises(ValueError):connect_claude(path,load_settings())
    assert path.read_text(encoding='utf-8')==original
    connect_claude(path,load_settings(),replace=True)
    assert json.loads(path.read_text())['mcpServers']['garmin-assistant']['command']==sys.executable


@pytest.mark.parametrize('raw',['{broken','[]','{"mcpServers":[]}'])
def test_invalid_client_file_is_never_replaced(tmp_path,raw):
    path=tmp_path/'client.json';path.write_text(raw,encoding='utf-8')
    with pytest.raises(ValueError):connect_claude(path,load_settings())
    assert path.read_text(encoding='utf-8')==raw
    assert list(tmp_path.glob('*.bak'))==[]


def test_configure_preserves_key_and_rejects_invalid_input_before_writes():
    settings=load_settings()
    configured=configure(settings,'en','Asia/Dubai','10','60','test-only-key')
    assert configured.language=='en' and configured.key_file.read_text()=='test-only-key'
    configure(configured,'zh','Asia/Shanghai','10','60','')
    before=(settings.data_dir/'settings.json').read_bytes()
    with pytest.raises(ValueError):configure(configured,'en','Invalid/Zone','10','60','replacement')
    assert configured.key_file.read_text()=='test-only-key'
    assert (settings.data_dir/'settings.json').read_bytes()==before


def test_codex_backs_up_and_only_passes_nonsecret_paths(tmp_path,monkeypatch):
    home=tmp_path/'codex home';home.mkdir();path=home/'config.toml'
    path.write_text('model = "example"\n',encoding='utf-8')
    monkeypatch.setenv('CODEX_HOME',str(home))
    monkeypatch.setattr('garmin_assistant.setup.shutil.which',lambda name:'/fake/codex')
    calls=[]
    def run(argv,**kwargs):
        calls.append(argv);return subprocess.CompletedProcess(argv,0)
    monkeypatch.setattr('garmin_assistant.setup.subprocess.run',run)
    backup=connect_codex(load_settings())
    assert backup.read_text()=='model = "example"\n'
    assert calls[0][:4]==['/fake/codex','mcp','add','garmin-assistant']
    assert 'GARMIN_PERSONAL_API_KEY' not in str(calls)
    assert f'GARMIN_ASSISTANT_HOME={load_settings().data_dir}' in calls[0]


def test_codex_missing_or_failure_is_not_success(tmp_path,monkeypatch):
    monkeypatch.setenv('CODEX_HOME',str(tmp_path/'codex'))
    monkeypatch.setattr('garmin_assistant.setup.shutil.which',lambda name:None)
    with pytest.raises(ValueError):connect_codex(load_settings())
    monkeypatch.setattr('garmin_assistant.setup.shutil.which',lambda name:'/fake/codex')
    monkeypatch.setattr('garmin_assistant.setup.subprocess.run',lambda *a,**k:subprocess.CompletedProcess(a[0],1))
    with pytest.raises(ValueError):connect_codex(load_settings())


def test_codex_creates_selected_home_before_cli(tmp_path,monkeypatch):
    home=tmp_path/'new codex home'
    monkeypatch.setenv('CODEX_HOME',str(home))
    monkeypatch.setattr('garmin_assistant.setup.shutil.which',lambda name:'/fake/codex')
    def run(argv,**kwargs):
        assert home.is_dir()
        return subprocess.CompletedProcess(argv,0)
    monkeypatch.setattr('garmin_assistant.setup.subprocess.run',run)
    connect_codex(load_settings())


def test_claude_replacement_keeps_permissions_and_new_file_is_private(tmp_path,monkeypatch):
    path=tmp_path/'client.json';path.write_text('{}',encoding='utf-8');path.chmod(0o600)
    expected=stat.S_IMODE(path.stat().st_mode)
    modes=[];real_chmod=os.chmod
    def chmod(file,mode,*args,**kwargs):
        modes.append(mode);return real_chmod(file,mode,*args,**kwargs)
    monkeypatch.setattr('garmin_assistant.setup.os.chmod',chmod)
    connect_claude(path,load_settings())
    assert expected in modes
    modes.clear()
    connect_claude(tmp_path/'new.json',load_settings())
    assert 0o600 in modes
    if os.name!='nt':
        assert stat.S_IMODE(path.stat().st_mode)==expected
        assert stat.S_IMODE((tmp_path/'new.json').stat().st_mode)==0o600
