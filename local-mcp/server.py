# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Local read-only Garmin MCP server; stdout is reserved for MCP messages."""
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from provider import OfficialProvider
from service import GarminService
from training import TrainingWorkflow
from research import update_research
from menu import FUNCTION_MENU
from athlete_profile import load_profile, save_profile

logging.getLogger('garmin_personal_api').setLevel(logging.WARNING)
ROOT = Path(__file__).resolve().parent
DATA = (Path(os.environ['LOCALAPPDATA']) / 'GarminLocalMCP').resolve()
KEY = ROOT.parent / 'API.txt'
service = GarminService(DATA / 'cache.sqlite3', OfficialProvider(KEY, DATA / 'bearer-token.json'))
training = TrainingWorkflow(service, DATA, report_folder=ROOT.parent/'reports')
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True)
LOCAL_WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False)
mcp = FastMCP('garmin_local', instructions=(
    'For every Garmin health/training analysis, first fill the interval since the previous successful sync using garmin_sync_data; garmin_assess_tomorrow already does this. '
    'If last literature search is >=7 days old, refresh research before advice; never claim latest evidence if refresh fails. '
    'Combine applicable current running/recovery evidence with cited classic models. Assess candidate abstracts before using their findings; do not automatically treat them as reviewed rules. '
    'Always finish Garmin answers with the current function_menu. Standalone menu/status/config questions do not require health synchronization. '
    'Use these tools for this user\'s Garmin health and exercise questions. '
    'Fetch data before answering; never invent missing values. Default dates use Asia/Dubai. '
    'Cache lasts 15 minutes; use refresh=true when the user asks for latest data. '
    'Report stale status and fetched_at when a refresh fails. '
    'Garmin calendar dates and returned units are authoritative; missing data is not zero. '
    'Only data synced to Garmin Connect is available. Garmin data tools are read-only; garmin_set_athlete_profile writes user-confirmed local preferences. '
    'For trends, query ranges; paginate activities with start/limit. '
    'Unavailable metrics such as training readiness must not be fabricated. '
    'Mention Garmin as the source when presenting its data.'
    ' For syncing use garmin_sync_data. For tomorrow running suitability call garmin_assess_tomorrow, '
    'which syncs latest data and checks recent research. Legacy running goal: 10 km under 60 minutes. For multisport assessments use garmin_assess_session with the saved primary sport and chosen session sport; never override its goal with the legacy goal. '
    'Ask about current pain, illness and fatigue if missing; never assume absent symptoms. '
    'Tomorrow advice is provisional until morning recheck. Cite reviewed sources. '
    'PubMed candidates are unappraised: fetching an abstract does not validate a training rule. '
    'Do not claim fastest possible progress or predict a target date from wearable readiness.'
))


def today():
    return datetime.now(timezone(timedelta(hours=4))).date().isoformat()


@mcp.tool(annotations=READ_ONLY)
def garmin_status() -> dict:
    """Get local cache coverage, freshness policy and credential-file presence; no network call."""
    return {**service.status(), 'key_file_exists': KEY.is_file(),
            'default_timezone': 'Asia/Dubai', 'today': today(),'function_menu':FUNCTION_MENU}


@mcp.tool(annotations=READ_ONLY)
def garmin_function_menu() -> dict:
    """Return the current supported Garmin functions and persistent analysis policy; no network call."""
    return {'function_menu':FUNCTION_MENU,'policy':{
        'before_analysis':'补齐上次完整同步后至今的运动和健康数据，报告失败和缺失。',
        'research':'距上次成功检索满 7 天时重新检索，必要时可强制更新；失败时明确注明旧依据。',
        'evidence':'最新适用研究 + 经典模型；列明论文/著作名称、年份、链接及实际应用。',
        'goal':'10 公里跑进 60 分钟','after_response':'返回现有功能菜单。'}}


@mcp.tool(annotations=READ_ONLY)
def garmin_daily_summary(date: str | None = None, refresh: bool = False) -> dict:
    """Read Garmin daily wellness summary (YYYY-MM-DD; default today), including available daily metrics."""
    return service.query('summary', refresh=refresh, date=date or today())


@mcp.tool(annotations=READ_ONLY)
def garmin_sleep(date: str | None = None, refresh: bool = False) -> dict:
    """Read sleep and sleep stages for a Garmin calendar date (default today). Empty means unavailable."""
    return service.query('sleep', refresh=refresh, date=date or today())


@mcp.tool(annotations=READ_ONLY)
def garmin_heart_rate(date: str | None = None, refresh: bool = False) -> dict:
    """Read a day's heart-rate values and available summary; preserve Garmin units and timestamps."""
    return service.query('heart_rate', refresh=refresh, date=date or today())


