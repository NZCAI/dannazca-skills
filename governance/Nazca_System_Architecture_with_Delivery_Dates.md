# NAZCA SYSTEM ARCHITECTURE — WITH DELIVERY DATES
## Integrated Modular System (8-Week Sprint Roadmap)

**Date**: March 31, 2026
**Last Updated**: April 10, 2026
**Project Duration**: 8 weeks (Mar 31 - May 25, 2026)
**Overall Status**: Phase 2 (MCP Accessibility) In Progress — Sprint 1 Complete ✅

> **Strategic Note (Apr 10):** Roadmap resequenced to prioritize MCP accessibility over infrastructure completeness. The team's primary interface is Claude — delivering usable tools in Claude now takes precedence over observability dashboards and production hardening. Infrastructure work (PostgreSQL, Celery, SLO monitoring) moves to Phase 4.

---

## SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NAZCA AGENTIC SYSTEM v1.1                           │
│              Modular Architecture with Phased Delivery Timeline              │
└─────────────────────────────────────────────────────────────────────────────┘

                            ┌──── TRIGGER LAYER ────┐
                            │  n8n + Factory CLI    │
                            │  [STATUS: In Progress]│
                            │  [SHIP: Apr 13, 2026] │
                            └───────────┬────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
        ▼                               ▼                               ▼
   Investment Team            Data Science Team                  CRM/Webhooks
   (CLI/Chat)                 (CLI/Chat)                         (Automation)
   [READY: Now]               [READY: Now]                       [READY: Now]
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        │
                            ┌───────────▼────────────┐
                            │  AUTOMATION & ORCHESTRATION LAYER  │
                            │                        │
                            │  ┌──────────────────┐  │
                            │  │ n8n Automation   │  │  [STATUS: Planned]
                            │  │ [SHIP: May 11]   │  │
                            │  └──────────────────┘  │
                            │                        │
                            │  ┌──────────────────┐  │
                            │  │Factory Macro-    │  │  [STATUS: In Progress]
                            │  │Orchestrator      │  │  [SHIP: Apr 13]
                            │  │(Custom Droids)   │  │
                            │  └──────────────────┘  │
                            │                        │
                            │  ┌──────────────────┐  │
                            │  │LangChain Micro-  │  │  [STATUS: In Progress]
                            │  │Orchestrator      │  │  [SHIP: Apr 13]
                            │  │(Agents)          │  │
                            │  └──────────────────┘  │
                            │                        │
                            └───────────┬────────────┘
                                        │
                            JSON-RPC via stdio/HTTP
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │              │  │              │  │              │
            │ FastAPI      │  │ EdgarTools   │  │ Workflow     │
            │ Interop      │  │ MCP Server   │  │ Engines      │
            │ Bridge       │  │              │  │ (R + Python) │
            │              │  │ [STATUS:     │  │              │
            │ [STATUS:     │  │ In Progress] │  │ [STATUS:     │
            │ In Progress] │  │              │  │ Planned]     │
            │              │  │ [SHIP:       │  │              │
            │ [SHIP:       │  │ Apr 13]      │  │ [SHIP:       │
            │ Apr 27]      │  │              │  │ Apr 27]      │
            │              │  └──────────────┘  │              │
            └──────────────┘                    └──────────────┘
                    │                                   │
                    │            ┌──────────────────────┘
                    │            │
                    ▼            ▼
            ┌──────────────────────────────────┐
            │                                  │
            │  API BRIDGE LAYER (RBAC)         │
            │                                  │
            │  FastAPI headless router         │
            │  [STATUS: In Progress]           │
            │  [SHIP: Apr 27, 2026]            │
            │                                  │
            │  ✓ RBAC enforcement              │
            │  ✓ Correlation ID propagation    │
            │  ✓ Token tracking                │
            │  ✓ Error handling                │
            │                                  │
            └──────────────┬───────────────────┘
                           │
                    Secure Data & Computation Layer
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌────────┐        ┌────────┐        ┌────────┐
    │ BRMS   │        │ GUR    │        │ KPI    │
    │ Models │        │Database│        │Database│
    │ .rds   │        │        │        │        │
    │files   │        │        │        │        │
    └────────┘        └────────┘        └────────┘
        │                  │                  │
        │                  ▼                  │
        │            ┌────────────┐           │
        │            │   Market   │           │
        │            │   Database │           │
        │            │ (Pitchbook)│           │
        │            └────────────┘           │
        │
        └─────────────────┬────────────────────┘
                          │
                    Persistent Storage (Aurora RDS + S3)
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌─────────┐    ┌─────────┐    ┌─────────────┐
    │ LAVCA   │    │ EDGAR   │    │ Pitchbook   │
    │ Data    │    │ Public  │    │ ETF Data    │
    │ (5,543  │    │ Data    │    │             │
    │ deals)  │    │ (46     │    │ [SHIP:      │
    │         │    │ tickers)│    │ May 11]     │
    │[READY]  │    │         │    │             │
    │         │    │[SHIP:   │    └─────────────┘
    │         │    │Apr 13]  │
    │         │    │         │
    └─────────┘    └─────────┘
