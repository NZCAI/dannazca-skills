# Product Requirements Document (PRD): Nazca Agentic System Core Architecture V2.0

**Date Created**: 2026-03-20
**Last Updated**: 2026-03-30
**Status**: Phase 1 (Foundation) — In Development
**Related Document**: Nazca_Governance_Blueprint_v1.md (Governance & Delivery Blueprint)
**Audience**: Data Scientists, Engineers, Architects, Technical Implementation Team

---

## 1. Problem Statement & Goals
Nazca operates multiple independent AI and data products—spanning from public-facing WhatsApp Copilots ("Lupe") and automated CRM deal pipelines, to deep data science models and internal Trading Agent workflows. Historically, these systems used powerful but siloed data stores and execution environments.

**Primary Goal:** Build a robust, flexible, and MACH-aligned (Microservices-based, API-first, Cloud-native, Headless) architecture using FastAPI and a federated Model Context Protocol (MCP) network hosted on AWS. This system will route triggers, execute multi-step logic in LangChain, securely expose diverse data sources, and enforce strict Agent Governance.

**Success Metrics:**
- 100% of technical team prompt changes flow through the version-controlled governance repo.
- Zero direct database credential exposure in prompts or agent instructions.
- End-to-end observability (token, latency, tool-call traces) for all production agents.
- Controlled polyglot interoperability (Python + TypeScript/n8n) through standardized MCP tools.
- Graceful degradation: one MCP service failure does not bring down the full orchestration path.

### 1.1 Related Documents & Governance Framework

**Related Document**: Nazca_Governance_Blueprint_v1.md (Governance & Delivery Blueprint)
**Last Synced**: March 30, 2026

This document (PRD_V2) is the **technical specification** for architects, data scientists, and engineers. It details system components, technical workflows, software requirements, and design decisions.

For governance, RBAC framework, observability requirements, delivery timeline, and risk mitigation—refer to **Nazca_Governance_Blueprint_v1.md**:
- Nazca_Governance_Blueprint_v1 Section 2: Governance & Safety (RBAC, observability, audit logging)
- Nazca_Governance_Blueprint_v1 Section 5: 8-Week Technical Roadmap (delivery schedule and milestones)
- Nazca_Governance_Blueprint_v1 Section 6: Dependencies & Sequencing (critical path)
- Nazca_Governance_Blueprint_v1 Section 8: Relationship to Nazca_Technical_Specification_v2 (how the two documents work together)

Both documents share standardized nomenclature (Tool, Product, Workflow, System Requirement, Engine). See the **Nazca_Nomenclature_Standards.xlsx** spreadsheet for definitions and component inventory.

---

## 2. System Architecture & Components

### 2.1 Headless Interoperability Layer (FastAPI Bridge)
FastAPI is the central headless routing plane (not the business logic plane).

**Ingress Sources:**
1. **n8n Automation Layer (Trigger Automation):**
   - Primary automation trigger engine for CRM/Spreadsheets, data collection jobs, and external process kickoff.
   - Emits normalized events (e.g., `trigger_scoring`, `sync_kpis`, `refresh_profiles`) to FastAPI.
2. **Human-in-the-loop Interfaces (Macro-Orchestrator Clients):**
   - Factory CLI / chat clients (and compatible interfaces) for ad-hoc analyst requests and operator commands.

**Egress Targets:**
- **LangChain Micro-Orchestrator** for heavy multi-step reasoning, decomposition, and tool orchestration.
- **MCP Federation** for structured tool execution (data reads, model calls, external lookups).

**Design Constraints:**
- Stateless API layer.
- Strict schema validation with Pydantic.
- Background execution for long-running tasks.
- Idempotent trigger handling where required.

**Governance Controls** (see Nazca_Governance_Blueprint_v1.md Section 2 for RBAC, observability monitoring, and audit logging):
- All requests validated through RBAC matrix at FastAPI entry point
- Observability: token counts, latency, and tool-call traces propagated via trace IDs
- Audit logging: all tool invocations and permission checks logged to CloudWatch/S3
- Fail-safe: invalid tokens rejected before business logic execution

