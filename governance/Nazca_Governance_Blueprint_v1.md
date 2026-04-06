# Product Definition Review: Nazca Agentic System v1.0

**Date**: 2026-03-25
**Last Updated**: 2026-03-30
**Owner**: Admin
**Status**: Phase 1 (Foundation) — Ready for Implementation
**Related Document**: Nazca_Technical_Specification_v2.md (Technical Architecture & Specification)
**Audience**: Team leads, Operations, Governance owners, Delivery stakeholders

---

## Executive Summary

Nazca is a **data-centric, multi-team AI orchestration system** combining:
- **n8n** automation engine (workflow triggers)
- **FastAPI Bridge MCP** (routing + RBAC enforcement)
- **Langchain orchestration** (agent chains + governance)
- **SEC Edgar MCP** (financial data access)
- **Postgres/Aurora** (persistent state)
- **Factory.ai Shared Skills** (standardized prompts)
- **Prompt repositories** (investment + technical frameworks)

**Vision**: Enable teams to collaborate safely on data analysis, automation, and AI-driven decision-making with automatic audit logging, role-based access, and token-efficient context management.

**Ship Timeline**: 8 weeks, 4 bi-weekly sprints (see roadmap below).

---

## 1. Core Architecture

### 1.1 System Flow

```
User Request
  ↓
FastAPI Bridge (RBAC enforcement + routing)
  ↓
Langchain Orchestration (context + governance + trace propagation)
  ├─ n8n (automation triggers)
  ├─ mcp-edgartools (SEC filings)
  ├─ Postgres/Aurora (data queries)
  └─ S3 (artifact storage)
  ↓
Governance Event Logging (audit trail, token tracking)
  ↓
CloudWatch + S3 (observability + compliance)
```

### 1.2 Key Components

| Component | Purpose | Containerized | Owner |
|-----------|---------|---|---|
| FastAPI Bridge | MCP routing + RBAC | Yes (S2) | You |
| n8n | Automation engine | Yes (S3) | Automations Trainee |
| EdgarTools MCP | SEC filing queries | Yes (S1) | Data Scientist |
| Postgres/Aurora | Persistent state | N/A (managed RDS) | You |
| S3 | Artifacts + logs | N/A (AWS managed) | You |

### 1.3 Team Roles (RBAC)

| Role | Access Level | Tools | Phase |
|------|---|---|---|
| Admin (you) | Full AWS + PRD | All | S1 |
| Data Scientist | MCP + S3 uploads | EdgarTools, Postgres, n8n | S1 |
| ML Trainee (2x) | Lambda + SageMaker | Compute + data | S3 |
| Automations Trainee (2x) | n8n workflows | Workflow builder | S1 |
| Investment Analyst | Read-only UI | Dashboard only | Post-S2 |
| Partners | Health/scores/tokens | Analytics read-only | Post-S4 |
| **Agents**: |  |  |  |
| Product Manager | Roadmap + decisions | Governance docs | S2 |
| Code-Reviewer | PR approvals | Git + review tools | Ongoing |
| AI-Data-Analyst | Edgar + analytics | EdgarTools + Dropbox | S1 |

---

## 2. Governance & Safety

### 2.1 RBAC Framework

**Enforcement Point**: FastAPI Bridge layer (entry point for all requests)
**Principle**: Deny-by-default — access only granted explicitly
**References**:
- `RBAC_Framework_v2.md` (139 lines)
- `team-rbac-tool-matrix.yaml` (189 lines)
- `agent-rbac-tool-matrix.yaml` (128 lines)
- `RBAC_Implementation_Guide_v2.md` (160 lines)

### 2.2 Observability & Audit

**Governance Events Tracked**:
- Data access (who queried what, when, why)
- RBAC decisions (access allowed/denied)
- Tool usage (n8n workflows triggered, API calls made)
- Token consumption (per-request tracking via Langchain instrumentation)

