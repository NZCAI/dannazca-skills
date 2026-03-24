# Installation Guide (Nazca Team)

## Prerequisites
- Python 3.10+
- `uv` installed (recommended)
- Factory CLI (`droid`)
- Claude Desktop and/or Claude Code

## 1) Set runtime identity (required by SEC)
```bash
export EDGAR_IDENTITY="Your Name your.email@example.com"
```

## 2) Default setup (stdio, recommended)
### Factory
```bash
droid mcp add edgartools "uvx --from edgartools[ai] edgartools-mcp" --env EDGAR_IDENTITY="$EDGAR_IDENTITY"
```

### Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "edgartools": {
      "command": "uvx",
      "args": ["--from", "edgartools[ai]", "edgartools-mcp"],
      "env": {
        "EDGAR_IDENTITY": "Your Name your.email@example.com"
      }
    }
  }
}
```

## 3) Compatibility profile (when schema/transport mismatch appears)
Use pinned profile:

```bash
droid mcp add edgar517 "uvx --from edgartools[ai]==5.17.1 edgartools-mcp" --env EDGAR_IDENTITY="$EDGAR_IDENTITY"
```

In Claude Desktop, add another entry:
- `name`: `edgar517`
- `command`: `uvx`
- `args`: `["--from","edgartools[ai]==5.17.1","edgartools-mcp"]`
- same `EDGAR_IDENTITY`

## 4) HTTP mode (WIP / pilot)
Run local shared endpoint:
```bash
EDGAR_IDENTITY="$EDGAR_IDENTITY" uvx --from "edgartools[ai]" edgartools-mcp --transport streamable-http --host 127.0.0.1 --port 8765
```

Register in Factory:
```bash
droid mcp add edgartools-http http://127.0.0.1:8765/mcp --type http
```

Client-side Claude/Factory config should point to:
`http://127.0.0.1:8765/mcp`

## 5) Validation
```bash
droid exec --list-tools | rg -i "edgar"
```

Try:
- “Compare AAPL vs NVDA revenue and net income trends for 12 quarters.”
- “Extract risk factors from latest 10-K for META.”
