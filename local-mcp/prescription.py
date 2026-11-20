# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Conservative, explainable multisport next-day prescription templates."""

SESSION_SPORTS = {'running', 'cycling', 'swimming', 'climbing', 'other'}
ACTIVITY_KEYS = {
    'running': 'running', 'run': 'running', 'virtual_run': 'running',
    'cycling': 'cycling', 'road_biking': 'cycling', 'indoor_cycling': 'cycling',
    'swimming': 'swimming', 'pool_swimming': 'swimming', 'open_water_swimming': 'swimming',
    'rock_climbing': 'climbing', 'climbing': 'climbing',
}


def classify_activity(activity):
    key = (activity.get('activityType') or {}).get('typeKey', '')
    return ACTIVITY_KEYS.get(key, 'unknown')


def build_prescription(profile, session_sport, safety, activities, session_intent=None, swimming_safety=None):
    if session_sport not in SESSION_SPORTS:
        raise ValueError('unsupported session_sport')
    blocked = safety.get('decision') in {'avoid_running', 'recovery', 'insufficient_data'}
    primary = profile['primary_sport']
    if blocked:
        return {'prescription_status': 'avoid' if safety.get('decision') == 'avoid_running' else 'recover',
                'session_action': safety.get('recommendation','停止专项训练并复评。') if safety.get('decision')=='avoid_running' else '明天优先恢复或停止专项训练。',
                'capacity_focus': '保护恢复与安全边界。', 'capacity_summary': '共同安全门优先于专项训练。',
                'dose': '不安排专项强度。', 'downgrade_rule': '任何不适均停止并复评。',
                'evidence_boundary': '恢复信号不能替代医疗评估。'}
    if session_sport == 'swimming' and not all((swimming_safety or {}).get(k) is False for k in ('shoulder_pain', 'swimming_alone')):
        return {'prescription_status': 'recover', 'session_action': '先确认肩痛与是否独自下水，再决定是否游泳。',
                'capacity_focus': '保护肩部与水上安全。', 'capacity_summary': '游泳专项信息未完整确认。',
                'dose': '不生成游泳专项剂量。', 'downgrade_rule': '未确认前改为陆上恢复。',
                'evidence_boundary': '肩痛或独自下水信息未知或存在风险，暂不提供游泳训练。'}
    if session_sport == 'other':
        return {'prescription_status': 'easy', 'session_action': '选择舒适、低风险的恢复活动。',
                'capacity_focus': '维持一般活动与恢复。', 'capacity_summary': '其他项目不生成专项规则。',
                'dose': 'RPE 2–3/10。', 'downgrade_rule': '不适即停止。', 'evidence_boundary': '缺少该项目的专项规则与数据。'}
    action = {'running': '轻松跑，保持完整交谈。', 'cycling': '轻松转腿骑行，保持完整交谈。',
              'swimming': '轻松技术游，不追求速度。', 'climbing': '低强度技术攀爬，避免极限抓点。'}[session_sport]
    cross = session_sport != primary
    summary = (f'{session_sport} 作为交叉训练，需结合长期{primary}目标确认作用，不换算专项负荷。' if cross
               else f'今天以{primary}项目维持基础能力。')
    boundary = ('Garmin 数据不能确认指力、肌腱或皮肤准备度。' if session_sport == 'climbing'
                else '可穿戴数据不能替代症状检查或专项技术判断。')
    focus={'running':'维持有氧基础与跑步组织耐受。','cycling':'维持低强度有氧与踏频控制。',
           'swimming':'维持水中技术与呼吸节律。','climbing':'练习动作技术，保护指部和上肢组织。'}[session_sport]
    return {'prescription_status': 'recover' if session_intent=='recovery' else 'easy',
            'session_action': action, 'capacity_focus': focus,
            'same_sport_sessions':sum(classify_activity(a)==session_sport for a in activities),
            'capacity_summary': summary, 'dose': 'RPE 2–3/10；不安排专项高强度。',
            'downgrade_rule': '热身或过程中出现疼痛、异常疲劳或不适时停止并改为恢复。',
            'evidence_boundary': boundary}