**Log Destinations**:
- CloudWatch (real-time dashboards)
- S3 (2-year archive for compliance)
- Correlation IDs (trace end-to-end request flow)

**Reference**: `Observability_Framework.md` (195 lines)

### 2.3 Containerization Strategy

**Services**: EdgarTools HTTP, FastAPI Bridge, n8n
**Health Checks**: Liveness + readiness + startup probes
**Resilience**: Circuit breaker pattern (fallback to cache if EdgarTools times out)
**SLOs**:
- EdgarTools: 99.5% uptime, < 5s response
- FastAPI: 99.9% uptime, < 100ms latency
- n8n: 99% uptime, < 30s execution

**Reference**: `Containerization_Policy.md` (316 lines)

---

## 3. Shared Skills Integration

**Objective**: Eliminate prompt sprawl. Standardize team behaviors using Factory.ai skills.

### 3.1 Available Skills

| Skill | Purpose | When to Use |
|-------|---------|---|
| **solid** | Code quality + TDD | Writing new Python functions, refactoring |
| **tracer-bullets** | Feature strategy | Starting new integrations (e.g., n8n → DB) |
| **humanizer** | Documentation | PRDs, stakeholder comms, team docs |
| **data-querying** | Safe analytics | Aurora/RDS metrics for investment team |
| **product-management** | Planning & scoping | Breaking down business requests |
| **universal-tester** | QA/stress-testing | Pre-deployment validation of agents |

### 3.2 EdgarTools MCP

**What**: SEC filing analysis tool (10-K/10-Q/8-K, insider transactions, trends, monitoring)
**Where**: `tools/edgartools-mcp/` in shared skills repo
**Integration**: FastAPI Bridge routes Edgar queries → mcp-edgartools container (S1)
**Installation**: One-prompt setup in `tools/edgartools-mcp/one-prompt-installation-guide.md`

---

## 4. Prompt Repository Architecture

### 4.1 Technical Prompt Repository

**Purpose**: Standardize internal product + feature development, stack maintenance
**Scope**: Code generation, refactoring, deployment, testing
**Integration**: Langchain + Claude agents use these prompts for consistent behavior
**Structure** (to be defined):
```
/prompts/technical/
  ├─ feature-development/   (tracer-bullets methodology)
  ├─ code-review/           (RBAC + security checks)
  ├─ deployment/            (containerization, health checks)
  ├─ testing/               (universal-tester framework)
  └─ stack-maintenance/     (dependency updates, migrations)
```

**Implementation Timeline**: Weeks 5–6 (S3) alongside n8n container + token tracking

### 4.2 Investment Prompt Repository

**Purpose**: Standardize analysis outcomes, tool workflows
**Scope**: Edgar data extraction, metric aggregation, report generation
**Integration**: AI-Data-Analyst agent + Partners dashboard
**Structure** (to be defined):
```
/prompts/investment/
  ├─ edgar-analysis/        (10-K/10-Q extraction)
  ├─ metrics-aggregation/   (financial calculations)
  ├─ report-generation/     (output formatting)
  └─ trend-monitoring/      (anomaly detection)
```

**Implementation Timeline**: Week 7–8 (S4) post-containerization, focus on SLO delivery

---

## 5. 8-Week Technical Roadmap

**Format**: 4 bi-weekly sprints with measurable ships per sprint

### Sprint 1 (Weeks 1–2): Foundation — RBAC + EdgarTools
**Ship**: RBAC enforcement live + EdgarTools containerized
**Deliverables**:
- [ ] FastAPI Bridge RBAC checks at entry point (dev environment)
- [ ] EdgarTools Dockerfile + health checks complete
- [ ] Build & push EdgarTools image to ECR
- [ ] Deploy 1 replica to ECS test environment
- [ ] Load test: 100 queries/sec baseline latency/errors
- [ ] Context-manager skill + project-context.yaml live

