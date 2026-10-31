"""Chunked official API synchronization, idempotent history and explicit partial runs."""
from datetime import date, datetime, timedelta, timezone
from .menu import core_menu


def local_today():
    from .config import local_today as configured_today
    return configured_today()


def unpack(kind, data):
    if isinstance(data, dict):
        key = 'data' if kind == 'daily_summaries' else 'hrvSummaries' if kind == 'hrv_summaries' else None
        if key is None or key not in data:
            raise ValueError('Unexpected Garmin response envelope')
        data = data[key]
    if data is None:
        return []
    if not isinstance(data, list) or any(not isinstance(r, dict) for r in data):
        raise ValueError('Unexpected Garmin response shape')
    if kind=='body_battery':
        return [{**row,'calendarDate':row.get('calendarDate') or row.get('date')} for row in data]
    return data


def validate_rows(kind, rows, start, end):
    validated=[]
    for row in rows:
        # Official sleep range responses include explicit no-sleep placeholders
        # with null date/duration and device/sleep-need metadata. They are gaps.
        if kind=='sleep_summaries' and 'calendarDate' in row and 'sleepTimeSeconds' in row and row['calendarDate'] is None and row['sleepTimeSeconds'] is None:
            continue
        raw=str(row.get('startTimeLocal',''))[:10] if kind=='activities' else row.get('calendarDate')
        try:parsed=date.fromisoformat(raw)
        except (ValueError,TypeError):raise ValueError('Malformed Garmin calendar date') from None
        if parsed.isoformat()!=raw or not start<=raw<=end:
            raise ValueError('Garmin record outside requested date range')
        if kind=='activities' and (type(row.get('activityId')) is not int or row['activityId']<=0):
            raise ValueError('Malformed activity ID')
        validated.append(row)
    return validated


class SyncManager:
    def __init__(self, service, store):
        self.service, self.store = service, store

    def run(self, days=93, end_date=None, full=False, current_date=None):
        if type(days) is not int or not 1 <= days <= 366:
            raise ValueError('days must be 1 to 366')
        current_date=current_date or local_today()
        end = date.fromisoformat(end_date or current_date)
        if end.isoformat() != (end_date or end.isoformat()) or end.isoformat() > current_date:
            raise ValueError('end_date must be a valid nonfuture YYYY-MM-DD')
        requested = end - timedelta(days=days-1)
        start = requested
        last = self.store.last_complete()
        if not full and last and last['requested_start'] <= requested.isoformat() and last['end_date'] <= end.isoformat():
            # Revisit the overlap AND every intervening date, even if the user
            # returns after more than the usual 93-day analysis window.
            start = date.fromisoformat(last['end_date']) - timedelta(days=7)
        previous_ids={r['activityId'] for r in self.store.load(start.isoformat(),end.isoformat())['activities']}
        previous_end=last['end_date'] if last else None
        gap_start=(date.fromisoformat(previous_end)+timedelta(days=1)) if previous_end else requested
        gap_days=max(0,(end-gap_start).days+1)
        report = {'status':'ok','requested_start':requested.isoformat(),'start_date':start.isoformat(),
                  'end_date':end.isoformat(),'mode':'full' if start == requested else 'incremental',
                  'fetched_at':datetime.now(timezone.utc).isoformat(),'errors':[],'requests':0,
                  'interval':{'previous_sync_end':previous_end,'gap_start':gap_start.isoformat() if gap_days else None,
                              'gap_end':end.isoformat() if gap_days else None,'gap_days':gap_days},
                  'function_menu':core_menu()}
        try:
            for kind in ('daily_summaries','sleep_summaries','hrv_summaries','steps','stress','body_battery'):
                current = start
                while current <= end:
                    until = min(current + timedelta(days=27), end)
                    result = self.service.query(kind, refresh=True, start_date=current.isoformat(), end_date=until.isoformat())
                    report['requests'] += 1
                    if result['status'] not in ('ok','no_data'):
                        report['errors'].append({'dataset':kind,'start_date':current.isoformat(),'error':result.get('error')})
                        raise RuntimeError('Sync interrupted')
                    rows = validate_rows(kind, unpack(kind,result['data']),current.isoformat(),until.isoformat())
                    self.store.replace_range(kind, rows, current.isoformat(), until.isoformat(), result.get('fetched_at'))
                    current = until + timedelta(days=1)
            activity_start=start
            while activity_start<=end:
                activity_end=min(activity_start+timedelta(days=365),end)
                all_activities=[]
                for page in range(50):
                    result = self.service.query('activities', refresh=True, start_date=activity_start.isoformat(), end_date=activity_end.isoformat(), start=page*100, limit=100)
                    report['requests'] += 1
                    if result['status'] not in ('ok','no_data'):
                        report['errors'].append({'dataset':'activities','error':result.get('error')})
                        raise RuntimeError('Sync interrupted')
                    rows = validate_rows('activities',unpack('activities',result['data']),activity_start.isoformat(),activity_end.isoformat())
                    all_activities.extend(rows)
                    self.store.put('activities',rows,result.get('fetched_at'))
                    if len(rows) < 100:
                        break
                else:
                    raise ValueError('Activity pagination exceeded 5000; use a smaller range')
                self.store.replace_range('activities', all_activities, activity_start.isoformat(), activity_end.isoformat(), result.get('fetched_at'))
                activity_start=activity_end+timedelta(days=1)
        except Exception as exc:
            report['status'] = 'partial'
            if not report['errors']:
                report['errors'].append({'error':'sync_processing_failed','error_type':type(exc).__name__})
        data = self.store.load(requested.isoformat(), end.isoformat())
        current_ids={r['activityId'] for r in self.store.load(start.isoformat(),end.isoformat())['activities']}
        report['interval'].update({'new_activity_records':len(current_ids-previous_ids),
                                   'removed_activity_records':len(previous_ids-current_ids) if report['status']=='ok' else None,
                                   'gap_fetch_completed':report['status']=='ok'})
        report['records'] = {k:len(v) for k,v in data.items()}
        report['missing_calendar_days'] = {k:days-len({r.get('calendarDate') for r in rows})
                                           for k,rows in data.items() if k!='activities'}
        self.store.finish(report)
        return report