---

### 2.2 Federated MCP Architecture (AWS, JSON-RPC)
MCP is not a single monolith and not just a PostgreSQL wrapper. It is a federated capability layer.

**Protocol Mandate:**
- **JSON-RPC via stdio/HTTP** for MCP interactions (required for standards-compliant tool interoperability).

**Initial MCP Service Topology (modular):**
1. `mcp-postgres`
   - Read-only, policy-constrained access to Aurora/RDS and approved analytical views.
2. `mcp-data-science`
   - Controlled access to DS artifacts and datasets (e.g., `.rds`, `gur_clean.csv`, `matriz_kpis.csv`).
3. `mcp-n8n`
   - Standardized wrappers for approved n8n automations/tools.
4. `mcp-market`
   - Market/external dataset connectors (e.g., PitchBook/ETF pipelines) under licensing and policy controls.

**AWS Operational Model:**
- Deploy as isolated services (containers) in AWS (e.g., ECS/Fargate/EKS pattern as selected).
- Health endpoints + service-level alarms.
- Independent scaling and failure isolation per MCP service.
- Secret management via AWS-native secret stores.
- Network segmentation and least-privilege IAM roles.

---

### 2.3 Agent Governance Layer (Priority)
Governance is a first-class system layer, not an appendix.  
Trading Analysis Framework is one governed product among many.

**Governance Scope:**
- Cross-framework governance for all agentic products (e.g., Trading Analysis, LP Copilot, Deal Pipeline Scorer, future frameworks).

**Repository Strategy (single control plane):**
- Central governance repo structure (example):
  - `/frameworks/trading-analysis/`
  - `/frameworks/lp-copilot/`
  - `/frameworks/deal-pipeline-scorer/`
  - shared `/policies`, `/evaluations`, `/tool-permissions`

**Three Governance Pillars:**
1. **Versioned Prompt/Policy Control**
   - Prompts/policies are text artifacts in Git, decoupled from runtime code.
   - Mandatory PR reviews and change history for every behavioral change.
2. **RBAC + Tool Authorization**
   - Agent-to-tool and team-to-tool permission matrices.
   - Explicit deny-by-default for high-risk tools/datasets.
3. **CI/CD Evaluation Gates**
   - Automated quality gates before merge/deploy (regression evals, safety checks, style/tone constraints, benchmark thresholds).

---

### 2.4 LangChain Internal Governance Flow (Reference Execution Model)
This flow is the core operational reference for runtime governance:

1. **Identity Injection**
   - Load approved prompt/policy bundle by version/tag.
2. **RBAC Tool Binding**
   - Bind only authorized MCP tools for the requesting agent role.
3. **Reason/Act Loop with Traceability**
   - Execute LangChain steps with full trace capture (`@traceable` or equivalent instrumentation).
4. **Output Guardrails**
   - Enforce post-processing checks (policy compliance, data leakage prevention, format contracts) before response emission.

This execution flow is mandatory for governed production agents.

---

### 2.5 Observability, Reliability, and Operations
Telemetry is necessary but not sufficient; operations require governance-aware observability.

**Required Signals:**
- Request IDs spanning FastAPI → LangChain → MCP tool calls.
- Token consumption, latency distributions, failure classes.
- Tool-level success/error rates and fallback behavior.
- Governance violations (blocked tool attempts, policy check failures).

**Operational Controls:**
- Per-service SLOs and alerting.
- Retry/circuit-breaker strategy for MCP dependencies.
- Dead-letter or replay paths for failed async triggers.
- Audit logs for governance-relevant actions (who changed what, when, and why).

---

### 2.6 Data Science Workflows — Investment Analysis (NEW)

Nazca supports standardized, repeatable **data science workflows** for investment analysis. These workflows chain multiple tools and data sources through FastAPI → LangChain orchestration.

