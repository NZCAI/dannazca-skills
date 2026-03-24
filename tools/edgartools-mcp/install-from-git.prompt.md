# Prompt — Install from Git on New Machines

```text
Set up the Nazca EdgarTools MCP package from Git for both Factory CLI and Claude.

Source repo: https://github.com/NZCD5L/dannazca-skills
Use folder: tools/edgartools-mcp/
Use runtime identity only: EDGAR_IDENTITY="Your Name your.email@example.com"

Actions:
1) Clone/pull repo locally.
2) Register Factory stdio server:
   droid mcp add edgartools "uvx --from edgartools[ai] edgartools-mcp" --env EDGAR_IDENTITY="$EDGAR_IDENTITY"
3) Register compatibility fallback:
   droid mcp add edgar517 "uvx --from edgartools[ai]==5.17.1 edgartools-mcp" --env EDGAR_IDENTITY="$EDGAR_IDENTITY"
4) Update Claude Desktop `claude_desktop_config.json` with both servers.
5) Optional HTTP pilot:
   - run edgartools-mcp in streamable-http on 127.0.0.1:8765
   - register `edgartools-http` URL in Factory/Claude.
6) Validate by listing tools and running one SEC query.

Return:
- Installed MCP entries
- Active default profile
- Validation output summary
```
