from garmin_assistant.menu import core_menu
from garmin_assistant.onboarding import welcome
from garmin_assistant.config import Settings


def test_menu_routes_dashboard_to_browser_tool():
    entry=next(x for x in core_menu() if x['id']==5)
    assert entry['tool']=='garmin_open_training_dashboard'
    assert '网页' in entry['command']


def test_returning_user_sees_dashboard_instructions(tmp_path):
    r=welcome(Settings(tmp_path,language='zh'))
    assert '打开训练日报' in r['message']
    assert '生成分析' in r['message']
