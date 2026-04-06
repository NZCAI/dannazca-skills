# Nazca Governance Blueprint — EXTENDED
## Data Science Workflow Governance — Full Reference

**Date**: March 31, 2026
**Related Document**: `Nazca_Governance_Blueprint_v1.md` (LEAN version for quick lookup)
**For implementation details:** See `Data_Science_Workflow_Integration_Framework.md`

---

## 9. Data Science Workflow Governance — EXTENDED

Nazca operates three standardized data science workflows (5A, 5B, Market Analysis) through a unified FastAPI gateway with end-to-end governance, RBAC, and audit logging.

### 9.1 Workflow Execution Model — Detailed

**Workflow Types:**

1. **Workflow 5A (Yahoo Finance):**
   - Purpose: Investment IRR prediction for entry/pre-seed deals
   - Runtime: R-based, ~5 minutes execution
   - Data sources: LAVCA (7 vars) + Yahoo Finance ETF returns (1 var) + KPI medians (4 vars)
   - Output: ranking_comite_final.xlsx with IRR estimates + confidence intervals
   - Use case: Fast go/no-go decisions on early-stage deals

2. **Workflow 5B (EDGAR):**
   - Purpose: Investment IRR prediction for follow-on deals
   - Runtime: R + EdgarTools MCP, ~10 minutes execution
   - Data sources: LAVCA (7 vars) + EDGAR public comparables (1 var + 5 extra fundamentals) + KPI calculations (4 vars)
   - Output: ranking_comite_final.xlsx with fundamentals + IRR estimates
   - Use case: Deep analysis on mature company follow-on investments

3. **Market Analysis (Sector Waves):**
   - Purpose: Sector wave correlation analysis for strategic planning
   - Runtime: Python-based, async, ~5-7 minutes total
   - Data sources: LAVCA investments (5,543), exits (1,172); EDGAR (46 tickers); Pitchbook (11,654 deals)
   - Output: 6 Excel files + 4 Word reports + 45+ PNG charts
   - Use case: Understand market cycles, identify sector trends, strategic portfolio alignment

**Execution Trigger:**

All workflows exposed via unified FastAPI:
- `POST /api/v1/workflows/trigger` — Polymorphic router (accepts workflow type in body)
- `POST /api/v1/workflows/5a` — Direct trigger for 5A
- `POST /api/v1/workflows/5b` — Direct trigger for 5B
- `POST /api/v1/workflows/market-analysis` — Direct trigger for Market Analysis

Each execution tagged with `correlation_id` for end-to-end tracing and audit compliance.

**Async Job Management:**

- All workflows return `job_id` immediately → HTTP 202 Accepted
- Client polls `GET /api/v1/jobs/{job_id}` for status + progress (0-100%)
- Completed outputs downloaded via `GET /api/v1/jobs/{job_id}/export` (format: excel|zip|json)
- Job retention: 30 days (outputs archived to S3, metadata kept for compliance)

**Progress Tracking:**
- 5A/5B: Phases 0–6 execution, each phase 1–3 minutes
- Market Analysis: Phases 1–5 async, can be executed in parallel or sequential
- Client can cancel job anytime via `POST /api/v1/jobs/{job_id}/cancel`

---

### 9.2 RBAC & Access Control — Detailed

**Workflow Execution Permissions:**

| Role | 5A Execute | 5B Execute | Market Exec | Edgar Tools | Data Read | Automation | Notes |
|------|---|---|---|---|---|---|---|
| **admin** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Full access, can override RBAC |
| **data_scientist** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Executes workflows + uploads outputs |
| **ai_data_analyst** | ✗ | ✓* | ✓* | ✓ | ✓ | ✗ | EDGAR research only (no BRMS/correlations) |
| **investment_analyst** | ✗ | ✗ | ✗ | ✓ (ad-hoc) | ✓ (RO) | ✗ | Consumer of workflow outputs + portfolio data |
| **ml_trainee** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | No production access (dev environment only) |
| **automations_trainee** | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | GUR extraction + n8n workflow management only |

*ai_data_analyst: Can trigger EDGAR research aspects of 5B/Market (edgar_screen, edgar_compare, edgar_trends) but cannot execute full BRMS inference phase or market correlation computations. Output limited to EDGAR metrics, no proprietary rankings.

**Enforcement Mechanism:**