**Workflow Paths:**
1. **Workflow 5A (Yahoo Finance Path):** LAVCA private market data + public market comparables via Yahoo Finance ETF proxies. No EDGAR MCP required. Simple, fast path for entry/pre-seed deals.
2. **Workflow 5B (EDGAR Path):** LAVCA private market data + EDGAR public company comparables for deeper fundamental analysis. Requires EdgarTools MCP for SEC filing queries. Richer data, more complex path for follow-on deals.

**Prerequisite:** GUR Extraction workflow (standardized company + funding data from portfolio PDF + GUR spreadsheet)

**Output:** Investment ranking Excel with predicted IRR, confidence intervals, operational KPIs, and (for 5B) additional EDGAR fundamentals.

**Users:**
- **Data Scientist (builder):** Develops and executes workflows using R (brms), Python, LAVCA/EDGAR data; uploads model artifacts to S3.
- **Investment Team (consumer):** Reviews completed rankings, performs due diligence, makes investment decisions; can query EDGAR ad-hoc for public comparables.

See Section 7 for detailed workflow specifications.

---

## 3. Recommended Development Sequence (Roadmap)

### Phase 1 — Foundations Completed
- TradingAgents backend validated in controlled environment.
- MVP interface tested for stakeholder feedback.
- Prompt extraction initiated into governed repository model.

### Phase 2 — FastAPI Headless Bridge
- Initialize `nazca-api-bridge` as the central routing and validation layer.
- Implement core trigger ingestion and async orchestration contracts.
- Enforce request schemas, idempotency strategy, and trace propagation.

### Phase 3 — MCP Federation on AWS
- Launch `mcp-postgres` and `mcp-n8n` first (highest immediate value).
- Add `mcp-data-science` and `mcp-market` with policy wrappers.
- Standardize JSON-RPC contracts and service discovery.

### Phase 4 — Governance Enforcement
- Activate repository-wide governance model across frameworks.
- Implement RBAC matrices and deny-by-default tool policies.
- Add CI/CD eval gates and block non-compliant merges.

### Phase 5 — Production Hardening
- SLOs, dashboards, alarms, fallback paths, and incident playbooks.
- Load testing and chaos testing for dependency failures.
- Formal rollout strategy with staged environments.

---

## 4. Tool Landscape & Role Boundaries

| Layer | Primary Technology | Purpose | Governance Rule |
|---|---|---|---|
| Trigger Automation | n8n (TypeScript) | Event ingestion, automation kickoff, external process triggers | No direct privileged data access without MCP policy |
| Human Interface | Factory CLI / Chat clients | Operator and analyst interaction | All requests routed through FastAPI contracts |
| Routing Plane | FastAPI (Python) | Stateless validation, dispatch, trace propagation | No embedded product-specific business logic |
| Reasoning Plane | LangChain (Python) | Multi-step decomposition and decision workflows | Must follow 4-step governance execution model |
| Capability Plane | Federated MCP services | Data/model/tool access via JSON-RPC | Deny-by-default + per-agent RBAC bindings |
| Governance Plane | Git + CI/CD + Eval tooling | Versioning, approvals, policy enforcement | Mandatory PR + automated gates |

---

## 5. Key Architecture Decisions

1. **Why FastAPI + MCP (not only REST)?**
   - REST remains valid for public/internal API surfaces.
   - MCP/JSON-RPC is chosen for AI-tool interoperability standardization and portable tool semantics across orchestrators.
   - This combination preserves flexibility: REST for service contracts, MCP for agent tool contracts.

2. **Why federated MCP instead of one server?**
   - Failure isolation, independent scaling, clearer ownership boundaries, and faster iteration per capability domain.

3. **Why governance as priority?**
   - Without governance, scaling agents increases risk (behavior drift, unauthorized tool usage, unreproducible outputs).
   - Governance ensures controlled evolution across all frameworks, not only Trading Analysis.

---

## 6. Immediate Next Deliverables

1. Finalize governance repo taxonomy for multi-framework operation.
2. Define initial RBAC matrix (agents × tools × teams).
3. Publish JSON-RPC tool contract templates for first two MCP services.
4. Implement FastAPI trace propagation + async execution contract.
5. Stand up baseline operational dashboard (latency, errors, tool-call traces, governance events).

