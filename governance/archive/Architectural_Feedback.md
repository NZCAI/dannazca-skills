# Nazca Agentic System V2.0: Architectural Feedback & Analysis

**Date**: 2026-03-24
**Reviewed Documents**:
1. Nazca_Technical_Specification_v2.md (core architecture)
2. FastAPI_Bridge_PRD.md (MCP connector requirements)
3. TraddingAgentsDirectory.md (Trading Analysis Framework overview)
4. TradingAgents.md (orchestration specification)
5. READMEMCP.md (EdgarTools MCP packaging)
6. pdr-integration-handoff.md (EdgarTools governance integration)

---

## Executive Summary

### Key Architectural Strengths ✅
1. **Governance as first-class layer** — positioning governance in Section 2.3 of Nazca_Technical_Specification_v2 (not as an afterthought) signals correct priority
2. **Federated MCP design** — the isolation model (mcp-postgres, mcp-n8n, mcp-data-science, mcp-market) prevents single points of failure and allows independent scaling
3. **Clear role boundaries** — FastAPI as routing plane, LangChain as reasoning plane, MCP as capability plane (Section 2.4 governance flow is sound)
4. **Shipped products readiness** — Trading Agents framework and EdgarTools are structurally aligned with V2 model; refactoring is incremental, not rework

### Critical Gaps Blocking Implementation 🚫
1. **RBAC matrix unspecified** — PRD V2 Section 2.3 mandates "Agent-to-tool and team-to-tool permission matrices" but provides zero templates, examples, or first-pass matrix. **Policy decision required**: default roles (analyst, researcher, trader, risk-manager, admin), and whether permissions inherit or must be explicit per role per tool.

2. **Governance policy authority unclear** — who can modify RBAC matrices, prompt policies, or CI/CD gates? Is it admins only, or can teams self-modify within guardrails? **Policy decision required**: governance repo write permissions, change approval workflows for different policy types.

3. **Observability trace propagation incomplete** — PRD V2 Section 2.5 lists "required signals" but omits critical detail: how are request IDs propagated through async BackgroundTasks in FastAPI? How does LangChain's tracer capture correlations? **Design clarification required**: trace propagation schema, especially for n8n → FastAPI → MCP chains.

4. **MCP failure modes undefined** — PRD V2 Section 2.2 and FastAPI Bridge Section 3 mention "graceful degradation" but don't define failure semantics. If mcp-postgres times out, does the agent retry? Fallback? Fail? What's the timeout threshold? **Policy decision required**: per-service SLO/SLA, circuit-breaker thresholds, fallback behavior matrix.

### Integration Concerns with Shipped Products ⚠️
1. **EdgarTools HTTP fallback resilience is untested** — pdr-integration-handoff.md (Section 4) proposes HTTP pilot alongside stdio, but no documented strategy for handling profile fallback failures or measuring fallback success rates.
2. **Trading Agents observability instrumentation is incomplete** — TradingAgents.md lists agent teams but has no mention of token tracking, tool-call tracing, or governance event logging. Integration requires instrumentation additions.
3. **Prompt governance workflow not yet operational** — Trading Analysis Framework stores prompts in `prompts/` directory, but no version control strategy, approval gates, or rollback procedure are defined yet.

---

## Per-Document Feedback

### 1. PRD_Nazca_Agentic_System_V2.md

#### 1.1 Governance Model — Strengths
- **Section 2.3 "Agent Governance Layer"**: Correct positioning as first-class layer. The 3-pillar model (versioned prompts, RBAC, CI/CD gates) is sound.
- **Section 2.4 "LangChain Internal Governance Flow"**: The 4-step execution model (identity injection → RBAC tool binding → reason/act with traces → output guardrails) is clear and implementable.
- **Cross-framework scope** (Section 2.3 point 1): Recognizing governance applies to all frameworks (Trading Analysis, LP Copilot, Deal Pipeline Scorer) prevents framework-specific silos.