RBAC checked at FastAPI middleware (before business logic execution):

```python
@app.post("/api/v1/workflows/trigger")
async def trigger_workflow(
    req: WorkflowTriggerRequest,
    token: str = Header(..., alias="authorization")
):
    # Step 1: Verify token against JWT secret
    try:
        role = verify_token(token)
    except InvalidToken:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Step 2: Check permission for this workflow
    required_permission = f"workflows:{req.workflow}:execute"
    if not has_permission(role, required_permission):
        log_rbac_violation(role, req.workflow, token[:10], timestamp, correlation_id)
        raise HTTPException(status_code=403, detail=f"Role {role} not permitted for {req.workflow}")

    # Step 3: Check data source permissions
    if req.workflow == "5b" or req.workflow == "market-analysis":
        if not has_permission(role, "data_source:edgar"):
            raise HTTPException(status_code=403, detail="EDGAR access required")

    # Step 4: Execution
    job = trigger_workflow_internal(req, role, token)
    return WorkflowTriggerResponse(job_id=job.id, status="queued", ...)
```

**Invalid roles rejected:** 403 Forbidden, audit logged with timestamp + role + attempt details

---

### 9.3 Data Source Access Control — Detailed

All data source credentials stored in AWS Secrets Manager, never embedded in code.

| Data Source | 5A | 5B | Market | Access Pattern | Credentials | Failover |
|---|---|---|---|---|---|---|
| **LAVCA** | ✓ | ✓ | ✓ | CSV import OR n8n scraper | AWS S3 bucket (read-only) | Cached data (< 24h old) if S3 unavailable |
| **EdgarTools MCP** | ✗ | ✓ | ✓ | JSON-RPC tool calls (edgar_screen, edgar_compare, edgar_trends, edgar_company) | API key (AWS Secret Manager) | Portfolio medians (5B) or skip phase (Market) |
| **Pitchbook** | ✗ | ✗ | ✓ | Excel file upload to S3 | S3 bucket access | Skip phase if unavailable |
| **Yahoo Finance** | ✓ | ✗ | ✗ | HTTP API via R quantmod package | Public API (no authentication required) | None (fail workflow if timeout) |
| **Aurora RDS** | Fallback | Fallback | Fallback | SQL queries via psycopg2 (optional KPI lookup) | AWS Secret Manager (read-only user) | Skip if not available |

**Credential Policy:**
- Never embed API keys, passwords, or AWS credentials in code
- All secrets accessed via AWS Secrets Manager at runtime
- Environment variables use secret manager references (e.g., `${EDGAR_API_KEY}`)
- Credentials rotated quarterly (automated by AWS Secrets Manager)
- Access to secrets logged in CloudTrail (audit trail)

**Error Handling:**
- **LAVCA unavailable:** Return cached data with warning (age of cache displayed to user)
- **EDGAR timeout:** 5B uses portfolio medians from LAVCA; Market Analysis skips correlation phase
- **Pitchbook missing:** Market Analysis skips USA private market phase
- **Yahoo timeout:** 5A workflow fails (no fallback, data critical for path)

---

### 9.4 Observability & Audit Trail — Detailed

**Event Logging (All Workflows):**

Every operation logged with structured JSON format:

```json
{
  "timestamp": "2026-03-31T10:00:05.123Z",
  "correlation_id": "req-12345-abc",
  "event_type": "workflow_triggered",
  "workflow": "5b",
  "role": "data_scientist",
  "job_id": "job-uuid-5b-20260331-001",
  "parameters": {
    "company": "Albo",
    "fund_code": "NZ2"
  }
}
```

**Event Types:**

1. **Workflow triggered:** timestamp, role, workflow_id, correlation_id, parameters
2. **Phase complete:** workflow, job_id, phase_name, duration_ms, tokens_used, status (success/partial/failed)
3. **Data source access:** workflow, source (LAVCA/EDGAR/Yahoo), query_type, records_returned, latency_ms
4. **RBAC decision:** role, endpoint, decision (allow/deny), reason, timestamp
5. **Output written:** job_id, file_path, size_bytes, checksum, s3_location
6. **Error occurred:** job_id, phase, error_code, error_message, trace_id

