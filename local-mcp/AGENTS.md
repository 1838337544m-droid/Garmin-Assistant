# Repository update workflow

After a user-authorized source update passes the relevant tests and is merged into main:

1. Push main to the private origin, Garmin-Local-MCP.
2. Synchronize the tracked source snapshot to `local-mcp/` in the public repository
   `1838337544m-droid/Garmin-Assistant`, preserving its existing API edition and history.
3. Include source, tests, license and documentation only. Never include credentials,
   local athlete profiles, health databases, reports, environment files or scratch worktrees.
4. Test the public snapshot and push the public main branch without force.
5. Report both push results. A push failure must not be reported as success.

This is a workflow for approved updates, not permission to change training rules automatically.