**Milestones**:
- W1 EOD: Dockerfile + ECR image complete, load tested
- W2 EOD: FastAPI RBAC checks + EdgarTools in test, CI/CD gates configured

**Success Criteria**: RBAC + EdgarTools both passing automated tests, context-manager callable

---

### Sprint 2 (Weeks 3–4): Observability + FastAPI Container
**Ship**: Governance event logging + CloudWatch dashboards + FastAPI containerized
**Deliverables**:
- [ ] Governance event logging (RBAC + data access) → CloudWatch + S3
- [ ] Trace propagation via correlation IDs (end-to-end request tracing)
- [ ] CloudWatch dashboards operational (latency, errors, RBAC decisions)
- [ ] FastAPI Bridge Dockerfile + health checks complete
- [ ] FastAPI container integrated with EdgarTools routing
- [ ] Deploy 1 replica to test, load test (500 req/sec)

**Milestones**:
- W3 EOD: Trace propagation + governance event logging live
- W4 EOD: FastAPI Dockerfile complete, dashboards operational

**Success Criteria**: Observability events flowing to CloudWatch, FastAPI container healthy + routable

---

### Sprint 3 (Weeks 5–6): n8n Container + Token Tracking
**Ship**: n8n containerized + token tracking per-request + cost alerts + prompt repos planned
**Deliverables**:
- [ ] n8n Dockerfile (Postgres config, workflow mounts) complete
- [ ] Build & push to ECR, deploy 1 replica to test
- [ ] Migrate test workflows to container-based execution
- [ ] Token tracking instrumented in Langchain (per-request cost calculation)
- [ ] Daily cost spike alerts configured (>20% threshold)
- [ ] Circuit breaker pattern for EdgarTools fallback tested
- [ ] **Prompt repos architecture designed** (technical + investment structure defined, not implemented)

**Milestones**:
- W5 EOD: n8n Dockerfile tested locally, token counting integrated
- W6 EOD: n8n workflows in test, cost tracking live

**Success Criteria**: n8n workflows executing in containers, token costs tracked + alerted

---

### Sprint 4 (Weeks 7–8): Production Scale + Hardening
**Ship**: All services at scale + SLO monitoring live + team handoff complete
**Deliverables**:
- [ ] Scale EdgarTools to 3 replicas + auto-scaling enabled
- [ ] Scale FastAPI to 2 replicas + auto-scaling enabled
- [ ] Scale n8n to 2 replicas (workflow redundancy)
- [ ] Deploy all to AWS Fargate production environment
- [ ] Enable circuit breaker + fallback for EdgarTools
- [ ] SLO monitoring + alerting live (Slack/PagerDuty integrated)
- [ ] Rollback procedure tested + verified
- [ ] Operational runbook documented for ops team
- [ ] Team training completed + handoff signed off
- [ ] **Prompt repositories seeded** (initial templates + examples committed)

**Milestones**:
- W7 EOD: Production deployment at scale, auto-scaling policies enabled
- W8 EOD: SLO dashboard live, team operational

**Success Criteria**: All services healthy at scale, SLOs being met, team ready for maintenance

---

## 6. Dependencies & Sequencing

### Critical Path
1. **RBAC enforcement** (S1) → enables multi-team deployment
2. **EdgarTools containerization** (S1) → validates MCP federation pattern
3. **Observability framework** (S2) → required for production compliance
4. **FastAPI container** (S2) → routes all requests, controls access
5. **Token tracking** (S3) → required for cost governance + billing
6. **Prompt repositories** (S3–S4 planning) → enable consistent agent behavior

### Parallel Tracks
- **Container infrastructure** (S1–S4): Build + test containerized services
- **Governance framework** (S1–S2): RBAC + observability + audit trails
- **Agent orchestration** (ongoing): Langchain + shared skills integration
- **Architecture documentation** (ongoing): Keep PDR/roadmap current

---

