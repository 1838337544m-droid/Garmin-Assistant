import json
import threading
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import pytest
from dashboard import make_server


def test_dashboard_authorization_and_analysis(tmp_path):
    class Workflow:
        def assess_session(self,sport,**kwargs):
            assert sport=='cycling'
            return {'session_sport':sport,'primary_sport':'running','goal':'耐力',
                    'recommendation':'结果已生成','metrics':{},'missing':[]}
    server,url=make_server(Workflow(),tmp_path)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    root=url.split('/?')[0]; token=url.split('key=')[1]
    try:
        assert '保存选择'.encode() in urlopen(url).read()
        with pytest.raises(HTTPError) as denied:
            urlopen(root+'/profile')
        assert denied.value.code==403
        body=json.dumps({'primary_sport':'running','session_sport':'cycling','goal':'耐力'}).encode()
        headers={'X-Dashboard-Key':token,'Content-Type':'application/json'}
        req=Request(root+'/analyze',data=body,headers=headers)
        result=json.load(urlopen(req))
        assert '结果已生成' in result['html']
        with pytest.raises(HTTPError) as cross:
            urlopen(Request(root+'/analyze',data=body,headers={**headers,'Origin':'https://example.com'}))
        assert cross.value.code==403
    finally:
        server.shutdown();server.server_close();thread.join()
