# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Explicit read-only live verification. Prints metadata, never raw health data or credentials."""
import asyncio
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    root = Path(__file__).resolve().parent
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    config = StdioServerParameters(command=sys.executable, args=[str(root / 'server.py')], env=env)
    checks = []
    async with stdio_client(config) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            listed = await session.list_tools()
            names = [tool.name for tool in listed.tools]
            print(json.dumps({'mcp_tools': names}), flush=True)
            assert {'garmin_sync_data','garmin_assess_tomorrow','garmin_update_research'} <= set(names)
            status = await session.call_tool('garmin_status', {})
            payload = status.structuredContent
            if payload is None:
                payload = json.loads(status.content[0].text)
            day = payload['today']
            yesterday = (date.fromisoformat(day) - timedelta(days=1)).isoformat()
            for name, args in [
                ('garmin_activities', {'limit': 3, 'refresh': True}),
                ('garmin_daily_summary', {'date': yesterday, 'refresh': True}),
                ('garmin_sleep', {'date': day, 'refresh': True}),
                ('garmin_hrv', {'date': yesterday, 'refresh': True}),
                ('garmin_heart_rate', {'date': yesterday, 'refresh': True}),
                ('garmin_range', {'metric': 'steps', 'start_date': yesterday, 'end_date': day, 'refresh': True}),
                ('garmin_range', {'metric': 'stress', 'start_date': yesterday, 'end_date': day, 'refresh': True}),
                ('garmin_range', {'metric': 'body_battery', 'start_date': yesterday, 'end_date': day, 'refresh': True}),
            ]:
                result = await session.call_tool(name, args)
                data = result.structuredContent
                if data is None:
                    data = json.loads(result.content[0].text)
                if result.isError:
                    raise RuntimeError(f'MCP tool failed: {name}')
                entry = {'tool': name, 'status': data['status'], 'source': data['source'],
                         'fetched_at': data['fetched_at'], 'error': data['error'],
                         'payload_bytes': len(json.dumps(data['data']))}
                checks.append(entry)
                print(json.dumps(entry), flush=True)
                if data['status'] in ('error', 'stale'):
                    # Stop if credentials/network do not work, rather than repeatedly retrying.
                    break
                if name == 'garmin_activities' and isinstance(data['data'], list) and data['data']:
                    activity_id = data['data'][0].get('activityId')
                    if activity_id:
                        detail = await session.call_tool('garmin_activity_detail', {'activity_id': activity_id, 'refresh': True})
                        d = detail.structuredContent or json.loads(detail.content[0].text)
                        detail_check = {'tool': 'garmin_activity_detail', 'status': d['status'],
                                        'source': d['source'], 'error': d['error']}
                        checks.append(detail_check)
                        print(json.dumps(detail_check), flush=True)
            result = await session.call_tool('garmin_status', {})
            final = result.structuredContent or json.loads(result.content[0].text)
            report = {'tools': names, 'checks': checks, 'cache': final}
            (root / 'verification-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
            assert checks and all(c['status'] in ('ok', 'no_data') for c in checks), 'Live Garmin read did not pass'


if __name__ == '__main__':
    asyncio.run(main())
