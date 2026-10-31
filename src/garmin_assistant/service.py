"""Validated read-through cache; provider failures never expose response bodies."""
import json
import sqlite3
import time
from contextlib import contextmanager
from datetime import date as Date, datetime, timezone


KINDS = {'summary', 'sleep', 'heart_rate', 'hrv', 'steps', 'stress',
         'body_battery', 'activities', 'activity', 'daily_summaries', 'sleep_summaries', 'hrv_summaries'}


def timestamp(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def validate(kind, params):
    if kind not in KINDS:
        raise ValueError('Unsupported data type')
    p = dict(params)
    for key in ('date', 'start_date', 'end_date'):
        if p.get(key) is not None:
            try:
                value = Date.fromisoformat(p[key])
                if value.isoformat() != p[key]:
                    raise ValueError()
            except (ValueError, TypeError):
                raise ValueError('Dates must be valid YYYY-MM-DD strings') from None
    if kind in {'summary', 'sleep', 'heart_rate', 'hrv'} and not p.get('date'):
        raise ValueError('date is required')
    if kind in {'steps', 'stress', 'body_battery', 'daily_summaries', 'sleep_summaries', 'hrv_summaries'}:
        if not p.get('start_date') or not p.get('end_date'):
            raise ValueError('start_date and end_date are required')
    if p.get('start_date') and p.get('end_date'):
        days = (Date.fromisoformat(p['end_date']) - Date.fromisoformat(p['start_date'])).days + 1
        maximum = 28 if kind in {'steps', 'stress', 'sleep_summaries', 'hrv_summaries'} else 31 if kind == 'body_battery' else 366
        if not 1 <= days <= maximum:
            raise ValueError(f'Date range must contain 1 to {maximum} days; split longer queries')
    if kind == 'activities':
        p.setdefault('start', 0)
        p.setdefault('limit', 20)
        if type(p['start']) is not int or p['start'] < 0:
            raise ValueError('start must be a nonnegative integer')
        if type(p['limit']) is not int or not 1 <= p['limit'] <= 100:
            raise ValueError('limit must be 1 to 100; paginate with start')
    if kind == 'activity':
        if type(p.get('activity_id')) is not int or p['activity_id'] <= 0:
            raise ValueError('activity_id must be a positive integer')
    return p


class GarminService:
    def __init__(self, db_path, fetch, clock=time.time, ttl=900):
        self.db_path, self.fetch, self.clock, self.ttl = db_path, fetch, clock, ttl
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, kind TEXT NOT NULL, params TEXT NOT NULL, data TEXT NOT NULL, fetched REAL NOT NULL)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=30)
        try:
            with db:
                yield db
        finally:
            db.close()

    def query(self, kind, refresh=False, **params):
        params = validate(kind, params)
        encoded = json.dumps(params, sort_keys=True)
        key = kind + ':' + encoded
        now = self.clock()
        with self.connect() as db:
            row = db.execute('SELECT data, fetched FROM cache WHERE key=?', (key,)).fetchone()
        source = 'local_cache'
        stale = False
        error = None
        if refresh or row is None or not 0 <= now - row[1] < self.ttl:
            try:
                data = self.fetch(kind, params)
                raw = json.dumps(data, ensure_ascii=False)
                with self.connect() as db:
                    db.execute('INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?, ?)',
                               (key, kind, encoded, raw, now))
                row = (raw, now)
                source = 'garmin_api'
            except Exception as exc:
                code = getattr(exc, 'status_code', None)
                if code is None:
                    code = getattr(getattr(exc, 'response', None), 'status_code', None)
                error = ('authentication_failed: renew your personal API key with garmin-assistant auth' if code in (401, 403)
                         else 'rate_limited: retry later' if code == 429
                         else 'garmin_fetch_failed: check network, API key, or Garmin availability')
                stale = row is not None
        data = json.loads(row[0]) if row else None
        status = ('stale' if stale else 'error' if error else
                  'no_data' if data in (None, [], {}) else 'ok')
        return {'status': status, 'source': source if row else None,
                'data_type': kind, 'query': params,
                'fetched_at': timestamp(row[1]) if row else None,
                'cache_age_seconds': max(0, int(now - row[1])) if row else None,
                'date_policy': 'Dates are Garmin calendar dates; timestamps and units in data are unchanged.',
                'error': error, 'data': data}

    def status(self):
        with self.connect() as db:
            count, last = db.execute('SELECT COUNT(*), MAX(fetched) FROM cache').fetchone()
            coverage = [{'data_type': row[0], 'queries': row[1]}
                        for row in db.execute('SELECT kind, COUNT(*) FROM cache GROUP BY kind')]
        return {'cached_queries': count, 'last_successful_fetch': timestamp(last) if last else None,
                'cache_ttl_seconds': self.ttl, 'coverage': coverage,
                'sync_mode': 'on_demand', 'provider': 'Garmin official Personal API'}