#### 1.2 Governance Model — Gaps
- **RBAC matrix structure is not specified**: PRD states "Agent-to-tool and team-to-tool permission matrices" but provides no:
  - Default role taxonomy (analyst vs researcher vs trader vs risk-manager vs admin?)
  - Tool permission inheritance model (does "researcher" role inherit "analyst" tool access?)
  - Deny-by-default enforcement rules (how is a tool marked "high-risk"?)
  - Template or example matrix

  **Impact**: Teams cannot implement Phase 4 governance enforcement without guessing at role structure.
  **Recommendation**: Create RBAC matrix template with 3-4 example roles and Trading Agents × EdgarTools × MCP services as pilot matrix.

- **Governance policy authority is ambiguous**: Who modifies RBAC matrices, tool policies, or CI/CD evaluation gates?
  - Can individual product teams change their own tool permissions, or must all changes go through central governance repo PRs?
  - Are there different approval workflows for prompt changes vs RBAC changes vs CI/CD gate changes?
  - What's the escalation path if a team disagrees with a denied tool?

  **Impact**: Without clarity, governance becomes either too centralized (bottleneck) or too decentralized (inconsistent).
  **Recommendation**: Define governance policy authority matrix (who can change what, with what approval).

#### 1.3 Observability & Traceability — Strengths
- **Section 2.5 "Required Signals"**: Comprehensive list (request IDs, token consumption, latency, tool-level success rates, governance violations).
- **Traceability requirement is non-optional**: The phrase "end-to-end observability... for all production agents" signals this is blocking.

#### 1.4 Observability & Traceability — Gaps
- **Trace propagation schema is missing**: Section 2.5 lists "request IDs spanning FastAPI → LangChain → MCP tool calls" but doesn't specify:
  - Format of request ID (UUID, correlation ID standard?)
  - How is it passed through async BackgroundTasks (header, context variable, thread-local storage?)
  - Does LangChain's `@traceable` decorator automatically capture the request ID, or must it be injected?
  - How are MCP tool calls correlated back to the originating LangChain step?

  **Impact**: Without a schema, teams will implement ad-hoc tracing and correlation will fail at boundaries.
  **Recommendation**: Define trace propagation spec (format, injection points, correlation ID rules).

- **Governance event logging schema is unspecified**: Section 2.3 mentions "audit logs for governance-relevant actions (who changed what, when, and why)" but no schema is provided.
  - What constitutes a "governance event"? (tool denied for role, prompt rolled back, RBAC matrix modified?)
  - Who logs these events (FastAPI, LangChain, MCP, or all three)?
  - Where are they stored and how are they queried?

  **Impact**: Governance audit trail will be incomplete or inconsistent.
  **Recommendation**: Define governance event schema with examples.

#### 1.5 MCP Federation & Resilience — Strengths
- **Service isolation model** (Section 2.2): The federated topology (mcp-postgres, mcp-n8n, etc.) prevents cascading failures.
- **Policy wrappers concept** (Section 2.2): "deny-by-default + per-agent RBAC bindings" on MCP services is the right approach.

#### 1.6 MCP Federation & Resilience — Gaps
- **Failure semantics are undefined**: Section 2.2 mentions "graceful degradation: one MCP service failure does not bring down the full orchestration path" but doesn't define:
  - If mcp-postgres is unavailable for 30 seconds, what happens? (retry loop, timeout, fail agent step?)
  - What's the timeout threshold before an MCP call is considered failed?
  - Does the agent have a fallback response, or does it propagate the error to the user?
  - Are there per-service SLOs? (e.g., mcp-postgres must have 99.9% uptime, mcp-market can tolerate 99%)

  **Impact**: Agents will fail unpredictably under service degradation.
  **Recommendation**: Define MCP service SLA/SLO matrix and failure mode decision tree.

- **Circuit-breaker and retry strategy not specified**: Section 2.5 mentions "retry/circuit-breaker strategy for MCP dependencies" but provides no details:
  - Circuit-breaker thresholds (fail after N errors in M seconds?)
  - Retry backoff strategy (exponential, fixed, jittered?)
  - Is retry automatic or does it require explicit agent logic?

  **Impact**: Team will implement inconsistent retry strategies across services.
  **Recommendation**: Define circuit-breaker and retry policy templates.

