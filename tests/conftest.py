import pytest


@pytest.fixture(autouse=True)
def isolated_private_settings(tmp_path,monkeypatch):
    monkeypatch.setenv('GARMIN_ASSISTANT_HOME',str(tmp_path/'private-home'))
    monkeypatch.delenv('GARMIN_PERSONAL_API_KEY',raising=False)
    monkeypatch.delenv('GARMIN_ASSISTANT_KEY_FILE',raising=False)
    import garmin_assistant.sync as sync
    import garmin_assistant.training as training
    monkeypatch.setattr(sync,'local_today',lambda:'2026-10-31')
    monkeypatch.setattr(training,'local_today',lambda:'2026-10-31')
