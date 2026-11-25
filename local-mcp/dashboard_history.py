# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Offline last-result persistence and human-readable coverage metadata."""
import json
from datetime import datetime, timezone, timedelta
from research import atomic_json

MISSING_LABELS={
    'subjective_check':'身体感受尚未完整确认',
    'fresh_complete_sync':'本次完整同步未确认',
    'hrv_current_and_baseline':'近期 HRV 或个人参考不足',
    'current_sleep':'缺少最新睡眠记录',
    'resting_hr_baseline_or_recent':'静息心率或个人参考不足',
}


def coverage(result, now=None):
    now=now or datetime.now(timezone.utc)
    today=now.astimezone(timezone(timedelta(hours=4))).date().isoformat()
    sync=result.get('sync',{})
    missing=result.get('missing',[])
    return {'as_of':result.get('as_of'),'target_date':result.get('target_date'),
            'generated_at':result.get('generated_at'),
            'is_current':result.get('as_of')==today,
            'sync_status':sync.get('status','unknown'),
            'sync_complete':sync.get('fresh') is True and sync.get('status')=='ok',
            'missing':[MISSING_LABELS.get(item,item) for item in missing],
            'data_state':'complete' if sync.get('fresh') is True and sync.get('status')=='ok' and not missing else 'partial'}


def save_latest(folder,result):
    atomic_json(folder/'latest-dashboard.json',result)


def load_latest(folder,report_folder=None):
    path=folder/'latest-dashboard.json'
    # Migration: show the most recent existing session report before a new update.
    candidates=[path]
    if not path.exists() and report_folder and report_folder.exists():
        root=report_folder.resolve()
        candidates=sorted((p for p in report_folder.glob('session_*.json')
                           if p.resolve().parent==root),key=lambda p:p.stat().st_mtime,reverse=True)[:5]
    for path in candidates:
        try:
            if path.stat().st_size>8_000_000: continue
            value=json.loads(path.read_text(encoding='utf-8'))
            if (isinstance(value,dict) and isinstance(value.get('prescription'),dict)
                and isinstance(value.get('missing'),list) and isinstance(value.get('sync'),dict)
                and value.get('target_date') and value.get('as_of')):
                return value
        except (OSError,ValueError,TypeError):
            continue
    return None
