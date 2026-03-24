# HTTP Mode (WIP) — EdgarTools MCP

This folder is a pilot structure for running EdgarTools as a shared HTTP MCP endpoint.

## Goal
Provide always-on MCP availability for the investment team while keeping stdio as fallback.

## Current WIP assets
- `docker-compose.yml` — local shared endpoint on `:8765`
- `mcp-http.template.json` — client config snippet for HTTP registration

## Pilot checklist
1. Start service locally via docker compose.
2. Register `edgartools-http` in Factory/Claude.
3. Validate tool availability and query latency.
4. Track connection failures and fallback rate to stdio.
5. Decide promotion to production HTTP deployment.
