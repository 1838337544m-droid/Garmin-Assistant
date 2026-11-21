# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Display-only comparison; never changes training decisions."""
from datetime import date, timedelta


def distance_context(planned_km, observed_km, as_of, sync_ok):
    start=(date.fromisoformat(as_of)-timedelta(days=29)).isoformat()
    planned=f'{planned_km:g} km' if planned_km is not None else '未填写，无法比较'
    observed=f'{observed_km:g} km' if observed_km is not None else '缺失，无法比较'
    coverage='本次同步完成，仍仅代表 Garmin 已同步记录' if sync_ok else '本次完整同步未确认，仅覆盖已有记录'
    zh=(f'计划距离：{planned}；近30天已识别最长跑：{observed}。'
        f'历史窗口：{start} 至 {as_of}（今天尚未结束）；{coverage}。'
        '路线和强度尚未确认，距离差不能预测个人伤病概率或作为安全线。明早同步并复核是否保留计划距离。')
    en=(f'Planned distance: {planned_km if planned_km is not None else "not provided"} km; '
        f'longest recorded run in 30 days: {observed_km if observed_km is not None else "unavailable; cannot compare"} km. '
        f'Window: {start} to {as_of} (today incomplete). '
        +('Sync completed; Garmin records only. ' if sync_ok else 'Complete fresh sync unconfirmed; available records only. ')
        +'Route and intensity unconfirmed. Distance differences do not predict personal injury risk or establish a safety limit. Sync and reconsider the planned distance tomorrow morning.')
    return {'planned_km':planned_km,'observed_longest_km':observed_km,'window_start':start,
            'window_end':as_of,'fresh_complete_sync':bool(sync_ok),
            'comparable':planned_km is not None and observed_km is not None,
            'display_zh':zh,'display_en':en}
