"""Persistent date-keyed history, separate from the short-lived request cache."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone


class HistoryStore:
    def __init__(self, path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS records (kind TEXT, id TEXT, day TEXT, data TEXT, fetched TEXT, PRIMARY KEY(kind,id))')
            db.execute('CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY, completed TEXT, report TEXT)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        try:
            with db:
                yield db
        finally:
            db.close()

    def put(self, kind, rows, fetched):
        self.replace_range(kind, rows, fetched=fetched)

    def replace_range(self, kind, rows, start=None, end=None, fetched=None):
        values = []
        for row in rows:
            day = row.get('calendarDate') if kind != 'activities' else str(row.get('startTimeLocal', ''))[:10]
            identity = str(row.get('activityId', '')) if kind == 'activities' else day
            if not day or not identity:
                raise ValueError('Missing Garmin record identity')
            values.append((kind, identity, day, json.dumps(row, ensure_ascii=False), fetched))
        with self.connect() as db:
            if start is not None and end is not None:
                db.execute('DELETE FROM records WHERE kind=? AND day>=? AND day<=?',(kind,start,end))
            db.executemany('INSERT OR REPLACE INTO records VALUES (?,?,?,?,?)', values)

    def load(self, start_date, end_date):
        result = {k: [] for k in ('daily_summaries','sleep_summaries','hrv_summaries','steps','stress','body_battery','activities')}
        with self.connect() as db:
            for kind, data in db.execute('SELECT kind,data FROM records WHERE day>=? AND day<=? ORDER BY day', (start_date, end_date)):
                result.setdefault(kind, []).append(json.loads(data))
        return result

    def finish(self, report):
        with self.connect() as db:
            db.execute('INSERT INTO runs(completed,report) VALUES (?,?)',
                       (datetime.now(timezone.utc).isoformat(), json.dumps(report)))

    def last_complete(self):
        with self.connect() as db:
            rows = db.execute('SELECT report FROM runs ORDER BY id DESC').fetchall()
        return next((r for (raw,) in rows if (r := json.loads(raw))['status'] == 'ok'), None)

    def latest(self):
        with self.connect() as db:
            row = db.execute('SELECT report FROM runs ORDER BY id DESC LIMIT 1').fetchone()
        return json.loads(row[0]) if row else None
