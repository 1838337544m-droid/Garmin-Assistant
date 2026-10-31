"""Official Garmin Personal API adapter. Never returns credentials."""
from pathlib import Path
import os

OFFICIAL_HOST = 'https://personal.connectapi.garmin.com'


def dispatch(client, kind, p):
    if kind == 'summary':
        return client.get_daily_summaries(p['date'], p['date'])
    daily = {'sleep': 'get_daily_sleep', 'heart_rate': 'get_daily_heart_rate',
             'hrv': 'get_daily_hrv'}
    ranges = {'steps': 'get_daily_steps', 'stress': 'get_daily_stress',
              'body_battery': 'get_daily_body_battery', 'daily_summaries': 'get_daily_summaries',
              'sleep_summaries': 'get_daily_sleep_summaries', 'hrv_summaries': 'get_daily_hrv_summaries'}
    if kind in daily:
        return getattr(client, daily[kind])(p['date'])
    if kind in ranges:
        return getattr(client, ranges[kind])(p['start_date'], p['end_date'])
    if kind == 'activities':
        return client.search_activities(**p)
    if kind == 'activity':
        return client.get_activity(p['activity_id'])
    raise ValueError('Unsupported data type')


class OfficialProvider:
    def __init__(self, key_file: Path, token_file: Path):
        self.key_file, self.token_file = key_file, token_file

    def __call__(self, kind, params):
        from garmin_personal_api import GarminPersonalApiClient, PersonalApiAuthenticator
        from garmin_personal_api.errors import HttpError
        key = (os.environ['GARMIN_PERSONAL_API_KEY'] if 'GARMIN_PERSONAL_API_KEY' in os.environ
               else self.key_file.read_text(encoding='utf-8-sig')).strip()
        if not key or any(c.isspace() for c in key):
            raise ValueError('Key file must contain exactly one API key')
        with PersonalApiAuthenticator(timeout=20, bearer_token_cache_file=self.token_file) as auth:
            # Do not permit inherited environment variables to redirect credentials.
            auth.base_url = OFFICIAL_HOST
            token = auth.obtain_token(key)
            with GarminPersonalApiClient(token.access_token, timeout=20) as client:
                client.base_url = OFFICIAL_HOST
                try:
                    return dispatch(client, kind, params)
                except HttpError as exc:
                    if exc.status_code != 401:
                        raise
                    token = auth.obtain_token(key, force_refresh=True)
                    client.update_bearer_token(token.access_token)
                    return dispatch(client, kind, params)
