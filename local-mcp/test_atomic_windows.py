from pathlib import Path
from research import atomic_json


def test_store_python_cross_volume_rename_retries_physical_file(tmp_path,monkeypatch):
    original=Path.replace
    calls=[]
    def replace(source,target):
        calls.append(source)
        if len(calls)==1:
            error=OSError('cross-volume')
            error.winerror=17
            raise error
        return original(source,target)
    monkeypatch.setattr(Path,'replace',replace)
    target=tmp_path/'profile.json'
    atomic_json(target,{'saved':True})
    assert target.read_text(encoding='utf-8').find('true')!=-1
    assert len(calls)==2
