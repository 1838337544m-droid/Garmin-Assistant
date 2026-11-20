# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Run local sync and tomorrow analysis without restarting a connected MCP client."""
import argparse
import json
from server import training, DATA, today
from research import update_research

parser=argparse.ArgumentParser(description='Local Garmin sync and running assessment')
commands=parser.add_subparsers(dest='command',required=True)
sync=commands.add_parser('sync');sync.add_argument('--days',type=int,default=93);sync.add_argument('--full',action='store_true')
assessment=commands.add_parser('tomorrow');assessment.add_argument('--no-sync',action='store_true');assessment.add_argument('--no-research',action='store_true')
assessment.add_argument('--planned-km',type=float);assessment.add_argument('--subjective-json',help='JSON object of current symptom ratings')
commands.add_parser('research')
commands.add_parser('dashboard')
args=parser.parse_args()
if args.command=='dashboard':
    from dashboard import run
    run(training,DATA)
    raise SystemExit(0)
elif args.command=='sync':result=training.sync(days=args.days,full=args.full)
elif args.command=='research':result=update_research(DATA,today(),force=True)
else:result=training.tomorrow(subjective=json.loads(args.subjective_json) if args.subjective_json else None,
                              planned_km=args.planned_km,sync_first=not args.no_sync,research_refresh=not args.no_research)
print(json.dumps(result,ensure_ascii=False,indent=2))
