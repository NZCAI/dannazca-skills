# PDR Integration Handoff (for `product-management` Droid)

Use this as the integration brief to attach EdgarTools MCP into Nazca's governed tool suite.

## Objective
Promote EdgarTools MCP from standalone package to a governed federated capability in the PRD V2 architecture.

## Integration Steps
1. **Catalog capability**
   - Register EdgarTools under external market/filings capability inventory.
   - Link package path: `tools/edgartools-mcp/`.
2. **Define governance controls**
   - RBAC matrix: which roles can access company/ownership/full-text tools.
   - Deny-by-default for high-volume or broad full-text operations unless justified.
3. **Set execution policy**
   - Default profile: `edgartools` stdio.
   - Fallback profile: `edgar517` for compatibility.
   - HTTP pilot profile: `edgartools-http` for shared operation testing.
4. **Observability requirements**
   - Track tool invocation counts, errors, and fallback usage.
   - Add pilot KPI: `% successful MCP calls without profile fallback`.
5. **Rollout**
   - Pilot with 2–3 analysts.
   - Exit criteria: stable availability + acceptable query latency + low fallback rate.

## Suggested roadmap updates in main PRD
- Add EdgarTools as named service candidate under `mcp-market`.
- Add phase gate for HTTP pilot stabilization before production endpoint.
- Add fallback policy language for MCP version compatibility pinning.

## Deliverables owned by PM Droid
- Updated PRD annex for EdgarTools integration
- Tool ownership and SLA proposal
- Rollout checklist and acceptance criteria
