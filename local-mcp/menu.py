# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""User-facing actions supported by this local MCP installation."""
FUNCTION_MENU = [
    {'command':'打开训练日报（网页）','description':'在浏览器选运动、填身体感受、点击生成分析，结果直接显示。','tool':'garmin_open_training_dashboard'},
    {'command':'设置长期运动主项与目标','description':'本地保存跑步、骑车、游泳或攀岩偏好；不修改 Garmin 数据。','tool':'garmin_get_athlete_profile / garmin_set_athlete_profile'},
    {'command':'生成明日专项处方','description':'按长期主项和本次运动给出能力总结、恢复边界与明早复评提示。','tool':'garmin_assess_session'},
    {'command':'同步数据','description':'补齐上次同步后至今的数据，重查重叠日期并报告缺失项。','tool':'garmin_sync_data'},
    {'command':'分析明天是否适合运动','description':'先同步，再结合恢复、近期跑步和文献，给出面向 10 公里 60 分钟目标的预建议。','tool':'garmin_assess_tomorrow'},
    {'command':'查看近期运动或某次详情','description':'按日期查询跑步等运动，或查看指定运动详情。','tool':'garmin_activities / garmin_activity_detail'},
    {'command':'查看睡眠、心率或 HRV','description':'读取指定日期的健康数据。','tool':'garmin_sleep / garmin_heart_rate / garmin_hrv'},
    {'command':'查看区间步数、压力和 Body Battery','description':'分段读取日期区间的数据，供对比分析。','tool':'garmin_range'},
    {'command':'更新训练和康复文献','description':'立即检索近期收录论文，返回出处及待评估状态。','tool':'garmin_update_research'},
    {'command':'查看同步状态或功能菜单','description':'查看缓存状态，或列出当前实际可用功能。','tool':'garmin_status / garmin_function_menu'},
]