---

## 7. Data Science Workflows & Use Cases (Detailed Specification)

### 7.1 Workflow 5A: IRR Prediction (Yahoo Finance Path)

**Purpose:** Fast investment return prediction for entry/pre-seed deals using market sentiment + public ETF comparables.

**Pipeline Stages:**
1. **Phase 0 (GUR Extraction):** Extract company, sector, stage, memo_date from portfolio PDF + GUR data
2. **Phase 1 (LAVCA):** Calculate 7 market features (3/6/12/24m funding windows, sector momentum, market trend)
3. **Phase 2 (Yahoo Finance):** Fetch 1-year returns for sector-mapped ETF (ICLN for AgTech, XBI for Biotech, XLK for Tech, etc.)
4. **Phase 3 (KPIs):** Use portfolio medians or available internal data for 4 operational metrics
5. **Phase 4 (Assembly):** Scale 8 features to training distribution
6. **Phase 5 (BRMS):** Bayesian inference via brms model → predicted_irr_1y + confidence intervals
7. **Phase 6 (J-Curve):** Adjust for stage-specific exit timelines → final ranking Excel

**Tools Used:** LAVCA data, Yahoo Finance HTTP (via quantmod R package), BRMS statistical inference, Excel output

**System Requirements:** R 4.4+, brms 2.23.0+, quantmod, readxl, openxlsx, ~4GB RAM for training

**Owner:** Data Scientist (development + execution); Investment Team (consumption)

**Output:** `ranking_comite_final.xlsx` with predicted IRR, SD, Sharpe, J-curve adjusted returns, contexto variables

**When to Use:** Entry/Pre-Seed deals, exploratory scoring, quick turnarounds

---

### 7.2 Workflow 5B: IRR Prediction (EDGAR Path)

**Purpose:** Rich investment return prediction for follow-on deals using market data + deep fundamental analysis of public comparables.

**Pipeline Stages:**
1. **Phase 0 (GUR Extraction):** Same as 5A
2. **Phase 1 (LAVCA):** Same 7 market features as 5A
3. **Phase 2 (EDGAR Comparables):**
   - Search for public comparables via edgar_screen() / edgar_search() by broad_group
   - Fetch 3+ years of financials: edgar_trends() for quarterly revenue + growth, edgar_compare() for margins + multiples
   - Average across comparables; derive 1 MODEL variable (comp_return_1y) + 5 EXTRA variables (revenue growth, gross margin, profitability, R&D intensity, trend)
4. **Phase 3 (KPIs):** Use real data from matriz_kpis.csv (if follow-on) OR EDGAR-derived proxies (comparable revenue, margin benchmarks by stage)
5. **Phase 4 (Assembly):** Scale 8 model features + 5 EXTRA features to training distribution
6. **Phase 5 (BRMS):** Same inference as 5A → predicted_irr_1y
7. **Phase 6 (J-Curve):** Same adjustment → final ranking Excel + EXTRA EDGAR fundamentals

**Tools Used:** LAVCA data, EdgarTools MCP (edgar_screen, edgar_search, edgar_compare, edgar_trends, edgar_company), BRMS, Excel output

**System Requirements:** R 4.4+, brms, readxl, openxlsx, Python 3.10+ (for EDGAR MCP calls), ~4GB RAM, EdgarTools MCP server running, network access to efts.sec.gov + data.sec.gov

**Owner:** Data Scientist (development + execution, with AI-Data-Analyst for EDGAR research); Investment Team (consumption, including ad-hoc Edgar queries)

**Output:** `ranking_comite_final.xlsx` with predicted IRR + EXTRA EDGAR columns (comp_rev_growth_yoy, comp_gross_margin, comp_profitability, comp_rev_trend_q, comp_rd_intensity)

**When to Use:** Follow-on deals with public comparables, deeper due diligence, sector benchmarking required

---

### 7.3 Workflow: Market Analysis (Sector Waves)