**Retention Policy:**
- **CloudWatch:** 30 days (real-time dashboards, alerts, quick queries)
- **S3 archive:** 2 years (compliance, audit trail, slow access)
- **Log rotation:** Daily files per date (2026-03-31_workflows.jsonl, etc.)
- **Encryption:** All logs encrypted at rest (S3 SSE-KMS)

**Correlation ID (Trace Propagation):**

Generated on workflow trigger OR passed by client:
```bash
curl -X POST /api/v1/workflows/5b \
  -H "X-Correlation-ID: my-custom-id" \
  -d '{...}'
```

Propagated to all downstream operations:
- R script execution (logged in .log file)
- EDGAR MCP calls (included in request body)
- S3 uploads (tagged as object metadata)
- Database queries (included in query context)

**Enables:** Root cause analysis, full request reconstruction, compliance audit trail

---

### 9.5 Cost & Token Tracking — Detailed

**Per-Workflow Metrics Captured:**

1. **Tokens consumed:** LLM inference (if applicable), estimated from input/output token counts
2. **EDGAR API calls:** Count of edgar_screen, edgar_compare, edgar_trends, edgar_company calls
3. **Compute time:** R execution time (5A/5B), Python processing time (Market Analysis)
4. **Data transfer:** S3 uploads (results), downloads (input files)
5. **Execution time:** Total wall-clock duration from trigger to completion

**Aggregation & Reporting:**

- **Real-time:** Tracked per-request via Langchain instrumentation
- **Daily summary:** Total tokens/EDGAR calls/compute by workflow + role, stored in S3 CSV
- **Weekly alert:** If any metric exceeds threshold (e.g., > 100k tokens/week) → Slack notification
- **Monthly report:** For billing + optimization feedback

**Example Tracking (CloudWatch):**
```
2026-03-31 10:05:00 | correlation_id: req-xyz-123 | workflow: 5b | role: data_scientist
  tokens_used: 3200
  edgar_calls: 5 (edgar_screen: 2, edgar_compare: 3)
  execution_time: 610s
  output_size: 2.3MB
```

**Cost Alerts:**
- Spike alert: > 20% above rolling 7-day average for any workflow
- Weekly budget: Set per-role limits (e.g., data_scientist: $500/week)
- Monthly review: Compare actual vs budgeted costs

---

### 9.6 Error Handling & Fallback Strategy — Detailed

**Failure Mode Analysis & Recovery:**

| Failure Mode | Workflow Impact | Root Cause | Fallback Strategy | User Notification | Recovery |
|---|---|---|---|---|---|
| **LAVCA data unavailable** | 5A, 5B, Market blocked at Phase 1 | S3 not accessible OR n8n scraper failed | Use cached CSV (< 24h old) | Warning message with cache age + date | Manual LAVCA upload to S3 |
| **EDGAR API timeout** | 5B Phase 2 fails, Market Phase 2 fails | EdgarTools service down OR slow network | 5B: substitute portfolio medians from LAVCA; Market: skip Phase 2, continue with Phase 3 | Job status = "partial_complete", list phases skipped | Admin escalates to EdgarTools team |
| **R script error** | 5A, 5B fails immediately | Invalid input OR model fitting failed | Log error, return phase output before crash | 500 error with trace_id for debugging | Data Scientist reviews logs, re-runs with corrected input |
| **S3 write failure** | Output not saved, user cannot download | S3 bucket full OR IAM permission denied OR network error | Fallback to local temp storage, retry upload in background | Warning: "Output saved to temp, retry in progress" | Admin checks S3 quota/permissions, manual copy if needed |
| **RBAC violation** | Request blocked immediately | User token invalid OR role not permitted | None (security boundary, deny) | 403 Forbidden + audit log | User re-authenticates OR admin grants permission |
| **Correlation ID missing** | Tracing broken | Client didn't send, server didn't generate | Server auto-generates UUID | None (transparent) | All logs tagged with auto-generated ID |

**Retry Logic:**

- **Transient errors** (timeout, connection reset, 503 Service Unavailable):
  - Retry 1st time after 1 second
  - Retry 2nd time after 3 seconds
  - Fail if 3rd attempt fails
  - Example: `[retry 1 of 2] EdgarTools timeout, retrying...`

- **Permanent errors** (401 Unauthorized, 404 Not Found, invalid schema):
  - Fail immediately, do not retry
  - Example: `EdgarTools API key invalid, aborting`

