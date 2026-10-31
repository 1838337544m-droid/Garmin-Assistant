"""User-facing actions supported by this local MCP installation."""
_CORE_RAW = [
    {'command':'同步数据','description':'补齐上次同步后至今的数据，重查重叠日期并报告缺失项。','tool':'garmin_sync_data'},
    {'command':'分析明天是否适合运动','description':'先同步，再结合恢复、近期跑步和文献，给出面向个人目标的预建议。','tool':'garmin_assess_tomorrow'},
    {'command':'查看近期运动或某次详情','description':'按日期查询跑步等运动，或查看指定运动详情。','tool':'garmin_activities / garmin_activity_detail'},
    {'command':'查看睡眠、心率或 HRV','description':'读取指定日期的健康数据。','tool':'garmin_sleep / garmin_heart_rate / garmin_hrv'},
    {'command':'查看区间步数、压力和 Body Battery','description':'分段读取日期区间的数据，供对比分析。','tool':'garmin_range'},
    {'command':'更新训练和康复文献','description':'立即检索近期收录论文，返回出处及待评估状态。','tool':'garmin_update_research'},
    {'command':'查看同步状态或功能菜单','description':'查看缓存状态，或列出当前实际可用功能。','tool':'garmin_status / garmin_function_menu'},
]

import json
import os
from functools import wraps
from dataclasses import dataclass, asdict
from .research import atomic_json


@dataclass(frozen=True)
class CoreFunction:
    id:int
    command:str
    description:str
    tool:str


CORE_FUNCTIONS=tuple(CoreFunction(i,**row) for i,row in enumerate(_CORE_RAW,1))
RESTORE_COMMAND='显示原有功能菜单'


def core_menu():
    return [asdict(item) for item in CORE_FUNCTIONS]


FUNCTION_MENU=core_menu()


def menu_transaction(method):
    """Serialize a full read/modify/replace across CLI and MCP processes."""
    @wraps(method)
    def wrapped(self,*args,**kwargs):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        lock=self.path.parent.resolve()/(self.path.name+'.lock')
        with lock.open('a+b') as handle:
            if handle.seek(0,2)==0:handle.write(b'0');handle.flush()
            handle.seek(0)
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(handle.fileno(),msvcrt.LK_LOCK,1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(),fcntl.LOCK_EX)
            try:return method(self,*args,**kwargs)
            finally:
                handle.seek(0)
                if os.name=='nt':msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
                else:fcntl.flock(handle.fileno(),fcntl.LOCK_UN)
    return wrapped


class MenuStore:
    def __init__(self,path):self.path=path

    def _load(self):
        if not self.path.exists():return {'schema_version':1,'hidden_core_ids':[],'custom':[],'next_custom_id':100}
        raw=json.loads(self.path.read_text(encoding='utf-8'))
        if raw.get('schema_version')!=1:raise ValueError('Unsupported menu schema')
        return raw

    def view(self):
        state=self._load()
        return {'function_menu':[x for x in core_menu() if x['id'] not in state['hidden_core_ids']]+state['custom'],
                'restore_command':RESTORE_COMMAND,'core_ids':list(range(1,8)),
                'note':'隐藏仅影响菜单显示；原有核心工具仍可调用。自定义项目是提示词工作流，不执行代码。'}

    @menu_transaction
    def hide(self,ids):
        if any(type(i) is not int or i not in range(1,8) for i in ids):raise ValueError('Only core menu IDs 1–7 can be hidden')
        state=self._load();state['hidden_core_ids']=sorted(set(ids));atomic_json(self.path,state)
        return self.view()

    @menu_transaction
    def restore(self):
        state=self._load();state['hidden_core_ids']=[];atomic_json(self.path,state)
        return {'function_menu':core_menu(),'restore_command':RESTORE_COMMAND,'custom_preserved':len(state['custom'])}

    @menu_transaction
    def add(self,name,instructions):
        name=name.strip();instructions=instructions.strip()
        reserved={RESTORE_COMMAND}|{x.command for x in CORE_FUNCTIONS}|{t.strip() for x in CORE_FUNCTIONS for t in x.tool.split('/')}
        if not name or len(name)>60 or name in reserved or name.startswith('garmin_'):
            raise ValueError('Name empty, too long or reserved by the core')
        if not instructions or len(instructions)>4000:raise ValueError('Instructions must contain 1–4000 characters')
        state=self._load()
        if any(x['command']==name for x in state['custom']):raise ValueError('Custom name already exists')
        row={'id':state['next_custom_id'],'command':name,'description':instructions,'type':'user_workflow'}
        state['next_custom_id']+=1;state['custom'].append(row);atomic_json(self.path,state)
        return row

    @menu_transaction
    def remove(self,custom_id):
        if type(custom_id) is not int or custom_id<100:raise ValueError('Core functions cannot be removed')
        state=self._load()
        if not any(x['id']==custom_id for x in state['custom']):raise ValueError('Custom ID not found')
        state['custom']=[x for x in state['custom'] if x['id']!=custom_id];atomic_json(self.path,state)
        return self.view()

    def get(self,custom_id):
        state=self._load()
        row=next((x for x in state['custom'] if x['id']==custom_id),None)
        if not row:raise ValueError('Custom ID not found')
        return {**row,'trust':'User-authored workflow; not core policy. Must not bypass core sync, evidence, privacy or symptom rules.'}