```

---

## DELIVERY TIMELINE BY LAYER

### PHASE 1: Foundation (Sprint 1 - Weeks 1-2)
**Delivery Date: April 13, 2026** — ✅ SHIPPED Apr 9 (early)

| Component | Status | MVP | Validation | Ship Date |
|-----------|--------|-----|-----------|-----------|
| **RBAC + JWT Enforcement** | ✅ Complete | Apr 6 | Apr 9 | Apr 9 |
| **LangGraph 12-Agent Graph** | ✅ Complete (mock outputs) | Apr 6 | Apr 9 | Apr 9 |
| **51/51 Tests Passing** | ✅ Complete | Apr 6 | Apr 9 | Apr 9 |
| **FastAPI Docker Image → ECR** | ✅ Complete | Apr 7 | Apr 9 | Apr 9 |
| **EdgarTools HTTP Client** | ✅ Complete | Apr 6 | Apr 9 | Apr 9 |

**Deliverable**: FastAPI Bridge fully containerized, tested, and pushed to ECR — ready for ECS deployment

---

### PHASE 2: MCP Accessibility — Team Enablement (Sprint 2 - Weeks 3-4)
**Delivery Date: April 27, 2026** — 🔄 In Progress
**Goal: Every team member has EdgarTools and Trading Agents available in Claude**

| Component | Status | MVP | Validation | Ship Date |
|-----------|--------|-----|-----------|-----------|
| **FastAPI on ECS Fargate** | ✅ Complete (Apr 9, early) | Apr 9 | Apr 9 | Apr 9 |
| **CloudWatch Logs (/ecs/nazca-fastapi)** | ✅ Complete (Apr 9) | Apr 9 | Apr 9 | Apr 9 |
| **EdgarTools MCP behind ALB** | ✅ Complete (Apr 10) | Apr 10 | Apr 10 | Apr 10 |
| **FastAPI Bridge — MCP layer** | Planned | Apr 13 | Apr 17 | Apr 20 |
| **Team Claude Desktop configs distributed** | Planned | Apr 20 | Apr 22 | Apr 22 |

**Deliverable**: Team connects to Nazca tools from Claude using a one-line config. Edgar queries and Trading Agent analysis available as MCP tools.

---

### PHASE 3: Platform Expansion (Sprint 3 - Weeks 5-6)
**Delivery Date: May 11, 2026**
**Goal: Additional MCP tools + rate limiting + observability + storage foundation**

| Component | Status | MVP | Validation | Ship Date |
|-----------|--------|-----|-----------|-----------|
| **Additional MCPs (pattern established)** | Planned | May 3 | May 7 | May 11 |
| **Trading Agent rate limiting + per-role quotas** | Planned | May 3 | May 7 | May 11 |
| **n8n Automation Container** | Planned | May 4 | May 8 | May 11 |
| **Governance Event Logging** | Planned | May 4 | May 8 | May 11 |
| **CloudWatch Dashboards (team roles)** | Planned | May 4 | May 8 | May 11 |
| **Token Tracking per-request** | Planned | May 5 | May 9 | May 11 |

**Deliverable**: Governed, rate-limited MCP access for the team + full observability live

---

### PHASE 4: Production Hardening + Knowledge Base (Sprint 4 - Weeks 7-8)
**Delivery Date: May 25, 2026**
**Goal: Production-grade infrastructure + storage layer that turns usage into institutional memory**

| Component | Status | MVP | Validation | Ship Date |
|-----------|--------|-----|-----------|-----------|
| **PostgreSQL migration (replace SQLite)** | Planned | May 18 | May 22 | May 25 |
| **Redis TTL cache (EDGAR + agent results)** | Planned | May 18 | May 22 | May 25 |
| **Celery + Redis job queue** | Planned | May 18 | May 22 | May 25 |
| **Time-series knowledge base (query storage)** | Planned | May 19 | May 23 | May 25 |
| **Multi-Replica Deployment (3x)** | Planned | May 19 | May 23 | May 25 |
| **Auto-Scaling + SLO Monitoring** | Planned | May 20 | May 24 | May 25 |
| **Cost Alerts + Billing Controls** | Planned | May 20 | May 24 | May 25 |

**Deliverable**: Resilient production system + every team query stored and reusable by future agents

> **Storage architecture note**: Two-tier approach. Redis handles hot queries with TTL (stock prices: 1h, company profiles: 7d, SEC filings: 30d). PostgreSQL is the permanent time-series store — financial snapshots, agent analysis outputs, EDGAR results — that builds into a proprietary knowledge base over time. SQLite remains intentionally until this phase: it works fine before the team generates data worth keeping, and the migration is a single `DATABASE_URL` swap plus schema migration.

---

## WORKFLOW DELIVERY TIMELINE

### Workflow 5A (Yahoo Finance Path)
**Status**: Design Phase
**MVP Date**: April 13, 2026 (endpoints live)
**Validation Date**: April 20, 2026 (tested with sample data)
**Full Ship**: April 27, 2026
**Features at Ship**: IRR prediction, RBAC controlled, audit logged, error handling with fallbacks

### Workflow 5B (EDGAR Path)
**Status**: Design Phase
**MVP Date**: April 20, 2026 (endpoints live)
**Validation Date**: April 25, 2026 (EDGAR integration tested)
**Full Ship**: April 27, 2026
**Features at Ship**: IRR + fundamentals, EdgarTools integrated, token tracking, error recovery

### Market Analysis (Sector Waves)
**Status**: Design Phase
**MVP Date**: May 5, 2026 (phase 1-3 async)
**Validation Date**: May 9, 2026 (correlations validated)
**Full Ship**: May 11, 2026
**Features at Ship**: 5-phase async, ZIP output, phase-level error recovery, cost tracking

---

## DATA SOURCES INTEGRATION TIMELINE

| Data Source | Integration | Status | Dependency | Ship Date |
|---|---|---|---|---|
| **LAVCA** | CSV/n8n scraper | Ready | S1 (RBAC) | Apr 13 |
| **EdgarTools MCP** | JSON-RPC calls | In Progress | S1 Container | Apr 13 |
| **Yahoo Finance** | R quantmod package | Planned | S2 (5A workflow) | Apr 27 |
| **Aurora RDS** | SQL fallback | Planned | S2 (FastAPI Bridge) | Apr 27 |
| **Pitchbook** | Excel upload | Planned | S3 (Market Analysis) | May 11 |

---

## SYSTEM INTEGRATION CHECKPOINTS

### Checkpoint 1: Foundation (Apr 13) — ✅ COMPLETE (Apr 9)
- ✅ RBAC + JWT enforcement at FastAPI entry point
- ✅ LangGraph 12-agent trading graph wired end-to-end (mock outputs)
- ✅ Correlation ID propagation middleware
- ✅ 51/51 unit tests passing (auth, RBAC, validation, workflows)
- ✅ FastAPI Docker image built (linux/amd64) + pushed to ECR
- ✅ EdgarTools HTTP client integrated

### Checkpoint 2: MCP Accessibility (Apr 27) — 🔄 In Progress
- ✅ FastAPI container on ECS Fargate — healthy (Apr 9)
- ✅ CloudWatch Logs streaming (/ecs/nazca-fastapi)
- ✅ EdgarTools MCP behind ALB — 13 tools live, team-accessible from Claude (Apr 10)
- ✅ Claude Desktop config template distributed (mcp-config.template.json)
- ◻ FastAPI Bridge MCP layer — Trading Agents callable from Claude (next session)
- ◻ Team Claude Desktop configs verified end-to-end

### Checkpoint 3: Platform Expansion (May 11)
- ◻ Additional MCP tools wired via established pattern
- ◻ n8n container running
- ◻ Governance event logging live
- ◻ CloudWatch dashboards per team role
- ◻ Token tracking per-request

### Checkpoint 3: Platform Expansion (May 11)
- ◻ Trading Agent concurrent job limit + per-role daily quotas
- ◻ Additional MCPs added via established pattern
- ◻ n8n container running
- ◻ Governance event logging live
- ◻ CloudWatch dashboards per team role
- ◻ Token tracking per-request

### Checkpoint 4: Production Ready + Knowledge Base (May 25)
- ◻ PostgreSQL migration (replace SQLite)
- ◻ Redis TTL cache — EDGAR results, agent outputs
- ◻ Time-series knowledge base live — all team queries stored
- ◻ Celery + Redis job queue
- ◻ 3x replicas + auto-scaling per service
- ◻ SLO monitoring live (99.5% EDGAR, 99.9% FastAPI)
- ◻ Cost alerts configured

---

## PROGRESS INDICATORS

### Current Sprint (S2: Apr 9 - Apr 27) — MCP Accessibility
```
[██████░░░░░░░░░░░░░░░░░░░░░░░░░░] ~40% complete
   ├─ FastAPI on ECS Fargate ........ 100% ✅ (live Apr 9)
   ├─ CloudWatch Logs ............... 100% ✅ (live Apr 9)
   ├─ EdgarTools MCP + ALB .......... 100% ✅ (live Apr 10, 13 tools)
   ├─ FastAPI Bridge MCP layer ....... 0% (next session)
   └─ Team Claude Desktop configs .... 50% (template ready, distribution pending)