#### 1.7 FastAPI / LangChain Boundary — Strengths
- **Section 2.1 "Headless Interoperability Layer"**: Clear statement that FastAPI is routing plane, not business logic plane. "Stateless API layer" is correct.

#### 1.8 FastAPI / LangChain Boundary — Gaps
- **Async execution contract is vague**: Section 2.1 mentions "Background execution for long-running tasks" and "Idempotent trigger handling where required" but doesn't specify:
  - When should a task be background vs synchronous? (time threshold? complexity threshold?)
  - What's the idempotency guarantee? (exactly-once, at-least-once, at-most-once?)
  - How are failures in background tasks reported back? (webhooks, status endpoints, event logs?)
  - What's the retry strategy if a background task fails?

  **Impact**: n8n integrations and long-running analyses will have inconsistent execution semantics.
  **Recommendation**: Define async execution contract (with Trading Agents as example).

#### 1.9 Phase Sequencing — Strengths
- **Phased approach** (Section 3) is realistic: foundations → FastAPI → MCP → governance → hardening.
- **Phase 2 (FastAPI)** comes before **Phase 4 (governance)**, which is sensible (can't enforce governance without routing infrastructure).

#### 1.10 Phase Sequencing — Potential Issue
- **Phase 2 and Phase 4 may need adjustment**: If governance enforcement is mandatory in Phase 4, but FastAPI is deployed in Phase 2 without governance wired in, there's a risk that Phase 2 agents operate ungoverned and become harder to retrofit.

  **Recommendation**: Consider introducing basic governance checks in Phase 2 (even if simple), then expanding in Phase 4. This prevents technical debt.

---

### 2. FastAPI_Bridge_PRD.md

#### 2.1 Design & Role Clarity — Strengths
- **Section 3 "Decoupled Routing"**: The three route categories (public/internal/data-pipelines) are well-defined. Clear separation of concerns.
- **Section 4 "Concurrency Strategy"**: Good distinction between async I/O (webhooks < 200ms) and BackgroundTasks (long-running scripts). This prevents blocking.

#### 2.2 Design & Role Clarity — Gaps
- **MCP tool contract is unspecified**: Section 3 mentions "MCP Connector Implementation" and "expose n8n workflows as executable tools" but doesn't define:
  - What's the JSON-RPC schema for calling an n8n workflow from an agent? (tool name, input schema, output schema?)
  - How does FastAPI translate JSON-RPC calls into n8n webhooks? (parameter mapping, error translation?)
  - Are there tool discovery mechanisms (how does an agent learn what tools are available)?
  - What's the versioning strategy if an n8n workflow changes (backward compatibility guarantee?)

  **Impact**: LangChain agents won't know how to invoke n8n tools without a formal contract.
  **Recommendation**: Define MCP tool contract template with n8n mapping examples (TOOL INDICADORES and TOOL SNAPSHOTS as concrete cases).

- **Trace propagation through FastAPI is missing**: FastAPI will receive requests from n8n webhooks and spawn LangChain orchestration. But how is the trace propagated?
  - Does FastAPI generate a correlation ID and pass it to LangChain?
  - How does the correlation ID flow from n8n → FastAPI → LangChain → MCP?
  - Can you correlate an MCP tool failure back to the originating n8n webhook?

  **Impact**: Observability across the n8n → FastAPI → LangChain → MCP chain will be broken.
  **Recommendation**: Define trace propagation for FastAPI with specific header/context injection strategy.

#### 2.3 Public vs Internal Routing — Strength
- **Section 2 "Core Product Distinctions"**: Clear that public (WhatsApp Copilot) and internal (Trading Agents) are decoupled. No unwanted coupling.

#### 2.4 Public vs Internal Routing — Gap
- **Security boundary between public and internal is unspecified**: Section 2 and Section 5 mention "should we separate the API into two different Docker containers/ports" but this remains an open question.
  - If public and internal share one FastAPI instance, are there path-based firewalls or RBAC checks?
  - Can a public endpoint accidentally call an internal orchestration (Trading Agents script)?
  - What's the authentication mechanism (API keys, mTLS, service identity)?

  **Impact**: Security incident risk (public API accidentally triggering internal logic).
  **Recommendation**: Provide security design (recommend separate containers + network policies for production).

#### 2.5 Stateless Design — Strength
- **Section 3 "Data Storage"**: "Strictly pass-through. The API will NOT store state locally." Correct.

#### 2.6 Async Semantics — Gap
- **BackgroundTask failure handling is unspecified**: Section 4 mentions BackgroundTasks for internal scripts, but:
  - If a Trading Agents script fails asynchronously, how does FastAPI report it? (webhook callback to client? status endpoint?)
  - Is there a retry mechanism if a BackgroundTask fails?
  - What's the timeout before a BackgroundTask is considered failed?
  - How does observability correlate the async failure back to the original request?

  **Impact**: Long-running tasks can fail silently.
  **Recommendation**: Define BackgroundTask failure contract and observability strategy.

#### 2.7 Open Question Resolution
- **Section 5 "Open Questions"**: Two questions remain (MCP tool schemas, public vs internal separation). These should be resolved before Phase 2 implementation.

  **Recommendation**: Close these in the next iteration before PRD sign-off.

---

### 3. TraddingAgentsDirectory.md (Trading Analysis Framework Overview)

#### 3.1 Framework Structure — Strength
- **Section "Repository Structure"**: Clear separation of concerns (SKILL.md, TradingAgents.md orchestration, prompts/ directory). Good for versioning.
- **Section "Integration"**: Correctly states this framework will be executed by Nazca FastAPI Bridge. Good integration expectation.

#### 3.2 Framework Structure — Gaps
- **Prompt versioning workflow is undefined**: The `prompts/` directory contains agent system prompts, but:
  - How are prompt versions tracked? (Git branches, tags, semantic versioning?)
  - What's the approval workflow for a prompt change? (PR review, domain expert sign-off?)
  - How are prompts deployed to production? (direct pull, immutable snapshot, containerized?)
  - How is a prompt rollback executed if a version causes issues?

  **Impact**: Prompt changes cannot be governed without a versioning strategy.
  **Recommendation**: Define prompt versioning workflow (example: semantic versioning, required reviewer roles, snapshot-based deployment).

- **Agent prompts don't reference governance governance model**: The prompts directory should include metadata indicating which agents require governance checks (e.g., "Trader agent can only call specific tools"). Currently no RBAC references.

  **Impact**: Prompts and governance policies will diverge.
  **Recommendation**: Add governance metadata to each prompt file (required tool access, sensitive data restrictions).

#### 3.3 Multi-Agent Coordination — Gap
- **Governance across the multi-agent workflow is unspecified**: With analysts, researchers, traders, and risk-managers, who enforces governance?
  - Does the "Trader" agent have permission to call mcp-postgres directly, or only through the "Bull Researcher"?
  - Can the "Risk Manager" override trader decisions, or only recommend?
  - Is there a governance flow diagram showing which agent can call which tools?

  **Impact**: Multi-agent orchestration will have ungooverned tool access.
  **Recommendation**: Create RBAC matrix for Trading Agents (analyst roles × tool access).

#### 3.4 Recent Milestones — Strength
- **Streamlit Web UI and Ngrok tunneling** show good iteration. Enables faster feedback loops.

#### 3.5 Streamlit Integration — Gap
- **Streamlit UI and FastAPI Bridge integration strategy is undefined**:
  - Currently, does Streamlit directly orchestrate LangGraph/LangChain, or does it call FastAPI?
  - If it calls FastAPI, is there a UI-to-API contract defined?
  - How does governance apply to UI-initiated requests? (same RBAC rules as API calls?)

  **Impact**: Streamlit bypasses FastAPI, breaking observability and governance.
  **Recommendation**: Refactor Streamlit to call FastAPI endpoints (via ng rok tunnel or internal URL).

---

### 4. TradingAgents.md (Orchestration Specification)

#### 4.1 Agent Team Structure — Strength
- **Sections "I. Analyst Team" through "IV. Risk Management Team"**: Clear role taxonomy. Easy to map to governance roles.

#### 4.2 Agent Team Structure — Gaps
- **Tool permissions per agent are unspecified**:
  - Can the "Fundamentals Analyst" call mcp-market directly, or only to fetch SEC filings via EdgarTools?
  - Can the "Trader" modify trading data in n8n, or only read and propose?
  - Can "Risk Analysts" call external risk models, or only review internal data?

  **Impact**: Without explicit tool permissions, agents will have ungooverned access.
  **Recommendation**: Add RBAC matrix section to TradingAgents.md (agent role × tool access).

- **Observability instrumentation is missing**:
  - No mention of token tracking across the multi-agent workflow.
  - No mention of tool call tracing (which step called which tool, with what arguments and result).
  - No mention of governance event logging (e.g., "Risk Manager denied Trader's aggressive position").

  **Impact**: Observability for multi-agent workflows will be incomplete.
  **Recommendation**: Add instrumentation requirements section (token tracking, tool call traces, governance events).

- **Failure handling in multi-agent debate is unspecified**:
  - If the "Bull Researcher" fails to generate upside arguments, does the "Research Manager" proceed with incomplete data?
  - If one of the "Risk Analysts" times out, does the "Portfolio Manager" wait or proceed?

  **Impact**: Multi-step workflows will fail unpredictably.
  **Recommendation**: Define failure handling strategy (timeout, retry, partial success, escalation).

---

### 5. READMEMCP.md (EdgarTools MCP Packaging)

#### 5.1 Packaging & Documentation — Strength
- **Section "Key Assets"**: Good bundling of installation guide, config template, use-cases, and skill routing. Ready for productization.

#### 5.2 Packaging & Documentation — Gap
- **HTTP WIP is under-specified**: Section "Additional Assets" mentions `http-wip/` but provides no details on:
  - When should HTTP be used vs stdio? (is it a fallback, or a production option?)
  - What's the success criteria for HTTP pilot? (latency threshold, availability target, error rate threshold?)
  - How is the fallback triggered? (automatic after stdio failure, or manual toggle?)

  **Impact**: HTTP fallback resilience is untested and unmeasured.
  **Recommendation**: Define HTTP fallback strategy (trigger conditions, success metrics, rollback plan).

#### 5.3 Installation & Setup — Strength
- **mcp-config.template.json**: Good starting point for integrating EdgarTools into MCP server registry.

#### 5.4 MCP Service Integration — Gap
- **Policy wrapper is not defined**: pdr-integration-handoff.md (Section 3) mentions "Define governance controls" and "Deny-by-default for high-volume or broad full-text operations" but:
  - What queries are considered "high-volume" or "broad"? (full-text SEC 10-K? CIK lookups?)
  - Which roles are denied by default? (analyst, researcher, trader, all?)
  - How is a denied query logged and reported?
  - What's the escalation path if a user needs access to a denied query?

  **Impact**: Policy wrapper cannot be implemented without these definitions.
  **Recommendation**: Define EdgarTools policy wrapper spec (high-risk queries, role-based denials, escalation workflow).

---

### 6. pdr-integration-handoff.md (EdgarTools Governance Integration)

#### 6.1 Integration Strategy — Strength
- **Section 1 "Objective"**: Clear transition from standalone to governed federated capability.
- **Section 1 "Integration Steps"**: Good 5-step roadmap (catalog, define controls, set execution policy, observability, rollout).

#### 6.2 Integration Strategy — Gaps
- **RBAC matrix is a template, not filled in**: Section 2 mentions "RBAC matrix: which roles can access company/ownership/full-text tools" but doesn't provide:
  - What are the three tool categories (company, ownership, full-text)? Are there others (insider trading, EDGAR search)?
  - Which roles have access? (analyst yes, researcher yes, trader no, risk-manager yes?)
  - Are permissions cumulative (researcher inherits analyst tools) or explicit per role?

  **Impact**: Cannot move from pilot to production without a filled-in matrix.
  **Recommendation**: Create 3×4 RBAC matrix (3 EdgarTools categories × 4 agent roles).

- **HTTP fallback resilience is incomplete**: Section 3 mentions "Fallback profile: `edgar517` for compatibility" and "HTTP pilot profile: `edgartools-http`" but:
  - When does fallback happen? (immediate on stdio error? after N retries? time-based?)
  - How is the fallback measured? ("% successful MCP calls without profile fallback" — success criteria not specified)
  - What's the acceptance threshold? (95% success? 99%?)
  - If HTTP fallback fails, what happens? (final failure, or escalate to manual?)

  **Impact**: HTTP pilot success cannot be measured or evaluated for production readiness.
  **Recommendation**: Define EdgarTools HTTP fallback SLA (trigger conditions, success metrics, promotion criteria).

- **Observability requirements are vague**: Section 4 mentions "track tool invocation counts, errors, and fallback usage" but doesn't specify:
  - What events are logged? (successful query, denied query, fallback invoked, fallback failed, profile switch?)
  - Where are events sent? (CloudWatch, Datadog, local logs?)
  - What's the schema? (timestamp, user role, query type, result, error details?)
  - How is observability correlated with upstream requests? (can you trace an EdgarTools denial back to the originating agent step?)

  **Impact**: Observability will be incomplete and disconnected from system-wide tracing.
  **Recommendation**: Define EdgarTools observability schema and correlation strategy.

- **Rollout criteria are too loose**: Section 2 says "exit criteria: stable availability + acceptable query latency + low fallback rate" but:
  - What's "stable"? (99.5%, 99.9%, SLO-based?)
  - What's "acceptable latency"? (< 100ms, < 500ms, compared to what baseline?)
  - What's "low fallback rate"? (< 1%, < 5%?)

  **Impact**: Rollout decision will be subjective and inconsistent.
  **Recommendation**: Define EdgarTools rollout acceptance criteria with specific thresholds.

---

## Cross-Cutting Thematic Analysis

### Theme 1: Governance Model Rigor

#### Current State
PRD V2 defines a 3-pillar governance model (versioned prompts, RBAC, CI/CD gates) but stops short of prescriptive implementation details. The model is **strategically sound** but **operationally incomplete**.

#### Why This Matters
Without specific RBAC role taxonomy, tool permission matrices, and policy authority rules, each team will implement governance differently. This defeats the purpose of "100% of technical team prompt changes flow through the version-controlled governance repo" (PRD V2 success metric).

#### Specific Gaps
1. **RBAC Role Taxonomy**: No default roles defined. Teams will invent their own (analyst, researcher, trader, risk-manager are implicit but not explicit).
2. **Tool Permission Matrix**: No structure for how tools are assigned to roles. Can roles inherit permissions, or are all permissions explicit?
3. **Policy Authority**: No clarity on who can modify RBAC, and with what approval process.
4. **Prompt Versioning Workflow**: No branch strategy, approval gates, or rollback procedures defined.
5. **CI/CD Evaluation Gates**: No schema for what "automated quality gates" look like (regression evals? style checks? benchmark thresholds?).

#### Risk
**Risk**: Without prescriptive governance, the system will either:
- **Option A (too centralized)**: All changes require central approval, bottlenecking feature velocity.
- **Option B (too decentralized)**: Teams operate independently, causing inconsistency and audit failures.

#### Recommendation
Build governance policies in the following order:
1. **RBAC Role Taxonomy** (week 1): Define 4-5 default roles + inheritance model
2. **Tool Permission Matrix Template** (week 1): Show how to assign tools to roles with deny-by-default logic
3. **Governance Policy Authority** (week 2): Define who can change what, with what approval (create governance request PR template)
4. **Prompt Versioning Workflow** (week 2): Git branching strategy, approval requirements, deployment snapshot rules
5. **CI/CD Evaluation Gates** (week 3): Regression eval thresholds, style checks, benchmark requirements

---

### Theme 2: Observability & Traceability

#### Current State
PRD V2 Section 2.5 lists required signals (request IDs, token consumption, latency, tool-call traces, governance violations). But the **implementation strategy is missing**: how are traces propagated? What's the schema? Who owns observability?

#### Why This Matters
Without end-to-end tracing, you cannot:
- Correlate a user request to a failure in an MCP service
- Track token consumption across a multi-step agent workflow
- Debug governance violations (e.g., "why was this tool denied for this user?")
- Measure observability KPIs (P95 latency, token efficiency, tool hit rates)

#### Specific Gaps
1. **Trace Propagation Schema**: No format for request IDs, no injection points, no correlation rules for async tasks
2. **Governance Event Schema**: No definition of what constitutes a "governance event", no logging structure
3. **Tool-Call Tracing**: No specification for how tool invocations (name, input, output, latency) are captured and correlated
4. **Token Tracking**: No schema for tracking token consumption across LLM calls, agents, and workflows
5. **Observability Ownership**: No clarity on who owns observability (centralized platform team or per-product teams)

#### Risk
**Risk**: Observability will be fragmented across FastAPI, LangChain, and MCP services. Debugging production issues will require stitching together logs from multiple systems with no correlation IDs.

#### Recommendation
Define observability policies in the following order:
1. **Trace Propagation Spec** (week 1): Format, injection points, async rules, correlation ID standard
2. **Governance Event Schema** (week 1): Define event types (tool denied, prompt deployed, policy changed), schema, logging targets
3. **Tool-Call Tracing** (week 2): How MCP tool calls are captured, with input/output/latency metadata
4. **Token Tracking Schema** (week 2): How to track tokens across LLM calls and aggregate to workflow level
5. **Observability Dashboard Template** (week 3): Dashboards for latency, errors, token efficiency, governance violations

---

### Theme 3: MCP Federation Resilience

#### Current State
PRD V2 Section 2.2 describes federated MCP services (mcp-postgres, mcp-n8n, mcp-data-science, mcp-market) with the goal of "graceful degradation: one MCP service failure does not bring down the full orchestration path." But **failure semantics are not defined**.

#### Why This Matters
If mcp-postgres is down, what happens? Does the agent:
- Retry with exponential backoff?
- Fail immediately with a human-readable error?
- Attempt a fallback (e.g., return stale cached data)?
- Escalate to a human analyst?

Without defined failure semantics, developers will implement ad-hoc strategies and the system will behave unpredictably under load.

#### Specific Gaps
1. **Service SLA/SLOs**: No uptime targets or latency SLOs per service (e.g., mcp-postgres: 99.9% uptime, p99 latency < 100ms)
2. **Circuit-Breaker Thresholds**: No definition of when to trip a circuit breaker (fail N times in M seconds?)
3. **Retry Strategy**: No guidance on exponential backoff, max retries, or jitter
4. **Timeout Thresholds**: No per-service timeout (how long to wait for mcp-market before failing?)
5. **Fallback Behavior**: No definition of fallback responses or partial-success semantics
6. **Dead-Letter Handling**: No strategy for failed async tasks (retry, escalate, drop?)

#### Risk
**Risk**: Under production load, MCP service failures will cascade through the system. Agents will either:
- **Option A**: Retry forever, hanging the user request.
- **Option B**: Fail immediately with poor user experience.

#### Recommendation
Define resilience policies in the following order:
1. **Service SLA/SLO Matrix** (week 1): Uptime targets and latency thresholds per MCP service
2. **Circuit-Breaker Policy** (week 1): Failure thresholds, recovery strategy, metrics
3. **Retry & Backoff Strategy** (week 2): Exponential backoff formula, max retries, jitter rules
4. **Timeout Policy** (week 2): Per-service timeout thresholds, global orchestration timeout
5. **Fallback Strategy** (week 2): Define fallback responses for degraded services (partial success, stale data, escalation)
6. **Dead-Letter Policy** (week 3): Failed async task handling (retry, DLQ, manual intervention)

---

### Theme 4: Integration of Shipped Products

#### Current State
Trading Agents Framework and EdgarTools MCP are structurally aligned with V2 model but require **instrumentation and governance wrapping** to fit seamlessly.

#### Why This Matters
If Trading Agents and EdgarTools are not fully instrumented for observability and governance, they will become sources of blind spots in the new system.

#### Trading Agents Integration Gaps
1. **Prompt Governance**: Prompts in `prompts/` directory have no version control strategy, approval workflow, or deployment mechanism
2. **Observability Instrumentation**: No token tracking, tool-call logging, or governance event reporting
3. **Streamlit UI Bypass**: Streamlit currently executes agents directly, bypassing FastAPI and governance
4. **RBAC Compliance**: Agent prompts don't reference governance roles or tool permissions

#### EdgarTools Integration Gaps
1. **HTTP Fallback Strategy**: When to trigger HTTP fallback, success criteria, rollback plan not defined
2. **Policy Wrapper**: High-risk query definitions, role-based denials, and escalation workflow not specified
3. **Observability Schema**: No definition of what events to log or how to correlate to upstream requests
4. **Rollout Criteria**: No specific thresholds for moving from pilot to production

#### Risk
**Risk**: Trading Agents and EdgarTools will operate outside the governance and observability framework, defeating the purpose of V2 architecture.

#### Recommendation
Integration refactoring in the following order:
1. **Trading Agents Prompt Governance** (week 1): Migrate prompts to versioned governance repo with approval workflow
2. **Streamlit Refactoring** (week 1-2): Refactor Streamlit to call FastAPI endpoints instead of direct LangChain execution
3. **Trading Agents Observability** (week 2): Add token tracking, tool-call logging, governance event reporting
4. **Trading Agents RBAC Matrix** (week 2): Define agent role × tool access matrix
5. **EdgarTools Policy Wrapper** (week 2-3): Define high-risk queries, role-based denials, escalation workflow
6. **EdgarTools HTTP Fallback SLA** (week 3): Define success metrics and promotion criteria

---

## Governance Policy Implications

### Critical Policy Decisions Required Before Phase 2 Implementation

| Decision | Current State | Required by Phase | Impact |
|----------|---------------|------------------|--------|
| RBAC role taxonomy (analyst, researcher, trader, risk-manager, admin?) | Implicit | Phase 2 | Blocks all tool permission assignment |
| Tool permission inheritance (cumulative or explicit?) | Undefined | Phase 2 | Blocks RBAC matrix implementation |
| Governance policy authority (who can change RBAC?) | Undefined | Phase 2 | Blocks governance repo setup |
| Trace propagation schema (request ID format, injection points) | Undefined | Phase 2 | Blocks observability implementation |
| MCP service SLA/SLO targets (99.5%, 99.9%?) | Undefined | Phase 3 | Blocks MCP federation launch |
| Failure mode semantics (retry, fallback, fail?) | Undefined | Phase 3 | Blocks MCP error handling |
| EdgarTools HTTP fallback trigger conditions | Undefined | Phase 3 | Blocks EdgarTools rollout |
| Trading Agents prompt versioning workflow | Undefined | Phase 2 | Blocks governance repo structure |

### Dependencies & Sequencing
1. **RBAC and authority decisions must come first** — they unblock tool permission matrices and prompt governance
2. **Trace propagation schema must come early** — it enables observability across all phases
3. **MCP resilience policies must come before Phase 3** — they inform service deployment and monitoring setup
4. **Product integration policies should track core policies** — they inherit RBAC, tracing, and resilience rules

---

## Next Steps

1. **Complete this governance feedback review** with stakeholders (identify any dissenting views or clarifications needed)
2. **Prioritize policy decisions** above by impact and dependency
3. **Assign ownership** to governance framework designers (recommend assigning governance repo ownership explicitly)
4. **Build policy templates** following the recommendation sequencing (RBAC → prompt versioning → observability → resilience)
5. **Create first RBAC matrix** using Trading Agents + EdgarTools as pilot case study

---

**Document prepared**: 2026-03-24
**Next review**: After policy templates completed
**Owner assignment**: (to be assigned)
