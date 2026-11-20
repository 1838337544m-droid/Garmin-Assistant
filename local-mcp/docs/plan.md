# Local Garmin MCP

User authorized direct implementation on this computer. Python, stdio MCP,
official Garmin Personal API client, SQLite cache outside OneDrive. Existing
D:/garmin/API.txt remains the credential source, never copied into MCP config
or output. No unsolicited notifications or scheduled jobs: queries refresh on
demand with a 15 minute cache. Explicit refresh bypasses the cache. Stale data
must remain usable during network failures and be clearly marked stale.

## Implementation plan
- Write failing tests for cache persistence, freshness, safe errors, parameter
  validation, and preserving cached results when the provider fails.
- Implement a SQLite cache and official-client adapter; support daily summary,
  sleep, heart rate, HRV, stress, steps, Body Battery, activities, activity detail.
- Expose typed read-only MCP tools with date and freshness metadata.
- Test real authentication and reads without printing credentials or health
  payloads. Test MCP discovery and invocation through a real stdio client.
- Register the verified command in Codex, preserving existing MCP servers.
- Document usage, credential replacement, cache policy, and limitations.

## Constraints and checks
Use official host only. Never emit exception bodies/credentials. Validate date
ranges and IDs before network calls; cap ranges and activity page sizes. Store
only requested data. Report Garmin timezone/date as returned; default queries
use Asia/Dubai. Do not claim missing data means zero. No fabricated health data
in production. Check real failures as well as successful reads.

## Progress
2026-10-28: Source identified as Garmin Personal API. Environment installation
started. No existing code to integrate; standalone D:/garmin/local-mcp directory.

Implementation finished: 8 unit tests plus 7 invalid-input subcases passed.
Live stdio MCP initialization and all 8 tools verified; 9 actual read queries
(including range metric variants) returned ok. Credentials restricted by ACL.
Registered garmin_local using codex mcp add; existing entries preserved.
No background polling: user asks, tools fetch and cache. Restart client to load.