## 7. File Structure & Deliverables

**Location**: `/Users/dannazca/Factory/dannazca-skills/governance/`

| Document | Lines | Purpose |
|----------|-------|---------|
| `RBAC_Framework_v2.md` | 139 | Role definitions + principles |
| `team-rbac-tool-matrix.yaml` | 189 | Explicit role→tool mappings |
| `agent-rbac-tool-matrix.yaml` | 128 | Agent role→tool mappings |
| `RBAC_Implementation_Guide_v2.md` | 160 | How to enforce RBAC at FastAPI |
| `Containerization_Policy.md` | 316 | Docker strategy, SLOs, resilience |
| `Observability_Framework.md` | 195 | Trace propagation, event logging, token tracking |
| `8-Week-Technical-Roadmap.md` | ~350 | Detailed sprint breakdown |
| `project-context.yaml` | ~190 | Project state file (version-controlled) |
| `context-manager/main.py` | ~120 | Skill implementation |
| `context-manager/SKILL.md` | ~70 | Skill documentation |
| `Architectural_Feedback_v2.md` | 295 | Design decisions + tradeoffs |
| **Nazca_Governance_Blueprint_v1.md** (this file) | ~400 | Product definition + shared skills integration |

**Presentation**: `Nazca_Agentic_System_Deck.pptx`
- Slide 1: System overview
- Slide 2: Architecture diagram
- Slide 3: Key features
- Slide 4: FastAPI Bridge + MCPs
- **Slide 5**: 8-Week Gantt roadmap (updated ✓)
- **Slide 6**: Governance & Safety (new ✓)

---

## 8. Relationship to Nazca_Technical_Specification_v2

**Related Document**: Nazca_Technical_Specification_v2.md (Technical Architecture & Specification)
**Last Synced**: March 30, 2026
**Sync Strategy**: Both documents updated together for major changes

### Purpose of Each Document

**Nazca_Governance_Blueprint_v1.md** (this document) is the **Governance & Delivery Blueprint**. It answers: "WHO does WHAT by WHEN, with what oversight?"

- **Source of Truth for:**
  - RBAC framework and team role definitions
  - Observability, event logging, and audit trail requirements
  - Audit and compliance controls
  - Factory.ai shared skills integration
  - 8-week delivery roadmap with sprint milestones
  - Risk mitigation and contingency planning
  - Success metrics and project governance

- **Primary Audience:** Team leads, operations, governance owners, delivery stakeholders

**Nazca_Technical_Specification_v2.md** is the **Technical Architecture & Specification**. It answers: "HOW do we build this, what are the technical dependencies, and what workflows does it support?"

- **Source of Truth for:**
  - System components and their integration (FastAPI, LangChain, MCPs, databases)
  - Technical workflows (Pipeline 5A, Pipeline 5B, GUR Extraction) with detailed phases and data flows
  - Software requirements and dependency matrices (R versions, Python, brms, etc.)
  - Architecture decisions and technical trade-offs
  - Use cases and data flows for different personas (Data Scientists, Investment Team)
  - System requirements and tool dependencies

- **Primary Audience:** Data Scientists, engineers, architects, technical implementation team

### How to Cross-Reference

When working on governance changes, refer to this document (Nazca_Governance_Blueprint_v1.md).

When implementing workflows or integrating tools, refer to **Nazca_Technical_Specification_v2 Sections 7.1-7.3** for detailed workflow specifications.

When setting up observability or RBAC enforcement, refer to **Nazca_Governance_Blueprint_v1 Section 2** for governance requirements.

### Document Synchronization

Both documents share:
- Component naming (Tool, Product, Workflow, System Requirement, Engine — see Nomenclature Standards spreadsheet)
- System version numbers (R 4.4.1, Python 3.14.3, brms 2.23.0+, etc.)
- Workflow naming (Pipeline 5A, Pipeline 5B, GUR Extraction)
- Team role definitions and RBAC matrix

