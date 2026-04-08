# 8-Week Technical Roadmap: Nazca Agentic System

**Duration**: Weeks 1–8 (bi-weekly sprints)
**Format**: Technical milestones for internal team
**Note**: Product shipping roadmap to be added post-Phase 1 based on management feedback

---

## Sprint 1: Foundation (Weeks 1–2)
**Parallel Track**: RBAC Enforcement + EdgarTools Containerization

### Ship Commitment
- RBAC enforcement live at FastAPI Bridge entry point
- EdgarTools MCP containerized (Docker image in ECR)
- Health checks + baseline observability operational

### Weekly Milestones

**Week 1**:
- [ ] FastAPI RBAC checks deployed to dev environment
- [ ] EdgarTools Dockerfile complete + tested locally
- [ ] Load test EdgarTools at 100 req/sec baseline
- [ ] RBAC evaluation gates spec (CI/CD enforcement)

**Week 2**:
- [ ] EdgarTools Docker image pushed to AWS ECR
- [ ] 1 replica running in test environment
- [ ] RBAC CI/CD gates configured + gated PR workflow active
- [ ] RBAC audit logging to CloudWatch begin

---

## Sprint 2: Observability (Weeks 3–4)
**Track**: Governance Logging + FastAPI Containerization

### Ship Commitment
- Governance event logging live (RBAC decisions + data access)
- CloudWatch dashboards operational for team roles
- FastAPI Bridge containerized (integrated with EdgarTools)

### Weekly Milestones

**Week 3**:
- [ ] Trace propagation schema implemented (correlation IDs)
- [ ] RBAC decision logging to CloudWatch + S3 archive
- [ ] Data access logging (S3 uploads, Edgar queries) configured
- [ ] CloudWatch log group retention set (2yr RBAC, 5yr high-risk ops)

**Week 4**:
- [ ] FastAPI Dockerfile complete + health checks
- [ ] FastAPI integrated with EdgarTools container
- [ ] Team-specific dashboards (Admin, Data Scientist, Analyst) live
- [ ] Alert rules for SLO tracking configured (draft)

---

## Sprint 3: Token Tracking + n8n Container (Weeks 5–6)
**Track**: Instrumentation + Automation Containerization

### Ship Commitment
- Token tracking per-request + daily cost aggregation
- n8n containerized (Postgres-backed custom image)
- Circuit breaker pattern for EdgarTools fallback operational

### Weekly Milestones

**Week 5**:
- [ ] Token counting instrumented in Langchain (prompt + completion)
- [ ] n8n Dockerfile complete (Python 3.11 + postgres config)
- [ ] docker-compose tested locally (n8n + postgres + EdgarTools)
- [ ] Cost tracking per agent/role/tool configured

**Week 6**:
- [ ] n8n workflows migrated to container-based flow
- [ ] Workflow validation in test environment complete
- [ ] Daily cost spike alerts configured (> 20% threshold)
- [ ] Circuit breaker pattern for EdgarTools HTTP tested + deployed

---

## Sprint 4: Production Scale + Hardening (Weeks 7–8)
**Track**: Deployment + Operational Readiness

### Ship Commitment
- All services at production scale (replicas + auto-scaling)
- SLO monitoring + alerting live end-to-end
- Team operational handoff + runbook documented

### Weekly Milestones

**Week 7**:
- [ ] Production deployment to AWS Fargate/ECS (all 3 services)
- [ ] Replicas configured: EdgarTools 3, FastAPI 2, n8n 2
- [ ] Auto-scaling policies enabled (CPU/memory thresholds)
- [ ] Load testing at production expected throughput

**Week 8**:
- [ ] SLO dashboard operational (uptime, latency, error rate, cost)
- [ ] Alert rules live (pagerduty/slack notifications)
- [ ] Operational runbook documented (team access)
- [ ] Rollback procedure tested + verified
- [ ] Team handoff complete (ops team trained)

---

## SLA/SLO Targets

| Service | Uptime | Latency (p99) | Error Rate | Replicas |
|---------|--------|---------------|-----------|----------|
| n8n | 99% | < 30s execution | < 1% | 2 |
| EdgarTools MCP | 99.5% | < 5s response | < 0.5% | 3 |
| FastAPI Bridge | 99.9% | < 100ms | < 0.1% | 2 |

---

## Notes

- **WhatsApp Integration**: Handled via n8n webhook → FastAPI route (no auth layer yet)
- **Deployment Target**: AWS Fargate serverless (~$70/month estimated)
- **Context Size**: All governance docs < 200 lines (except roadmap ~250)
- **Product Roadmap**: To be added post-Phase 1 once management feedback collected
