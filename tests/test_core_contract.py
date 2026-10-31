from garmin_assistant.menu import CORE_FUNCTIONS, core_menu


def test_core_identifiers_and_tools_remain_backward_compatible():
    expected={1:'garmin_sync_data',2:'garmin_assess_tomorrow',3:'garmin_activities / garmin_activity_detail',
              4:'garmin_sleep / garmin_heart_rate / garmin_hrv',5:'garmin_range',6:'garmin_update_research',
              7:'garmin_status / garmin_function_menu'}
    assert {f.id:f.tool for f in CORE_FUNCTIONS}==expected


def test_core_menu_returns_detached_copies():
    edited=core_menu();edited[0]['command']='changed';edited.clear()
    assert core_menu()[0]['command']=='同步数据'
