# Garmin Assistant (API edition)

Read your own Garmin data locally, with running/recovery guidance and citations.
This is an independent project using Garmin's official Personal API. It does not
need your Garmin password and is not endorsed by Garmin.

## Install

Install Python 3.12+ and Git. On Windows, open PowerShell and run one line at a time:

```powershell
git clone https://github.com/1838337544m-droid/garmin-assistant-api.git
cd garmin-assistant-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\garmin-assistant.exe init --timezone America/New_York --goal-km 10 --goal-minutes 60
```

Choose your own IANA timezone, not necessarily the example above. Default is UTC.
On macOS/Linux use `python3` and `.venv/bin/garmin-assistant`.

Create your own key in [Garmin Connect Personal API settings](https://connect.garmin.com/app/settings/personalApiToken).
Then run this command **on its own**:

```powershell
.\.venv\Scripts\garmin-assistant.exe auth
```

At `Garmin Personal API key (hidden):`, paste the complete key once and press Enter.
No characters or asterisks appear: this is expected. Do not paste the next command
while the program is asking for the key. Use Ctrl+C to cancel and retry if needed.

First use shows a bilingual welcome. Enter **2** for **English** (1 selects Chinese).
Your selection is saved. `"saved": true` means the key was stored, not verified.
Next run:

```powershell
.\.venv\Scripts\garmin-assistant.exe doctor --live
```

`"garmin_status": "ok"` confirms a successful Garmin read; `no_data` means no record
for the selected day. Errors do not count as successful connection.

## Connect an AI client

Generate your local stdio configuration with `client-config --client claude` or
`client-config --client codex`. Use the absolute executable path and nonsecret
environment paths it returns. The top-level `note` is explanatory, not client config.

- Claude Desktop/Code: local stdio MCP configuration is supported by the relevant desktop/coding client.
- GPT/Codex local-execution environments: add the command as a local MCP server.
- Ordinary ChatGPT web/mobile: this edition has no remote OAuth server; generate a report locally and upload it instead.
- Doubao: use local MCP only in a client edition that actually exposes that capability. Otherwise upload a generated report.

See [client-specific setup and limits](CLIENTS.md). Product/account editions differ;
the project does not claim all clients have been tested end to end.

When first interacting with the MCP, the AI should call `garmin_welcome`. If it asks
for language, reply **2 / English** before selecting a function. MCP cannot force
an unsolicited chat popup just because a server was connected.

## Core functions

1. Sync data and fill the interval since the last successful sync.
2. Assess tomorrow's training against your personal goal.
3. View activities and activity details.
4. View sleep, heart rate and HRV.
5. Read steps, stress and Body Battery over a date range.
6. Refresh running and rehabilitation research.
7. View sync status and the function menu.

Core IDs remain 1–7. Custom prompt workflows use IDs >=100 and cannot replace core
tools. Hidden core items can be restored with **Show original function menu** or
**显示原有功能菜单**; your custom items are retained.

Switch at any time with `garmin-assistant language en` or `garmin-assistant language zh`.
Raw Garmin fields, paper titles and user-authored custom text are not rewritten.

## Important limits

Advice is provisional until the morning recheck. Unknown symptoms are not assumed
absent. The rules are coaching heuristics, not medical clearance or injury-risk
probabilities. Newly retrieved papers require appraisal; they do not automatically
change training rules. Connected AI providers receive the tool results you use.

Your key, settings, history and reports are outside the source checkout. Updating
the code preserves them. See [maintenance and rollback](MAINTENANCE.md).