**Purpose:** Analyze market trends across LATAM & USA, correlate private vs public market waves, predict sector momentum.

**Pipeline Stages:**
1. **Phase 1 (LATAM VC Analysis):** Extract LAVCA investments (5,543 records) + exits (1,172); aggregate by sector/industry; calculate time-to-exit lag correlation
2. **Phase 2 (Public Markets Analysis):** Fetch revenue from 46 public company tickers via EDGAR API; calculate growth by sector; correlate with LATAM private deal volume (lag 0, 1, 2 years)
3. **Phase 3 (USA Private Markets):** Process Pitchbook deals (11,654 records 2021-2026); aggregate by industry/vertical; calculate valuations + EV/Revenue multiples
4. **Phase 4 (Correlation & Wave Detection):** Match public company sectors to private deal verticals; detect wave phase (Boom/Expansion/Stable/Correction/Bust); cross-USA×LATAM synchrony
5. **Phase 5 (Reports):** Generate 4 Word documents (~8-25 pages each) + 45+ PNG charts + final ranking Excel

**Tools Used:** LAVCA data, EdgarTools MCP (edgar_screen, edgar_trends, edgar_compare), Pitchbook Excel, Python data processing (pandas, matplotlib, scipy)

**System Requirements:** Python 3.10+, pandas 3.0.0, matplotlib 3.10.8, openpyxl 4.2.0, scipy 1.14.0, ~2GB RAM

**Owner:** Data Scientist (research + execution); Investment Team (consumption for strategic planning)

**Output:**
- 6 Excel files: LATAM_VC_Analysis.xlsx, Time_To_Exit_Analysis.xlsx, Comparables_Public_Markets.xlsx, Pitchbook_USA_Analysis.xlsx, Pitchbook_Public_Comparables.xlsx, USA_Private_Market_Prediction.xlsx
- 4 Word reports: Reporte_Analisis_Mercados_Privados_LATAM.docx, Key_Findings.docx, Reporte_Final.docx, Executive_Prediccion_Oleadas_v2.docx
- 45+ PNG charts (sector waves, correlations, forecasts)

**When to Use:** Strategic market planning (quarterly review), sector rotation analysis, macro trend detection, LP reporting

---

### 7.4 Workflow: GUR Extraction (Prerequisite)

**Purpose:** Standardize and extract company metadata + founding/fundraising events from unstructured portfolio data.

**Input:** Portfolio PDF (company list, ask_usd, sector) + GUR spreadsheet (memo_date, funding amounts, valuation, stage)

**Output:** Standardized CSV with columns: company, sector_pdf, broad_group, stage, round_category, memo_date, amount_raised_usd, valuation_cap_usd, nazca_stake_pct, country, years_since_entry (derived), valuation_growth (derived)

**Owner:** Automations Trainee (via n8n bot + Selenium/Playwright) OR Data Scientist (manual extraction)

**Used By:** Workflows 5A, 5B, and all investment analysis processes

---

### 7.5 Use Case: Data Scientist (Model Builder & Analyst)

**Role:** Develops, executes, and maintains investment prediction & market analysis workflows.

**Access Level (RBAC):**
- Workflows: 5A (execute), 5B (execute), Market Analysis (execute)
- MCP read: All (LAVCA, EdgarTools for 5B/Market Analysis)
- S3 write: Upload model artifacts (.rds files), ranking excels, diagnostic plots, market analysis reports
- Compute: Local R + Python environments, AWS Lambda (optional for batch scoring)
- Tools: Claude Code CLI, R Studio, EdgarTools MCP, Jupyter notebooks for market analysis

**Workflow Execution:**
- **Use 5A** for quick iteration, portfolio entry analysis, less data requirements
- **Use 5B** for follow-on deals, when public comparables exist, deeper analysis needed
- **Use Market Analysis** for strategic planning, sector rotation, quarterly macro review

**Deliverables:**
- Investment Workflows (5A/5B): Fitted BRMS model (.rds), ranking Excel, diagnostic plots → S3
- Market Analysis: 6 Excel files, 4 Word reports, 45+ charts → S3