If either document requires updates to these shared elements, both must be synchronized to maintain consistency.

---

## 9. Data Science Workflow Governance — LEAN

Three standardized workflows (5A, 5B, Market Analysis) operate through unified FastAPI gateway with end-to-end RBAC, audit logging, and token tracking. **See `Nazca_Governance_Blueprint_v1_extended.md` for detailed governance policies.**

### 9.1 Execution Model

| Workflow | Type | Runtime | Execution |
|---|---|---|---|
| **5A (Yahoo)** | IRR prediction (entry/pre-seed) | R + Yahoo Finance | Sync ~5 min |
| **5B (EDGAR)** | IRR prediction (follow-on) | R + EdgarTools MCP | Sync ~10 min |
| **Market Analysis** | Sector waves correlation | Python (5 phases) | Async ~5-7 min |

**API Pattern:**
- Trigger: `POST /api/v1/workflows/{5a|5b|market-analysis}` → `202 Accepted` + job_id
- Poll: `GET /api/v1/jobs/{job_id}` → status + progress (0-100%)
- Download: `GET /api/v1/jobs/{job_id}/export` → Excel/ZIP/JSON
- Correlation ID tagged on all operations for end-to-end tracing

### 9.2 RBAC Matrix

| Role | 5A | 5B | Market | Edgar | Notes |
|------|----|----|--------|-------|-------|
| **admin** | ✓ | ✓ | ✓ | ✓ | Full access |
| **data_scientist** | ✓ | ✓ | ✓ | ✓ | Execute + upload |
| **ai_data_analyst** | ✗ | ✓* | ✓* | ✓ | EDGAR only (no BRMS) |
| **investment_analyst** | ✗ | ✗ | ✗ | ✓ (ad-hoc) | Read-only consumer |
| **ml_trainee** | ✗ | ✗ | ✗ | ✗ | No prod access |
| **automations_trainee** | ✗ | ✗ | ✗ | ✗ | GUR extraction only |

**Enforcement:** FastAPI middleware checks RBAC before execution. Invalid roles → 403 Forbidden + audit log.

### 9.3 Data Source Policy

All credentials stored in AWS Secrets Manager (never embedded). Access via MCP or secure environment variables.

| Source | 5A | 5B | Market | Auth |
|--------|----|----|--------|------|
| **LAVCA** | ✓ | ✓ | ✓ | S3 read |
| **EdgarTools MCP** | ✗ | ✓ | ✓ | Secret Manager |
| **Yahoo Finance** | ✓ | ✗ | ✗ | Public |
| **Pitchbook** | ✗ | ✗ | ✓ | S3 read |
| **Aurora RDS** | Fallback | Fallback | Fallback | Secret Manager |

### 9.4 Observability & Audit

**Events Logged:**
- Trigger: {timestamp, role, workflow, correlation_id, params}
- Phase complete: {phase, duration_ms, tokens, status}
- Data access: {source, query_type, records, latency_ms}
- RBAC decision: {role, endpoint, allow/deny, reason}
- Output: {file_path, size, checksum}

**Retention:** CloudWatch (30 days) + S3 archive (2 years)
**Correlation ID:** Propagated end-to-end (R scripts, EDGAR calls, S3 writes)

### 9.5 Cost Tracking

- Per-workflow: tokens, EDGAR calls, compute time, data transfer
- Daily summary by workflow + role
- Weekly alert if threshold exceeded

### 9.6 Error Handling

| Failure | Fallback | Response |
|---------|----------|----------|
| LAVCA unavailable | Use cached data (< 24h old) | Warning + age |
| EDGAR timeout | 5B: portfolio medians; Market: skip phase | partial_complete |
| R script error | Return error + partial results | 500 + trace_id |
| S3 write fail | Local temp storage + retry | Warning + manual upload |
| RBAC violation | None (security boundary) | 403 Forbidden |

