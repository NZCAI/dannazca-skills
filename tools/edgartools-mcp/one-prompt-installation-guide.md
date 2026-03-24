# One-Prompt Installation Guide (From Git, Factory + Claude)

Copy/paste this prompt into Droid or Claude Code:

```text
Install Nazca EdgarTools MCP package from Git and configure this machine for both Factory and Claude, using runtime identity only.

Repository:
https://github.com/NZCD5L/dannazca-skills

Do exactly this:
1) Clone or pull repo into a local working folder.
2) Export identity for this shell only:
   export EDGAR_IDENTITY="Your Name your.email@example.com"
3) Configure Factory default profile (stdio):
   droid mcp add edgartools "uvx --from edgartools[ai] edgartools-mcp" --env EDGAR_IDENTITY="$EDGAR_IDENTITY"
4) Add compatibility fallback profile:
   droid mcp add edgar517 "uvx --from edgartools[ai]==5.17.1 edgartools-mcp" --env EDGAR_IDENTITY="$EDGAR_IDENTITY"
5) Update Claude Desktop config with both servers (`edgartools` and `edgar517`) using the same command/args/env.
6) Optional HTTP pilot:
   - Start endpoint:
     EDGAR_IDENTITY="$EDGAR_IDENTITY" uvx --from "edgartools[ai]" edgartools-mcp --transport streamable-http --host 127.0.0.1 --port 8765
   - Register in Factory:
     droid mcp add edgartools-http http://127.0.0.1:8765/mcp --type http
7) Validate:
   droid exec --list-tools | rg -i "edgar"
8) Return a short report with:
   - which profile is active (edgartools or edgar517)
   - Factory MCP entries installed
   - Claude config update status
   - HTTP pilot status (on/off)
```
