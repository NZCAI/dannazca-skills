# Architectural Feedback v2: Nazca System

**Version**: 2.0
**Date**: 2026-03-24
**Scope**: PRD V2, FastAPI Bridge, EdgarTools MCP, trading-analysis framework

---

## Executive Summary

**Strengths**:
- RBAC framework is sound (team + agent roles clearly separated)
- FastAPI Bridge as central connector simplifies routing
- Langchain orchestration cleanly separates concerns
- n8n automation trigger reduces custom code

**Critical Actions**:
1. Add RBAC checks at FastAPI Bridge entry point
2. Define SLA/SLO targets (HTTP resilience, n8n uptime)
3. Containerize n8n + EdgarTools MCP for reliable deployment
4. Implement observability instrumentation (trace propagation, governance events)

---

## Section 2: Governance & RBAC

### 2.1 RBAC Framework Validated ✓
Team roles (Admin, Data Scientist, ML Trainee, Auto Trainee, Analyst, Partner) map cleanly to tools.
Agent roles (Product Manager, Code-Reviewer, AI-Data-Analyst) are operationally isolated.
See `RBAC_Framework_v2.md` for approved role definitions.

### 2.2 RBAC Implementation Checklist
- [ ] FastAPI Bridge enforces RBAC at entry point (all requests checked before routing)
- [ ] CI/CD gates validate RBAC coverage for new agents
- [ ] Audit logging captures all RBAC decisions (allow/deny)
- [ ] Role escalation workflow documented (ticket → approval → access)

### 2.3 Internal Tools, No Auth Required Yet
✓ **Correct decision**: Skip authentication complexity. RBAC is sufficient for internal worktools.
- No OAuth, no JWT, no secrets management needed yet
- RBAC checks provide governance (who can access what)
- Future: Add auth if/when external access required

### 2.4 Containerization Policy (NEW)
See `Containerization_Policy.md`:
- Docker images for n8n, EdgarTools MCP, FastAPI Bridge
- Health checks (liveness, readiness probes)
- Graceful degradation on service failure
- Enables HTTP fallback resilience for EdgarTools

### 2.5 No Public Endpoints ✓
- Internal tools only (no external API)
- FastAPI Bridge is single entry point
- All access flows through RBAC checks
- No need for public API authentication

### 2.6 SLAs/SLOs (to be defined)
See `Containerization_Policy.md` for targets:
- **n8n automation**: 99% uptime, < 30s execution latency
- **EdgarTools HTTP**: 99.5% availability, < 5s query response
- **FastAPI Bridge**: 99.9% uptime, < 100ms request latency

### 2.7 RBAC Checks at FastAPI Bridge
**Implementation**:
```
Client request → FastAPI Bridge
  ├─ Extract role from request context
  ├─ Check tool matrix (team-rbac-tool-matrix.yaml)
  ├─ Verify tool + operation allowed for role
  └─ Route to MCP or deny with audit log
```
- All denials logged (governance audit trail)
- High-risk ops require approval (tracked separately)
- Token usage tracked per role/agent

---

## Section 3: Architecture & Integration

### 3.1 FastAPI Bridge Role: Main Connector ✓
Routes requests → Langchain → MCP services.
Clear separation: FastAPI handles routing, Langchain handles orchestration.
**Recommendation**: Add request correlation ID for tracing.

### 3.2 Evaluation Gates (CI/CD)
Define gates before agent/prompt deployment:
1. **RBAC Coverage**: Does agent have RBAC matrix defined? (Require yes)
2. **Observability**: Does agent log governance events? (Require yes)
3. **Tool Permissions**: Does agent access only approved tools? (Auto-check via RBAC matrix)
4. **Risk Level**: Does agent access high-risk tools? (Require Risk/Compliance approval if yes)

See `Observability_Framework.md` for gate implementation details.

