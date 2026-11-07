import asyncio
import json
import os
import sys
from pathlib import Path
import pytest


def test_first_welcome_has_both_languages_and_no_implicit_choice():
    from garmin_assistant.onboarding import welcome
    from garmin_assistant.config import load_settings
    r=welcome(load_settings())
    assert r['language_selection_required']
    assert '欢迎首次使用佳明助手' in r['message']
    assert 'Welcome to Garmin Assistant' in r['message']
    assert [o['language'] for o in r['choices']]==['zh','en']


def test_language_saved_without_overwriting_goal_or_timezone():
    from garmin_assistant.config import load_settings,save_settings
    save_settings(load_settings(),timezone='Asia/Dubai',goal_distance_km=5,language='en')
    s=load_settings()
    assert s.language=='en' and s.timezone=='Asia/Dubai' and s.goal_distance_km==5


def test_english_menu_preserves_core_ids_and_custom_text():
    from garmin_assistant.onboarding import localize_result
    from garmin_assistant.menu import core_menu
    r=localize_result({'function_menu':core_menu()+[{'id':100,'command':'我的功能','description':'用户内容'}]},'en')
    assert r['function_menu'][0]['command']=='Sync data'
    assert [x['id'] for x in r['function_menu'][:4]]==list(range(1,5))
    assert r['function_menu'][-1]['command']=='我的功能'


def test_invalid_language_is_not_silently_saved():
    from garmin_assistant.config import load_settings,save_settings
    with pytest.raises(ValueError):save_settings(load_settings(),language='other')


def test_cli_switch_uses_the_new_language():
    import subprocess
    from garmin_assistant.config import load_settings,save_settings
    save_settings(load_settings(),language='zh')
    output=subprocess.check_output([sys.executable,'-m','garmin_assistant','language','en'],text=True,encoding='utf-8')
    r=json.loads(output)
    assert r['language']=='en' and r['function_menu'][0]['command']=='Sync data'
    assert load_settings().language=='en'


def test_interactive_auth_shows_bilingual_welcome_and_saves_explicit_choice(monkeypatch,capsys):
    import builtins
    import garmin_assistant.cli as cli
    from garmin_assistant.config import load_settings
    monkeypatch.setattr(cli.getpass,'getpass',lambda prompt:'dummy-local-test-key')
    monkeypatch.setattr(sys.stdin,'isatty',lambda:True)
    monkeypatch.setattr(builtins,'input',lambda prompt:'2')
    monkeypatch.setattr(sys,'argv',['garmin-assistant','auth'])
    cli.main()
    text=capsys.readouterr().out
    assert '欢迎首次使用佳明助手' in text and 'Welcome to Garmin Assistant' in text
    assert 'dummy-local-test-key' not in text
    assert load_settings().language=='en'


def test_english_core_names_cannot_be_overridden(tmp_path):
    from garmin_assistant.menu import MenuStore
    with pytest.raises(ValueError):MenuStore(tmp_path/'menu.json').add('sync data','override')


def test_english_localization_preserves_urgent_advice_and_raw_data():
    from garmin_assistant.readiness import assess
    from garmin_assistant.onboarding import localize_result
    r=assess({},'2026-10-28',subjective={'chest_pain':True})
    r['data']={'garminLabel':'原始字段'}
    result=localize_result(r,'en')
    assert 'Chest pain' in result['recommendation'] and 'emergency' in result['recommendation']
    assert result['data']=={'garminLabel':'原始字段'}


def test_english_report_is_saved_in_selected_language(tmp_path):
    from garmin_assistant.config import load_settings,save_settings
    from garmin_assistant.training import TrainingWorkflow
    settings=save_settings(load_settings(),language='en')
    r=TrainingWorkflow(None,settings.data_dir,settings=settings).tomorrow(as_of='2026-10-28',sync_first=False,research_refresh=False)
    text=Path(r['report_markdown']).read_text(encoding='utf-8')
    assert 'Running advice' in text and '## Function menu' in text
    assert r['function_menu'][0]['command']=='Sync data'


def test_live_doctor_does_not_read_health_before_language_choice(monkeypatch,capsys):
    from garmin_assistant.cli import main
    from garmin_assistant.service import GarminService
    def forbidden(*args,**kwargs):raise AssertionError('Health query before language choice')
    monkeypatch.setattr(GarminService,'query',forbidden)
    monkeypatch.setattr(sys,'argv',['garmin-assistant','doctor','--live'])
    main()
    r=json.loads(capsys.readouterr().out)
    assert r['onboarding']['language_selection_required']
    assert r['garmin_status']=='not_checked'


def test_cli_menu_asks_for_language_before_numbered_core_actions(monkeypatch,capsys):
    from garmin_assistant.cli import main
    monkeypatch.setattr(sys,'argv',['garmin-assistant','menu'])
    main()
    r=json.loads(capsys.readouterr().out)
    assert r['language_selection_required'] and 'function_menu' not in r


def test_mcp_onboarding_blocks_health_read_then_returns_english_menu():
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    async def run():
        config=StdioServerParameters(command=sys.executable,args=['-m','garmin_assistant','serve'],env=dict(os.environ))
        async with stdio_client(config) as streams:
            async with ClientSession(*streams) as session:
                init=await session.initialize()
                assert 'garmin_welcome' in init.instructions
                assert {'garmin_training_status','garmin_recovery_status','garmin_plan_tomorrow','garmin_assess_tomorrow'} <= {
                    tool.name for tool in (await session.list_tools()).tools}
                async def call(name,args):
                    r=await session.call_tool(name,args)
                    assert not r.isError
                    return r.structuredContent or json.loads(r.content[0].text)
                initial=await call('garmin_daily_summary',{})
                assert initial['language_selection_required']
                assert 'data' not in initial
                selected=await call('garmin_set_language',{'language':'en'})
                assert selected['language']=='en'
                menu=await call('garmin_function_menu',{})
                assert menu['function_menu'][0]['command']=='Sync data'
                assert not menu['language_selection_required']
    asyncio.run(run())
