"""Public entry point. User state is independent of installed source version."""
import argparse
import getpass
import json
import os
import sys
from . import __version__, TITLE
from .config import load_settings, save_settings, save_api_key
from .menu import MenuStore, RESTORE_COMMAND
from .onboarding import welcome,choose_language,localize_result,WELCOME_TEXT


def main():
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8',errors='backslashreplace')
    args_in=sys.argv[1:]
    if args_in==[RESTORE_COMMAND] or args_in==['Show original function menu']:args_in=['menu','--original']
    parser=argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--version',action='version',version=__version__)
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('serve',help='Start local stdio MCP')
    commands.add_parser('setup',help='Open local graphical setup; never paste a key into AI chat')
    deepseek=commands.add_parser('deepseek',help='Chat with DeepSeek using Garmin tools')
    deepseek.add_argument('--model',choices=['deepseek-flash','deepseek-v4-pro'])
    init=commands.add_parser('init');init.add_argument('--timezone',default=None);init.add_argument('--goal-km',type=float);init.add_argument('--goal-minutes',type=float)
    init.add_argument('--language',choices=['zh','en'])
    commands.add_parser('welcome',help='Show bilingual welcome and language choices')
    language=commands.add_parser('language');language.add_argument('selection',nargs='?',help='zh/en, 中文/English, or 1/2')
    commands.add_parser('auth',help='Paste your personal API key in a hidden prompt')
    doctor=commands.add_parser('doctor');doctor.add_argument('--live',action='store_true')
    sync=commands.add_parser('sync');sync.add_argument('--days',type=int,default=93);sync.add_argument('--full',action='store_true')
    tomorrow=commands.add_parser('tomorrow');tomorrow.add_argument('--no-sync',action='store_true');tomorrow.add_argument('--no-research',action='store_true');tomorrow.add_argument('--planned-km',type=float);tomorrow.add_argument('--subjective-json')
    commands.add_parser('research')
    menu=commands.add_parser('menu');menu.add_argument('--original',action='store_true');menu.add_argument('--hide',nargs='*',type=int)
    add=commands.add_parser('add-function');add.add_argument('--name',required=True);add.add_argument('--instructions',required=True)
    remove=commands.add_parser('remove-function');remove.add_argument('id',type=int)
    client=commands.add_parser('client-config');client.add_argument('--client',choices=['claude','codex','doubao'],default='claude')
    args=parser.parse_args(args_in)
    try:
        settings=load_settings();menus=MenuStore(settings.data_dir/'menu-preferences.json')
        if args.command=='serve':
            from .server import run
            run();return
        if args.command=='setup':
            from .gui_setup import run
            run();return
        if args.command=='deepseek':
            from .deepseek import run
            raise SystemExit(run(settings,args.model))
        if args.command=='welcome' or (args.command=='language' and not args.selection):
            print(welcome(settings)['message']);return
        if args.command=='language':
            selected=choose_language(args.selection)
            settings=selected
            result=localize_result({**menus.view(),'message':'语言已设为中文。' if selected.language=='zh' else 'Language set to English.'},selected.language)
        elif args.command=='init':
            changes={k:v for k,v in {'timezone':args.timezone,'goal_distance_km':args.goal_km,'goal_minutes':args.goal_minutes,'language':args.language}.items() if v is not None}
            updated=save_settings(settings,**changes)
            settings=updated
            result={'title':TITLE,'version':__version__,'data_dir':str(updated.data_dir),'timezone':updated.timezone,'goal':updated.goal}
        elif args.command=='auth':
            key=getpass.getpass('Garmin Personal API key (hidden): ').strip()
            save_api_key(settings,key)
            result={'saved':True,'note':'Key is local only; run garmin-assistant doctor --live to verify with Garmin.'}
            if settings.language is None:
                if sys.stdin.isatty():
                    print(WELCOME_TEXT)
                    while True:
                        try:
                            selected=choose_language(input('请输入 1 或 2 / Enter 1 or 2: '))
                            settings=selected
                            result['language']=selected.language
                            break
                        except ValueError:print('请选择 1（中文）或 2（English）/ Please enter 1 or 2.')
                else:result['onboarding']=welcome(settings)
        elif args.command=='doctor':
            from .menu import CORE_FUNCTIONS
            result={'version':__version__,'python':sys.version.split()[0],'timezone':settings.timezone,
                    'data_dir':str(settings.data_dir),'key_configured':bool(os.environ.get('GARMIN_PERSONAL_API_KEY')) or settings.key_file.is_file(),
                    'core_menu_ids':[f.id for f in CORE_FUNCTIONS],'status':'ok'}
            if args.live and settings.language is None:
                result.update({'garmin_status':'not_checked','onboarding':welcome(settings),
                    'next_step_cli':'garmin-assistant language zh / garmin-assistant language en; then rerun doctor --live'})
            elif args.live:
                from .server import service,today
                response=service.query('summary',date=today(),refresh=True)
                result.update({'garmin_status':response['status'],'error':response['error']})
                if response['status'] in ('error','stale'):result['status']='error'
            if settings.language is None:result['onboarding']=welcome(settings)
        elif args.command=='menu':
            result=welcome(settings) if settings.language is None else menus.restore() if args.original else menus.hide(args.hide) if args.hide is not None else menus.view()
        elif args.command=='add-function':result=menus.add(args.name,args.instructions)
        elif args.command=='remove-function':result=menus.remove(args.id)
        elif args.command=='client-config':
            paths={'GARMIN_ASSISTANT_HOME':str(settings.data_dir),'GARMIN_ASSISTANT_KEY_FILE':str(settings.key_file)}
            entry={'command':sys.executable,'args':['-m','garmin_assistant','serve'],'env':paths}
            if args.client=='codex':
                result={'instruction':'Use Settings > MCP servers, or the following command arguments (without passing a key):',
                        'argv':['codex','mcp','add','garmin-assistant','--env',f"GARMIN_ASSISTANT_HOME={paths['GARMIN_ASSISTANT_HOME']}",
                                '--env',f"GARMIN_ASSISTANT_KEY_FILE={paths['GARMIN_ASSISTANT_KEY_FILE']}",'--',sys.executable,'-m','garmin_assistant','serve']}
            else:result={'mcpServers':{'garmin-assistant':entry},'note':'stdio configuration with nonsecret paths. API key values are never embedded; environment-only keys require secure configuration in the client. Doubao availability varies by edition.'}
        else:
            if settings.language is None:
                print(json.dumps({**welcome(settings),'next_step_cli':'garmin-assistant language zh / garmin-assistant language en'},ensure_ascii=False,indent=2))
                return
            from .server import training,DATA,today
            if args.command=='sync':result=training.sync(days=args.days,full=args.full)
            elif args.command=='research':
                from .research import update_research
                result=update_research(DATA,today(),force=True)
            else:result=training.tomorrow(subjective=json.loads(args.subjective_json) if args.subjective_json else None,
                planned_km=args.planned_km,sync_first=not args.no_sync,research_refresh=not args.no_research)
        if settings.language:result=localize_result(result,settings.language)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if result.get('status') in ('error','partial'):raise SystemExit(1)
    except (ValueError,OSError,json.JSONDecodeError) as exc:
        # Do not print exception bodies which may contain private file content.
        print(json.dumps({'status':'error','type':type(exc).__name__,
                          'message':'Configuration or local operation failed; check arguments, permissions and client version.'}),file=sys.stderr)
        raise SystemExit(1)


if __name__=='__main__':main()