- **Partial failures** (Market Analysis Phase 4 fails, but Phase 1-3 succeeded):
  - Log warning, continue remaining phases
  - Mark job status as "partial_complete"
  - Return available outputs + list of skipped phases

---

### 9.7 Data Privacy & Confidentiality — Detailed

**Output Classification:**

1. **Investment Rankings (5A/5B outputs):**
   - Classification: **Investment-sensitive** (proprietary, competitive advantage)
   - Viewers: Fund managers, investors (authorized LPs only)
   - Storage: S3 with object-level IAM restrictions
   - Retention: 2 years (for audit trail)
   - Usage: Not shared with external parties without explicit approval

2. **Market Analysis Reports:**
   - Classification: **Strategic** (shared internally for planning)
   - Viewers: Nazca team + authorized LPs
   - Storage: S3 with bucket-level encryption
   - Retention: 2 years
   - Usage: Can be shared in investor updates

3. **Model Artifacts (.rds files, trained weights):**
   - Classification: **Technical** (IP, restricted to Data Scientists)
   - Viewers: Data Scientists only
   - Storage: S3 with granular IAM (specific role required)
   - Retention: 1 year (for reproducibility)
   - Usage: Internal model improvement only

**Storage & Encryption:**

- **Encryption at rest:** All outputs encrypted with S3 SSE-KMS (AWS managed keys)
- **Access control:** AWS IAM bucket policies + object tagging (e.g., tag: "classification=investment-sensitive")
- **Encryption in transit:** TLS 1.3 for all S3 transfers
- **Audit access:** All S3 access logged to CloudTrail (who accessed what, when)

**Data in Logs:**

- User data (company names, valuations) **logged with correlation IDs** for traceability
- User data **never duplicated** in observability logs (only metrics)
- Sensitive data (API keys, credentials) **stripped from logs** before writing

**Audit Access Control:**

- **Admin:** Full access to all logs (including data content) + compliance exports
- **Data Scientist:** Can view own execution logs (workflow results) but not peer data
- **Investment Team:** Can view success/failure summaries without underlying data
- **Monthly compliance report:** Auto-generated, includes:
  - Data access frequency by role
  - Sensitive data exposure incidents (if any)
  - RBAC violation attempts
  - Unsigned authorization changes

---

### 9.8 Workflow Governance Checklist — Detailed

**Before Each Workflow Deployment to Production:**

- [ ] **RBAC matrix validated:** Every role in the team has explicit permission or explicit deny for each workflow
- [ ] **Error handling tested:** Simulate LAVCA timeout, EDGAR API failure, S3 write denied scenarios
- [ ] **Correlation ID propagation verified:** Full request traced from trigger through all phases
- [ ] **Cost estimate reviewed:** Expected tokens (if LLM inference), EDGAR calls, compute minutes
- [ ] **Audit logging tested:** All events appear in CloudWatch within 60 seconds of execution
- [ ] **Fallback tested:** If LAVCA unavailable, workflow uses cached data successfully
- [ ] **Output encryption verified:** All S3 outputs encrypted at rest (SSE-KMS)
- [ ] **IAM permissions verified:** Service role has minimum required S3, RDS, Secrets Manager access

**Monthly Governance Review:**

- [ ] **Execution statistics:** Workflow count, average duration, error rate, success rate
- [ ] **Cost trends:** Token consumption, EDGAR calls, compute time over time
- [ ] **RBAC violations detected:** Any unauthorized access attempts? Log them and respond
- [ ] **Data source availability:** LAVCA uptime, EDGAR uptime, Pitchbook uptime (track SLOs)
- [ ] **User feedback:** Are workflows meeting expected performance? Any user-reported issues?
- [ ] **Security audit:** Any data exposure, credential leaks, or privilege escalation attempts?
- [ ] **Compliance status:** All required logs available, retention policies enforced, audit trails complete

**Sign-Off:** Review meeting held, findings documented, action items assigned

---

## References

- **Technical Implementation:** `Data_Science_Workflow_Integration_Framework.md` (LEAN + EXTENDED)
- **Workflow Specifications:** `Nazca_Technical_Specification_v2.md` (Sections 7.1-7.3)
- **RBAC Framework:** `RBAC_Framework_v2.md`
- **Observability:** `Observability_Framework.md`
- **Containerization:** `Containerization_Policy.md`

---

**Status:** Extended governance reference — Use LEAN version for quick lookup