**Outputs Consumed By:** Investment Team (rankings, market insights, due diligence), AI-Data-Analyst agent (model metadata, performance tracking)

---

### 7.6 Use Case: Investment Team (Model & Analysis Consumer)

**Role:** Reviews completed workflow outputs, performs due diligence, makes investment decisions, monitors market trends.

**Access Level (RBAC):**
- Workflows: 5A (read-only), 5B (read-only), Market Analysis (read-only)
- MCP read: EdgarTools (ad-hoc public company research for comparables validation)
- S3 read: Completed ranking excels, market analysis reports, model metadata (not weights)
- Compute: Dashboard UI, Excel analysis tools, ChatUI
- Tools: Investment ranking dashboards, ChatUI for ad-hoc Edgar queries, market analysis dashboards

**Workflow Interaction:**
- **Investment Rankings (5A/5B):** Receive completed ranking Excel; review predicted IRRs, confidence intervals, operational KPIs; query EDGAR ad-hoc for additional context
- **Market Analysis:** Review sector wave correlations, trend reports; use for LP reporting, portfolio allocation decisions

**No Access:** Workflow execution, model training, S3 write, n8n automation

---

## 8. System Requirements & Tool Dependencies

### 8.1 Software Versions (Current Environment)

| Component | Version | Context |
|-----------|---------|---------|
| macOS | 12.7.4 (Monterey, ARM64) | Deployment platform |
| R | 4.4.1 | Pipeline 5A, 5B base runtime |
| Python | 3.14.3 | EDGAR MCP queries, reporting |
| brms | 2.23.0 | Bayesian IRR model inference |
| rstan | 2.32.7 | BRMS backend (Bayesian engine) |
| tidyverse | 2.0.0 | Data transformation (dplyr, ggplot2) |
| readxl | 1.4.5 | Read GUR + KPI spreadsheets |
| openxlsx | 4.2.8.1 | Write ranking Excel output |
| quantmod | 0.4.28 | Yahoo Finance data (5A only) |
| python-docx | 1.2.0 | Report generation |
| matplotlib | 3.10.8 | Diagnostic plots |
| pandas | 3.0.0 | Data analysis |

### 8.2 Pipeline × Requirement Matrix

| Requirement | Pipeline 5A | Pipeline 5B | Market Analysis | LAVCA Extraction | Data Scientist | Investment Team |
|---|---|---|---|---|---|---|
| R 4.4+ | ✓ | ✓ | — | ✓ (parse) | ✓ | — |
| brms | ✓ | ✓ | — | — | ✓ | — |
| quantmod | ✓ | — | — | — | ✓ (5A) | — |
| readxl | ✓ | ✓ | — | ✓ | ✓ | — |
| openxlsx | ✓ | ✓ | ✓ | — | ✓ | — |
| Python 3.10+ | — | — | ✓ | — | ✓ | — |
| pandas | — | — | ✓ | — | ✓ (Market) | — |
| matplotlib | — | — | ✓ | — | ✓ (Market) | — |
| python-docx | — | — | ✓ | — | ✓ | — |
| scipy | — | — | ✓ | — | ✓ (Market) | — |
| EDGAR MCP server | — | ✓ | ✓ | — | ✓ (5B, Market) | ✓ (ad-hoc) |
| Yahoo Finance (HTTP) | ✓ | — | — | — | ✓ (5A) | — |
| Pitchbook data | — | — | ✓ | — | ✓ (Market) | — |
| n8n + bot (LAVCA) | — | — | — | ✓ | — | — |
| Claude Code CLI | — | — | — | — | ✓ | — |
| S3 | — | — | ✓ | ✓ (storage) | ✓ (upload) | ✓ (read) |
| Postgres/Aurora | — | — | — | — | ✓ (optional) | — |
| Internet | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| RAM ~4GB | ✓ (train) | ✓ (train) | ✓ (processing) | — | ✓ | — |

### 8.3 MCP Integration Notes