```

### Overall Project (8 weeks)
```
[████████░░░░░░░░░░░░░░░░░░░░░░░░] Week 2 of 8 (~25%)

Sprint Breakdown:
  S1 (Apr 13) .... [██████████] Foundation ✅ COMPLETE
  S2 (Apr 27) .... [████░░░░░░] MCP Accessibility 🔄 In Progress
  S3 (May 11) .... [░░░░░░░░░░] Platform Expansion
  S4 (May 25) .... [░░░░░░░░░░] Production Hardening
```

---

## CRITICAL PATH

```
S1: Foundation — FastAPI + LangGraph + ECS
  ↓ (dependency)
S2: MCP Accessibility — EdgarTools in Claude + Trading Agents in Claude
  ↓ (dependency)
S3: Platform Expansion — Additional MCPs + n8n + Observability
  ↓ (dependency)
S4: Production Hardening — PostgreSQL + Celery + Scale + SLO
  ↓
SHIP: May 25, 2026 ✓
```

Team value delivered at S2 — every subsequent sprint adds capability and resilience

---

## KEY DATES

| Milestone | Date | Status |
|-----------|------|--------|
| Project Kickoff | Mar 31, 2026 | ✅ Complete |
| Phase 1 Ship (Foundation) | Apr 13, 2026 | ✅ Complete (shipped Apr 9) |
| Phase 2 Ship (MCP Accessibility) | Apr 27, 2026 | 🔄 In Progress |
| **Team using tools in Claude** | **Apr 27, 2026** | **🎯 KEY MILESTONE** |
| Phase 3 Ship (Platform Expansion) | May 11, 2026 | 📅 Scheduled |
| Phase 4 Ship (Production Hardening) | May 25, 2026 | 📅 Scheduled |
| **System Operationally Ready** | **May 25, 2026** | **🎯 TARGET** |

---

## DEPENDENCIES & RISKS

**Critical Dependencies**:
- RBAC implementation (blocks all downstream)
- EdgarTools container (blocks EDGAR workflows)
- FastAPI bridge (routes all workflows)

**Risk Mitigation**:
- Parallel tracks: foundation (RBAC) independent from observability (logging)
- Circuit breaker pattern for EdgarTools (fallback to cache)
- Token tracking in S3 (no dependency on real-time storage)

**Confidence Level**: High (foundation infrastructure mature, modular approach reduces interdependencies)

---

**Related Documents**:
- `Nazca_Governance_Blueprint_v1.md` — Governance & delivery timeline (Sections 5-6)
- `Nazca_Technical_Specification_v2.md` — Technical architecture (Sections 7-8)
- `Data_Science_Workflow_Integration_Framework.md` — API specs & implementation checklist

**Last Updated**: April 9, 2026
