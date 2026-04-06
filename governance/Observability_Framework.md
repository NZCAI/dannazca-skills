# Observability Framework: Nazca System

**Version**: 1.0
**Date**: 2026-03-24

---

## Overview

End-to-end tracing + governance events + token tracking across FastAPI Bridge → Langchain → MCPs.

---

## 1. Trace Propagation Schema

### Correlation ID Flow
```
Request enters FastAPI Bridge:
  ├─ Generate correlation_id (UUID)
  ├─ Extract role from context
  ├─ Pass correlation_id to Langchain
  │
  ├─ Langchain creates child spans per tool call
  │ ├─ tool_id: which MCP (n8n, edgar, postgres)
  │ ├─ operation: what action (query, execute, upload)
  │ ├─ duration_ms: execution time
  │ └─ result: success/failure
  │
  └─ Log to observability backend (CloudWatch)
```

### Span Attributes
| Field | Type | Example |
|-------|------|---------|
| correlation_id | UUID | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| role | string | `data_scientist` |
| agent | string | `ai_data_analyst` (if invoked by agent) |
| tool | string | `mcp_edgartools` |
| operation | string | `fulltext_10k_search` |
| status | enum | `success`, `failure`, `denied` |
| duration_ms | int | `234` |
| timestamp | ISO8601 | `2026-03-24T10:30:45Z` |

---

## 2. Governance Event Logging

### Events to Log

**RBAC Decision**:
```
{
  "event_type": "rbac_decision",
  "timestamp": "2026-03-24T10:30:45Z",
  "correlation_id": "a1b2c3d4-...",
  "role": "data_scientist",
  "tool": "mcp_edgartools",
  "operation": "fulltext_10k_search",
  "decision": "allow",
  "reason": "role has read+execute permission"
}
```

**Data Access**:
```
{
  "event_type": "data_access",
  "timestamp": "2026-03-24T10:30:46Z",
  "correlation_id": "a1b2c3d4-...",
  "role": "data_scientist",
  "action": "s3_upload",
  "resource": "market_data_2026-03-24.csv",
  "size_bytes": 1048576
}
```

**High-Risk Operation**:
```
{
  "event_type": "high_risk_op",
  "timestamp": "2026-03-24T10:30:47Z",
  "correlation_id": "a1b2c3d4-...",
  "role": "ai_data_analyst",
  "tool": "mcp_edgartools",
  "query_type": "insider_holdings",
  "company": "acme_corp",
  "approval_status": "pending"  // if requires approval
}
```

### Logging Destinations
- **RBAC decisions**: CloudWatch (realtime) + S3 (daily archives)
- **Data access**: CloudWatch (realtime) + S3 (2-year retention)
- **High-risk ops**: CloudWatch (alert) + S3 (compliance audit trail)

---

## 3. Token Tracking Instrumentation

### Per-Request Token Count
```
{
  "event_type": "token_usage",
  "timestamp": "2026-03-24T10:30:48Z",
  "correlation_id": "a1b2c3d4-...",
  "agent": "ai_data_analyst",
  "prompt_tokens": 345,
  "completion_tokens": 123,
  "total_tokens": 468,
  "cost_usd": 0.00188,  // model-specific rate
  "model": "claude-opus"
}
```

### Aggregation (Dashboard)
- **Per-agent**: Total tokens + cost + trend (week/month)
- **Per-role**: Usage by team (Data Scientist, ML Trainee, etc.)
- **Per-tool**: Which MCPs consume most tokens
- **Alerts**: Daily cost spike > 20% threshold

---

## 4. Observability Rollout (4 Weeks)

### Week 1: Instrumentation Setup
- [ ] Add correlation ID generation to FastAPI Bridge
- [ ] Configure CloudWatch/S3 logging destinations
- [ ] Define span schema (trace propagation)
- [ ] Add test traces (verify flow end-to-end)

### Week 2: Governance Event Logging
- [ ] Implement RBAC decision logging (FastAPI layer)
- [ ] Implement data access logging (n8n, S3, Edgar)
- [ ] Set up high-risk operation alerts
- [ ] Test logging pipeline

### Week 3: Token Tracking
- [ ] Add token counting to Langchain orchestration
- [ ] Implement per-request token logging
- [ ] Configure cost calculation (model rates)
- [ ] Test token tracking on sample agents

### Week 4: Dashboards & Monitoring
- [ ] Create CloudWatch dashboards (service health, token usage, RBAC denials)
- [ ] Set up alerts (uptime, latency, cost spikes)
- [ ] Document query patterns for team
- [ ] Handoff to ops team

---

## 5. CI/CD Gate: Observability Coverage

**Before deploying new agent/prompt:**
```
Gate: observability-coverage-check
  Input: new agent + its MCP calls

  For each MCP call:
    ├─ Is tool in RBAC matrix? (require yes)
    ├─ Is operation audit-logged? (require yes)
    └─ Is token tracking enabled? (require yes)

  Status: PASS → Deploy
  Status: FAIL → Block merge + require instrumentation
```

---

## 6. Dashboards (Team-Specific)

**For You (Admin)**:
- System health: uptime, latency (p50/p95/p99), errors
- Token usage: total cost/day, trend, breakdown by agent
- RBAC denials: count, spike detection, investigation
- Audit trail: governance changes, high-risk ops

**For Data Scientist**:
- Edgar query success rate
- S3 upload volume + size
- n8n execution success rate
- Token usage (personal)

**For ML Trainee**:
- SageMaker job status
- Lambda invocation latency
- Token usage (personal)
- Failed model training runs

**For Investment Analyst**:
- Data readiness: which datasets ready
- Report availability: latest analysis
- System health: uptime, availability

**For Partners**:
- System health: uptime, performance metrics
- Code review scores: quality trends
- Token usage: overall spend
- Readiness scores: system maturity

---

## 7. Alerting Rules

| Metric | Threshold | Action |
|--------|-----------|--------|
| Service uptime | < 99% | Page on-call |
| RBAC denial rate | > 5%/hour | Investigate access pattern |
| Edgar query latency | > 10s (p99) | Check HTTP timeout, circuit breaker |
| n8n execution failure | > 10%/hour | Check workflow, trigger logs |
| Daily cost | +20% vs baseline | Investigate token usage spike |
| High-risk op | Any | Log + notify Risk owner (you) |

---

## 8. Data Retention Policies

| Data Type | Retention | Destination |
|-----------|-----------|-------------|
| RBAC decisions | 2 years | S3 (archive), CloudWatch (90 days) |
| Data access | 2 years | S3 (archive), CloudWatch (90 days) |
| High-risk ops | 5 years | S3 (compliance), CloudWatch (1 year) |
| Token usage | 1 year | S3 (analytics), CloudWatch (90 days) |
| Service health | 1 year | CloudWatch (360 days) |

---

**Status**: Ready for implementation (Week 1–4 rollout)
**Owner**: You (admin) + Ops team
**Approval**: Required before Week 1 starts
