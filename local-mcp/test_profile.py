import pytest

from athlete_profile import ProfileValidationError, load_profile, save_profile


def test_save_profile_normalizes_and_round_trips(tmp_path):
    saved = save_profile(tmp_path, 'running', '10 km', '2027-01-01', 'beginner')
    assert saved['primary_sport'] == 'running'
    assert load_profile(tmp_path)['schema_version'] == 1


def test_profile_rejects_unknown_sport_blank_goal_and_bad_date(tmp_path):
    for args in [('other', 'goal', None), ('running', ' ', None), ('running', 'goal', 'bad')]:
        with pytest.raises(ProfileValidationError):
            save_profile(tmp_path, *args)


def test_corrupt_profile_requires_reset(tmp_path):
    (tmp_path/'athlete_profile.json').write_text('{"primary_sport":"unknown"}',encoding='utf-8')
    with pytest.raises(ProfileValidationError):
        load_profile(tmp_path)