@mcp.tool(annotations=READ_ONLY)
def garmin_hrv(date: str | None = None, refresh: bool = False) -> dict:
    """Read heart-rate variability for a Garmin calendar date (default today)."""
    return service.query('hrv', refresh=refresh, date=date or today())


@mcp.tool(annotations=READ_ONLY)
def garmin_range(metric: Literal['steps', 'stress', 'body_battery'],
                 start_date: str, end_date: str, refresh: bool = False) -> dict:
    """Read inclusive date range: steps/stress at most 28 days; Body Battery at most 31 days. Split longer windows."""
    return service.query(metric, refresh=refresh, start_date=start_date, end_date=end_date)


@mcp.tool(annotations=READ_ONLY)
def garmin_activities(start_date: str | None = None, end_date: str | None = None,
                      start: int = 0, limit: int = 20, refresh: bool = False) -> dict:
    """Read Garmin activities, optionally filtered by date. Paginate using start offset; limit 1-100. Units as returned."""
    params = {'start': start, 'limit': limit}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    return service.query('activities', refresh=refresh, **params)


@mcp.tool(annotations=READ_ONLY)
def garmin_activity_detail(activity_id: int, refresh: bool = False) -> dict:
    """Read details of one activity using its positive activityId from garmin_activities."""
    return service.query('activity', refresh=refresh, activity_id=activity_id)


class SubjectiveCheck(BaseModel):
    """Current symptoms only. Omitted or null values mean unknown."""
    pain_0_10: float | None = Field(default=None, ge=0, le=10)
    fatigue_0_10: float | None = Field(default=None, ge=0, le=10)
    illness: bool | None = None
    pain_with_walking: bool | None = None
    focal_bone_pain: bool | None = None
    chest_pain: bool | None = None
    fainting: bool | None = None


class SwimmingSafety(BaseModel):
    shoulder_pain: bool | None = None
    swimming_alone: bool | None = None


@mcp.tool(annotations=READ_ONLY)
def garmin_get_athlete_profile() -> dict:
    """Read the locally saved sport and goal profile; no Garmin request."""
    return {'profile': load_profile(DATA)}


@mcp.tool(annotations=LOCAL_WRITE)
def garmin_set_athlete_profile(primary_sport: Literal['running','cycling','swimming','climbing'], goal: str,
                               goal_date: str | None = None, experience_note: str | None = None) -> dict:
    """Save user-confirmed local sport preferences; does not alter Garmin data."""
    return {'profile': save_profile(DATA,primary_sport,goal,goal_date,experience_note)}


@mcp.tool(annotations=READ_ONLY)
def garmin_assess_session(session_sport: Literal['running','cycling','swimming','climbing','other'] | None = None,
                          session_intent: Literal['recovery','base','quality','skills'] | None = None,
                          subjective: SubjectiveCheck | None = None, swimming_safety: SwimmingSafety | None = None,
                          refresh_research: bool = False) -> dict:
    """Create a safe, next-day multisport capacity prescription from the saved primary sport profile."""
    return training.assess_session(session_sport,session_intent,
        subjective.model_dump(exclude_none=True) if subjective else None,
        swimming_safety.model_dump(exclude_none=True) if swimming_safety else None,
        force_research=refresh_research)


@mcp.tool(annotations=READ_ONLY)
def garmin_sync_data(days: int = 93, full: bool = False) -> dict:
    """Sync official Garmin data to local history. First call backfills 93 days; later calls overlap 7 days. full=true refetches requested history. Returns coverage/errors, not all raw records."""
    return training.sync(days=days, full=full)


@mcp.tool(annotations=READ_ONLY)
def garmin_assess_tomorrow(subjective: SubjectiveCheck | None = None,
                           planned_distance_km: float | None = None,
                           refresh_research: bool = False) -> dict:
    """Sync latest Garmin history, check dated running/recovery research, and recommend tomorrow's training toward 10 km under 60 min. Current symptoms optional but unknown symptoms prevent hard-session clearance. Saves local reports; advice is provisional until morning recheck."""
    return training.tomorrow(subjective=subjective.model_dump(exclude_none=True) if subjective else None,
                             planned_km=planned_distance_km, force_research=refresh_research)


@mcp.tool(annotations=READ_ONLY)
def garmin_update_research(force: bool = True) -> dict:
    """Discover recent running-training and rehabilitation papers from PubMed. No health data sent. Includes dated reviewed sources and unappraised candidates; network failures are explicitly reported."""
    return update_research(DATA, today(), force=force)


if __name__ == '__main__':
    mcp.run(transport='stdio')