**EdgarTools MCP (for Workflow 5B):**
- Must be containerized + running as HTTP service (or stdio in dev)
- Network access required: efts.sec.gov (SEC filing text search), data.sec.gov (XBRL data)
- Calls used: edgar_screen() for comparable discovery, edgar_compare() for financial metrics, edgar_trends() for quarterly growth, edgar_company() for cash/cash-like items
- Fallback: If EdgarTools unavailable, Workflow 5B degrades to Workflow 5A (use portfolio medians instead of EDGAR proxies)

**LAVCA Extraction Service:**
- Requires n8n with Selenium/Playwright bot for web automation (LAVCA portal has no public API)
- Bot logs in to LAVCA, navigates to Disclosed Investments, downloads Excel, stores version in S3
- Triggered on schedule or manual request; outputs standardized CSV with 3,437+ historical deals

---

### 8.4 Unified Data Science Workflow Integration

All three workflows (5A, 5B, Market Analysis) are exposed through a **single unified FastAPI gateway** with standardized request/response schemas, RBAC enforcement, and observability.

**FastAPI Integration Points:**
- **Trigger endpoints:** `/api/v1/workflows/5a`, `/api/v1/workflows/5b`, `/api/v1/workflows/market-analysis`
- **Generic trigger:** `/api/v1/workflows/trigger` (polymorphic, routes to specific workflow)
- **Job management:** `/api/v1/jobs/{job_id}` (polling, cancellation, export)
- **MCP tools:** `/api/v1/edgar/*` (screen, compare, trends, company) — shared across 5B and Market Analysis
- **Data refresh:** `/api/v1/data/lavca/refresh` (trigger n8n bot for latest LAVCA data)
- **Observability:** `/api/v1/observability/workflows`, `/api/v1/observability/data-sources`

**Request/Response Standardization:**
- All workflows use standardized Pydantic schemas (see Data_Science_Workflow_Integration_Framework.md)
- Request includes: workflow type, parameters, correlation_id (for tracing)
- Response includes: job_id, status, estimated_duration, polling URL
- Error responses use standardized format (error, error_code, trace_id)

**RBAC Enforcement:**
- Data Scientist: Execute all three workflows
- AI-Data-Analyst: Execute EDGAR queries + Market Analysis (no BRMS phase)
- Investment Team: Read-only access + ad-hoc EDGAR queries
- All requests validated at FastAPI middleware level before reaching business logic

**Execution Model:**
- **5A/5B:** Synchronous execution (R script runs on Lambda or EC2, blocks for ~5-15 minutes)
- **Market Analysis:** Asynchronous execution (5 Python phases, client polls for progress)

**Trace Propagation:**
- Correlation ID embedded in every request/response
- Propagates to all downstream calls (R scripts, EDGAR MCP, S3 writes)
- Enables end-to-end debugging and audit trails

**See:** `Data_Science_Workflow_Integration_Framework.md` for detailed endpoint specifications, schemas, error handling, and implementation checklist.

---

## 9. Terminology & Standardization

For consistent communication across technical + business teams, key terms are defined as follows:

| Term | Definition |
|------|-----------|
| **Tool** | Reusable capability/service (JSON-RPC or REST); used by multiple products/workflows. Examples: EdgarTools MCP, n8n, FastAPI Bridge, Postgres |
| **Product** | Business-facing outcome; uses multiple workflows + tools; has RBAC + SLOs. Example: Investment Analysis Dashboard |
| **Workflow** | Multi-step data/automation process; choreographs tools + handoffs; produces specific output. Examples: Pipeline 5A, 5B, GUR Extraction |
| **System Requirement** | Explicit dependency needed to execute workflow or consume product. Examples: R 4.4+, EdgarTools MCP, 4GB RAM |
| **Engine** | Core execution runtime for orchestration; stateless; moves data/logic between tools. Examples: FastAPI Bridge (routing), LangChain (reasoning), n8n (automation), BRMS (inference) |

See `Nazca_Nomenclature_Standards.xlsx` for complete terminology guide + inventory mapping.