### 3.3 Integration Complete (RBAC ↔ Architecture)
- ✓ Team RBAC integrated (tool matrix enforced at FastAPI)
- ✓ Agent RBAC isolated (agents operate within defined scopes)
- ✓ Streamlit noted: internal MVP only, never production
- ✓ EdgarTools HTTP: final version, containerized for resilience

### 3.4 MCP Federation: Graceful Degradation
**Edge case**: EdgarTools HTTP timeout
- Circuit breaker: 3 failures → fallback (return cached data + notify user)
- Retry: exponential backoff (1s, 2s, 4s, then fail)
- Logging: all timeouts + fallback invocations tracked

See `Containerization_Policy.md` for deployment details.

### 3.5 Observability Instrumentation (NEW)
See `Observability_Framework.md`:
- **Trace Propagation**: Correlation ID across FastAPI → Langchain → MCPs
- **Governance Events**: RBAC checks, data access, token usage
- **Token Tracking**: Per-agent, per-operation cost tracking
- **Rollout**: Phased (4 weeks), monitoring-first approach

---

## Section 4: CI/CD & Deployment

### 4.1 Governance PR Gates
Changes to RBAC matrices require approval:
- `team-rbac-tool-matrix.yaml`: 2 approvals (you + team lead)
- `agent-rbac-tool-matrix.yaml`: 2 approvals (you + team lead)
- **Process**: PR → CODEOWNERS review → merge → effect within 1 hour

### 4.2 Containerization Rollout
See `Containerization_Policy.md`:
- Phase 1 (Week 1): Docker image for EdgarTools MCP (HTTP final)
- Phase 2 (Week 2): Docker image for n8n
- Phase 3 (Week 3): FastAPI Bridge containerization
- Phase 4 (Week 4): Deploy to Kubernetes/ECS with health checks

### 4.3 Audit Logging
- **RBAC decisions**: All allow/deny recorded (FastAPI layer)
- **Data access**: S3 uploads, Edgar queries logged (governance trail)
- **Governance changes**: Git history + approval records
- **Retention**: 2 years minimum

---

## Section 5: MCP Federation & Resilience

### 5.1 EdgarTools MCP: HTTP is Final ✓
- ✓ Stdio was MVP validation only
- ✓ HTTP is production version
- ✓ Containerized for reliable deployment
- ✓ Health checks (liveness, readiness)

### 5.2 Fallback Resilience Policy (NEW)
See `Containerization_Policy.md`:
- **HTTP timeout** (> 5s) → fallback to cache
- **Circuit breaker**: 3 consecutive failures → open circuit
- **Retry**: exponential backoff (max 3 retries)
- **Logging**: all failures + fallback invocations tracked
- **Docker enables**: consistent, reproducible deployments

### 5.3 Token Tracking
Per-request tracking:
- Input tokens (prompt + context)
- Output tokens (response)
- Cost calculation (model-specific rates)
- Aggregated by role, agent, time period
- Used for optimization + chargeback

### 5.4 Service Health Monitoring
Metrics to track:
- n8n: uptime, execution success rate, latency (p50, p95, p99)
- EdgarTools HTTP: availability, response time, cache hit rate
- FastAPI Bridge: request latency, error rate, RBAC denial rate
- Alerts: uptime < 99%, latency > threshold, denial spike

---

## Recommendations (Prioritized)

**Immediate (Week 1)**:
1. ✓ Finalize RBAC matrices (done — see RBAC_Framework_v2.md)
2. Add RBAC checks to FastAPI Bridge (code review + deploy)
3. Define SLA/SLO targets (see Section 2.6)

**Short-term (Week 2–3)**:
4. Implement observability instrumentation (see Observability_Framework.md)
5. Containerize EdgarTools MCP + n8n (see Containerization_Policy.md)
6. Set up audit logging (governance trail + data access)

**Medium-term (Week 4+)**:
7. Deploy containerized services (Kubernetes/ECS)
8. Monitor health + token usage
9. Optimize based on observability data

---

**Status**: Ready for implementation
**Next**: See Observability_Framework.md and Containerization_Policy.md for technical details
