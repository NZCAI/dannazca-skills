# NAZCA SYSTEM ARCHITECTURE — WITH DELIVERY DATES
## Integrated Modular System (8-Week Sprint Roadmap)

**Date**: March 31, 2026
**Project Duration**: 8 weeks (Mar 31 - May 25, 2026)
**Overall Status**: Phase 1 (Foundation) In Progress

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
**Delivery Date: April 13, 2026**

| Component | Status | MVP | Validation | Ship Date |
|-----------|--------|-----|-----------|-----------|
| **RBAC Enforcement** | ✅ In Progress | Apr 6 | Apr 10 | Apr 13 |
| **EdgarTools MCP Container** | ✅ In Progress | Apr 6 | Apr 10 | Apr 13 |
| **CI/CD Pipeline** | Planned | Apr 5 | Apr 9 | Apr 13 |
| **Correlation ID Tracing** | Planned | Apr 7 | Apr 11 | Apr 13 |

**Deliverable**: RBAC enforcement live + EdgarTools containerized + foundational infrastructure ready

---

### PHASE 2: Observability (Sprint 2 - Weeks 3-4)
**Delivery Date: April 27, 2026**

| Component | Status | MVP | Validation | Ship Date |
|-----------|--------|-----|-----------|-----------|
| **Governance Event Logging** | Planned | Apr 19 | Apr 23 | Apr 27 |
| **CloudWatch Dashboards** | Planned | Apr 20 | Apr 24 | Apr 27 |
| **FastAPI Container** | Planned | Apr 20 | Apr 24 | Apr 27 |
| **Workflow 5A/5B Endpoints** | Planned | Apr 21 | Apr 25 | Apr 27 |

**Deliverable**: Full observability + FastAPI routing live + 5A/5B workflows operational

---

### PHASE 3: Automation & Cost Tracking (Sprint 3 - Weeks 5-6)
**Delivery Date: May 11, 2026**

| Component | Status | MVP | Validation | Ship Date |
|-----------|--------|-----|-----------|-----------|
| **n8n Container** | Planned | May 3 | May 7 | May 11 |
| **Token Tracking** | Planned | May 4 | May 8 | May 11 |
| **Cost Alerts** | Planned | May 4 | May 8 | May 11 |
| **Market Analysis Async** | Planned | May 5 | May 9 | May 11 |

**Deliverable**: Automation engine live + token tracking enabled + market analysis integrated

---

### PHASE 4: Production Scale (Sprint 4 - Weeks 7-8)
**Delivery Date: May 25, 2026**

| Component | Status | MVP | Validation | Ship Date |
|-----------|--------|-----|-----------|-----------|
| **Multi-Replica Deployment (3x)** | Planned | May 18 | May 22 | May 25 |
| **SLO Monitoring** | Planned | May 19 | May 23 | May 25 |
| **Auto-Scaling Enabled** | Planned | May 19 | May 23 | May 25 |
| **Ops Handoff Complete** | Planned | May 20 | May 24 | May 25 |

**Deliverable**: Full production system operational at scale with governance & monitoring

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

### Checkpoint 1: Foundation (Apr 13)
- ✓ RBAC enforcement at FastAPI entry point
- ✓ EdgarTools MCP containerized + load tested (100 req/sec)
- ✓ Correlation ID propagation middleware
- ✓ Unit tests: 40+ passing (auth, RBAC, validation)

### Checkpoint 2: API Bridge (Apr 27)
- ✓ FastAPI container healthy
- ✓ Workflow 5A/5B endpoints operational
- ✓ Job management (trigger, poll, export)
- ✓ Observability dashboards live in CloudWatch
- ✓ Error responses standardized

### Checkpoint 3: Automation (May 11)
- ✓ n8n container running
- ✓ Token tracking per-request
- ✓ Market Analysis 5 phases async
- ✓ Cost alerts configured
- ✓ Fallback strategies tested

### Checkpoint 4: Production Ready (May 25)
- ✓ 3x replicas per service
- ✓ Auto-scaling policies enabled
- ✓ SLO monitoring live (99.5% EDGAR, 99.9% FastAPI)
- ✓ Team trained + handoff complete
- ✓ All workflows operationally validated

---

## PROGRESS INDICATORS

### Current Sprint (S1: Mar 31 - Apr 13)
```
[████████░░░░░░░░░░░░░░░░░░░░░░░░] ~30% complete
   ├─ RBAC Enforcement .............. 75% (testing phase)
   ├─ EdgarTools Container .......... 80% (load testing)
   ├─ FastAPI Bridge ................ 40% (architecture defined)
   └─ CI/CD Setup ................... 20% (planned)
```

### Overall Project (8 weeks)
```
[████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] Week 1 of 8 (~12%)

Sprint Breakdown:
  S1 (Apr 13) .... [████░░░░░░] Foundation
  S2 (Apr 27) .... [░░░░░░░░░░] Observability
  S3 (May 11) .... [░░░░░░░░░░] Automation
  S4 (May 25) .... [░░░░░░░░░░] Production
```

---

## CRITICAL PATH

```
S1: RBAC + EdgarTools
  ↓ (dependency)
S2: FastAPI Bridge + Observability
  ├─ (dependency)
  ↓
S3: n8n + Token Tracking
  ├─ (dependency)
  ↓
S4: Production Scale + SLO Monitoring
  ↓
SHIP: May 25, 2026 ✓
```

No delays on critical path = on-schedule delivery

---

## KEY DATES

| Milestone | Date | Status |
|-----------|------|--------|
| Project Kickoff | Mar 31, 2026 | ✓ Active |
| Phase 1 Ship (Foundation) | Apr 13, 2026 | 🔄 In Progress |
| Phase 2 Ship (Observability) | Apr 27, 2026 | 📅 Scheduled |
| Phase 3 Ship (Automation) | May 11, 2026 | 📅 Scheduled |
| Phase 4 Ship (Production) | May 25, 2026 | 📅 Scheduled |
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

**Last Updated**: March 31, 2026