**Retry:** Transient errors (timeout) retry 2x exponential backoff; permanent errors (auth) fail immediately.

### 9.7 Data Privacy

- **Output Classification:** Rankings (investment-sensitive) → fund managers/investors only; Reports (strategic) → Nazca team + LPs; Artifacts (technical) → Data Scientists only
- **Encryption:** All outputs encrypted at rest (S3 SSE-KMS), access controlled via AWS IAM
- **Audit Access:** Admin full access; Investment Team summary only; monthly compliance report auto-generated

### 9.8 Governance Checklist

**Pre-Deployment:**
- [ ] RBAC matrix validated for all roles
- [ ] Error handling tested (LAVCA, EDGAR, S3 failures)
- [ ] Correlation ID propagation verified end-to-end
- [ ] Cost estimate reviewed
- [ ] Audit logging verified (CloudWatch within 60s)

**Monthly Review:**
- [ ] Execution statistics (count, duration, error rate)
- [ ] Cost trends (tokens, API calls, compute)
- [ ] RBAC violations detected
- [ ] Data source uptime (LAVCA, EDGAR, Pitchbook)

---

## 11. Next Steps (Post-Phase 1)

### Immediate (This Week)
1. ✓ Update presentation slides (Slide 6 + Slide 5 updated)
2. ✓ Create PDR with shared skills integration
3. Convert PPTX to Google Slides for team sharing
4. Review PDR with Product Manager agent (if governance approved)

### Phase 2 (Sprint Planning)
1. **Week 1**: Kick off S1 (FastAPI RBAC + EdgarTools Docker)
2. **Week 3**: Begin S2 (Observability framework deployment)
3. **Week 5**: Plan prompt repository architecture in detail
4. **Week 7**: Production scale deployment (S4)

### Deferred Decisions
1. **GitHub ownership** — Determine if you or another agent manages repo (next session)
2. **Prompt repo details** — Define branching strategy, approval gates (S3 planning phase)
3. **Product roadmap** — After Phase 1 complete, align to business priorities

---

## 12. Success Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| RBAC enforcement coverage | 100% of FastAPI routes | S1 W2 |
| EdgarTools uptime | 99.5% | S4 W7 |
| Observability coverage | All services traced | S2 W4 |
| Token tracking accuracy | 100% of requests | S3 W6 |
| Team readiness | All roles trained | S4 W8 |
| Code quality (solid skill) | 0 linting errors on merged PRs | Ongoing |
| Workflow governance compliance | 100% of executions logged + RBAC enforced | S2 W3 |
| Data source monitoring | Uptime > 99% (LAVCA, EDGAR, Pitchbook) | Ongoing |

---

## 13. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| EdgarTools HTTP timeout | User experience | Circuit breaker pattern + cache fallback |
| Containerization delays | Schedule slip | Parallel RBAC track (independent) |
| RBAC enforcement overhead | Latency | FastAPI layer optimization + monitoring |
| Token cost overruns | Budget impact | Daily spike alerts + prompt repo review |
| Team onboarding delays | S1 slips | shared skills + context-manager reduce friction |
| Workflow execution failures | Data inconsistency | Correlation ID tracing + audit log review + manual recovery |
| Data source outages | Blocked workflows | Fallback to cached data + skip-phase strategy |

---

## 14. Approval & Sign-Off

**Document Owner**: Admin
**Last Updated**: 2026-03-25
**Status**: Ready for Implementation

**Approvals Required**:
- [ ] Architecture review (you)
- [ ] Team readiness (all roles)
- [ ] Security review (RBAC + audit trail)

**Next PDR Revision**: Post-Sprint 2 (Week 4 completion)

---

**Attached**:
- Shared Skills Repository: https://github.com/NZCD5L/dannazca-skills
- Presentation: `/Users/dannazca/Downloads/Nazca_Agentic_System_Deck.pptx` (Slides 5-6 updated)
