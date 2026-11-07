import tempfile
from pathlib import Path
import pytest


def test_hidden_core_is_restored_and_custom_functions_survive():
    from garmin_assistant.menu import MenuStore
    with tempfile.TemporaryDirectory() as tmp:
        store=MenuStore(Path(tmp)/'preferences.json')
        initial=store.view()['function_menu']
        assert [x['id'] for x in initial]==list(range(1,5))
        extension=store.add('我的周总结','查询最近七天记录，再总结跑量变化。')
        assert extension['id']>=100
        store.hide(list(range(1,8)))
        assert [x['id'] for x in MenuStore(store.path).view()['function_menu']]==[extension['id']]
        restored=MenuStore(store.path).restore()
        assert [x['id'] for x in restored['function_menu']]==list(range(1,8))
        assert len(MenuStore(store.path).view()['function_menu'])==5


@pytest.mark.parametrize('name',['同步数据','显示原有功能菜单','garmin_sync_data'])
def test_extension_cannot_override_reserved_core(name,tmp_path):
    from garmin_assistant.menu import MenuStore
    with pytest.raises(ValueError):MenuStore(tmp_path/'menu.json').add(name,'some workflow')


def test_custom_ids_stay_stable_and_cannot_delete_core(tmp_path):
    from garmin_assistant.menu import MenuStore
    store=MenuStore(tmp_path/'menu.json')
    first=store.add('A','Do A');second=store.add('B','Do B')
    store.remove(first['id'])
    assert store.add('C','Do C')['id']>second['id']
    with pytest.raises(ValueError):store.remove(1)


def test_config_is_outside_checkout_and_overrides_are_validated(tmp_path,monkeypatch):
    from garmin_assistant.config import load_settings, save_settings
    monkeypatch.setenv('GARMIN_ASSISTANT_HOME',str(tmp_path/'private'))
    a=load_settings()
    save_settings(a,timezone='Asia/Shanghai',goal_distance_km=5,goal_minutes=30)
    b=load_settings()
    assert b.timezone=='Asia/Shanghai' and b.goal_distance_km==5
    assert b.data_dir==tmp_path/'private'
    with pytest.raises(ValueError):save_settings(b,timezone='Invalid/Zone')


def test_custom_goal_changes_report_not_core_decision():
    from garmin_assistant.readiness import assess
    a=assess({},'2026-10-28')
    b=assess({},'2026-10-28',goal={'distance_km':5,'minutes':30})
    assert a['decision']==b['decision']
    assert b['goal']['distance_km']==5
    assert b['goal']['target']=='under 30 minutes'
