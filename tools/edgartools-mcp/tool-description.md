# EdgarTools MCP — Nazca Tool Description

## Fit with PRD (V2)
EdgarTools as an MCP server fits Nazca's federated capability layer: it provides external SEC intelligence as a modular tool service, keeps FastAPI/LangChain orchestration clean, and aligns with governance (RBAC, deny-by-default, auditable tool usage).

## Product Description
EdgarTools MCP exposes SEC EDGAR data to AI agents through standardized MCP tools for:
- Public company financial analysis
- Filing intelligence (10-K, 10-Q, 8-K, DEF 14A, Form 4, 13F)
- Trend/comparables workflows
- Ownership and insider monitoring

## Target Users
- Investment team (deal screening, follow-ons, memo prep)
- Technical analysts (structured extraction and time-series generation)
- Agent developers (tool-enabled diligence flows)

## Requirements
### Functional
1. Default local stdio install for fast onboarding.
2. Runtime identity only (`EDGAR_IDENTITY`), never hardcoded credentials.
3. Factory + Claude compatibility with reusable templates.
4. Prompt pack for diligence and follow-on workflows.
5. Guidance on when to pair with Nazca skills (`data-querying`, `product-management`, `solid`).

### Non-Functional
1. Reproducible setup across machines.
2. Minimal blast radius if tool fails (federated service boundary).
3. Auditable configuration in git.
4. HTTP mode path available for shared-team deployment.

## Scope
### In scope
- Tool packaging under `tools/edgartools-mcp/`
- Local stdio setup (default)
- HTTP WIP structure for pilot
- Installation prompts for cross-machine rollout

### Out of scope
- Full production HTTP infra deployment (ECS/k8s/SSO/zero-trust)
- org-wide RBAC enforcement implementation in this repo

## Tradeoffs (stdio vs HTTP)
- **stdio (default):** fastest onboarding, zero infra, per-user runtime variability.
- **HTTP (WIP/pilot):** shared availability, better governance and observability, higher ops overhead.

## Roadmap
### Phase 1 — Local baseline (Completed)
- Stdio tool package, prompt pack, templates, and install guides.

### Phase 2 — HTTP pilot (WIP)
- Add HTTP config templates and local docker/systemd run patterns.
- Validate uptime and compatibility for investment workflows.

### Phase 3 — Production hardening (Planned)
- Centralized auth, telemetry, SLOs, runbooks, ownership model.
- Integrate with Nazca MCP federation and policy controls.

## Governance Notes
- Use allowlisted tool access by role.
- Keep `EDGAR_IDENTITY` at runtime only.
- Log MCP server selection (`stdio` vs `http`) in team runbooks.
- Keep fallback profile for compatibility pinning when client/schema mismatches occur.
