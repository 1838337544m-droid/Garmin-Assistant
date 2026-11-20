# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Validated local athlete-sport profile storage."""
from datetime import date, datetime, timezone
from pathlib import Path

from .research import atomic_json

PRIMARY_SPORTS = {'running', 'cycling', 'swimming', 'climbing'}


class ProfileValidationError(ValueError):
    pass


def _path(folder):
    return Path(folder) / 'athlete_profile.json'


def load_profile(folder):
    path = _path(folder)
    if not path.is_file():
        return None
    import json
    try:
        result=json.loads(path.read_text(encoding='utf-8'))
        if (not isinstance(result,dict) or result.get('schema_version')!=1 or
            result.get('primary_sport') not in PRIMARY_SPORTS or
            not isinstance(result.get('goal'),str) or not result['goal'].strip() or
            not isinstance(result.get('profile_effective_at'),str)):
            raise ValueError('invalid profile')
        return result
    except (ValueError,TypeError):
        raise ProfileValidationError('Invalid athlete profile; save the sport and goal again.') from None


def save_profile(folder, primary_sport, goal, goal_date=None, experience_note=None):
    if primary_sport not in PRIMARY_SPORTS:
        raise ProfileValidationError('primary_sport must be supported')
    if not isinstance(goal, str) or not goal.strip():
        raise ProfileValidationError('goal must be nonblank')
    if goal_date:
        try:
            date.fromisoformat(goal_date)
        except (TypeError, ValueError):
            raise ProfileValidationError('goal_date must be ISO date') from None
    if experience_note is not None and (not isinstance(experience_note, str) or len(experience_note) > 500):
        raise ProfileValidationError('experience_note must be at most 500 characters')
    result = {'schema_version': 1, 'primary_sport': primary_sport, 'goal': goal.strip(),
              'goal_date': goal_date, 'experience_note': experience_note,
              'profile_effective_at': datetime.now(timezone.utc).isoformat()}
    Path(folder).mkdir(parents=True, exist_ok=True)
    atomic_json(_path(folder), result)
    return result
