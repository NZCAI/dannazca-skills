# Containerization Policy: Nazca System

**Version**: 1.0
**Date**: 2026-03-24
**Scope**: Docker strategy for n8n, EdgarTools MCP, FastAPI Bridge

---

## Overview

Containerization enables:
- Consistent, reproducible deployments
- Health check automation (liveness, readiness)
- Graceful degradation + fallback resilience
- HTTP fallback for EdgarTools (reliable, no stdio complexity)

---

## 1. Docker Strategy

### Service 1: EdgarTools MCP (HTTP)

**Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY edgartools-mcp .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

**Health Checks**:
- **Liveness**: GET `/health` (returns 200 if running)
- **Readiness**: GET `/ready` (returns 200 if Edgar API reachable)
- **Startup probe**: 30 second timeout (Edgar API connection can be slow)

**Image**: `nazca:edgartools-mcp-1.0`
**Size**: ~500MB (Python, deps, minimal OS)
**Registry**: Private ECR (AWS)

### Service 2: n8n

**Dockerfile** (if custom):
```dockerfile
FROM n8nio/n8n:latest
# Use official image; minimal customization
ENV DB_TYPE=postgres
ENV DB_HOST=aurora.rds.amazonaws.com
EXPOSE 5678
```

**Health Checks**:
- **Liveness**: GET `/api/health` (returns 200 if n8n running)
- **Readiness**: Check DB connection + workflow load
- **Startup probe**: 60 second timeout (DB init can take time)

**Image**: `nazca:n8n-1.0`
**Size**: ~1GB (Node.js, workflows, deps)
**Registry**: Private ECR (AWS)

### Service 3: FastAPI Bridge

**Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY fastapi-bridge .
RUN pip install -r requirements.txt
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

**Health Checks**:
- **Liveness**: GET `/health`
- **Readiness**: Check connected MCPs + RBAC config loaded
- **Startup probe**: 10 second timeout

**Image**: `nazca:fastapi-bridge-1.0`
**Size**: ~300MB
**Registry**: Private ECR (AWS)

---

## 2. SLAs/SLOs

### n8n Automation
- **Uptime SLO**: 99% (8.64 hours downtime/month acceptable)
- **Execution SLO**: < 30s median latency for automation triggers
- **Error rate SLO**: < 1% execution failures

**Deployment**:
- 2 replicas (redundancy)
- Auto-scaling: scale up if CPU > 70%
- Rolling updates (0 downtime)

### EdgarTools HTTP
- **Uptime SLO**: 99.5% (3.6 hours downtime/month)
- **Response SLO**: < 5s median for queries
- **Error rate SLO**: < 0.5% query failures

**Deployment**:
- 3 replicas (high availability)
- Auto-scaling: scale up if requests/sec > threshold
- Circuit breaker: 3 failures → open (cache returns)

### FastAPI Bridge
- **Uptime SLO**: 99.9% (43.2 minutes downtime/month)
- **Latency SLO**: < 100ms (p99: < 500ms)
- **Error rate SLO**: < 0.1%

**Deployment**:
- 2 replicas minimum (redundancy)
- Auto-scaling: scale up if latency > 200ms
- Rate limiting: 1000 requests/min per role

---

## 3. Resilience Patterns

### Pattern 1: EdgarTools HTTP Fallback
```
User query → FastAPI Bridge → EdgarTools HTTP container
             ├─ Success (< 5s) → return result
             ├─ Timeout (> 5s) → [3 retries with exponential backoff]
             │  ├─ Retry 1: wait 1s
             │  ├─ Retry 2: wait 2s
             │  ├─ Retry 3: wait 4s
             │  └─ Still failing → circuit breaker opens
             │
             └─ Circuit open → return cached data + "using cached data" message
                ├─ Log to CloudWatch (timeout event)
                ├─ Notify user (query executed with stale data)
                └─ Try to recover (background job checks health every 30s)
```

### Pattern 2: Graceful Degradation
If EdgarTools container unhealthy:
- Health check fails (readiness probe returns 500)
- Kubernetes removes from load balancer
- Existing queries: timeout → fallback to cache
- New queries: immediately fallback (no wait)
- Alerts: uptime < SLO threshold

### Pattern 3: n8n Workflow Recovery
If n8n container fails:
- Kubernetes automatically restarts (liveness probe fails)
- In-flight workflows: retry on resume
- Audit log: workflow failure + restart + retry
- Alert: if > 3 restarts in 1 hour

---

## 4. Deployment Rollout (8 Weeks, Bi-Weekly Sprints)

### Sprint 1: Weeks 1–2 (Foundation: RBAC + EdgarTools)
**Parallel Track**: Containerization alongside RBAC enforcement

**Week 1**:
- [ ] EdgarTools Dockerfile + health checks complete
- [ ] Build image, push to ECR
- [ ] Deploy to ECS/Fargate (1 replica, test environment)
- [ ] Verify HTTP accessibility + health checks operational
- [ ] Load test: 100 queries/sec (baseline latency/errors)

**Week 2**:
- [ ] EdgarTools container confirmed stable (< 5s response)
- [ ] Circuit breaker pattern implementation ready
- [ ] RBAC enforcement live at FastAPI Bridge (separate track)
- [ ] Readiness checkpoint: containers + RBAC both passing tests

### Sprint 2: Weeks 3–4 (Observability + FastAPI Container)
**Parallel Track**: Observability logging + FastAPI containerization

**Week 3**:
- [ ] FastAPI Bridge Dockerfile + health checks complete
- [ ] Integrate FastAPI to route via EdgarTools container
- [ ] Build image, push to ECR
- [ ] Deploy (1 replica, test) + verify connectivity to EdgarTools

**Week 4**:
- [ ] Governance event logging live (RBAC + data access)
- [ ] CloudWatch dashboards operational
- [ ] FastAPI container validated with load test (500 req/sec)
- [ ] Readiness checkpoint: observability + FastAPI integration tested

### Sprint 3: Weeks 5–6 (n8n Container + Token Tracking)
**Parallel Track**: n8n containerization + token instrumentation

**Week 5**:
- [ ] n8n Dockerfile (Postgres config, workflow mount) complete
- [ ] Build image, push to ECR
- [ ] Deploy (1 replica, test environment)
- [ ] Migrate test workflows → container-based execution

**Week 6**:
- [ ] n8n workflows validated in container
- [ ] Token tracking per-request instrumented in Langchain
- [ ] Cost aggregation + daily spike alerts configured
- [ ] Circuit breaker pattern for EdgarTools fallback tested

### Sprint 4: Weeks 7–8 (Production Scale + Hardening)
**Deployment**: All services to production at scale

**Week 7**:
- [ ] Scale EdgarTools: 3 replicas + auto-scaling enabled
- [ ] Scale FastAPI: 2 replicas + auto-scaling enabled
- [ ] Scale n8n: 2 replicas (workflow redundancy)
- [ ] Deploy to AWS Fargate production environment
- [ ] Enable circuit breaker + fallback for EdgarTools
- [ ] Production load testing at expected throughput

**Week 8**:
- [ ] SLO monitoring + alerting live (all services)
- [ ] Alert rules validated + Slack/PagerDuty integrated
- [ ] Rollback procedure tested + verified
- [ ] Operational runbook documented for ops team
- [ ] Team handoff complete + training finished

---

## 5. Monitoring & Alerts

### Kubernetes Metrics
- **Pod restarts**: Alert if > 3/hour
- **Container CPU**: Alert if > 80%
- **Container memory**: Alert if > 85%
- **Health check failures**: Alert if liveness fails

### Application Metrics
- **EdgarTools latency**: Alert if p99 > 10s
- **n8n execution failures**: Alert if > 10%
- **FastAPI error rate**: Alert if > 0.1%
- **Circuit breaker opens**: Alert immediately

### Log Aggregation
- All container logs → CloudWatch
- Search by correlation_id (trace requests end-to-end)
- Filter by service (edgartools, n8n, fastapi)
- Archive to S3 (2-year retention)

---

## 6. Configuration Management

### Environment Variables (per container)
```
# EdgarTools HTTP
EDGAR_API_KEY=<secret>
EDGAR_BASE_URL=https://www.sec.gov
CACHE_TTL_SECONDS=3600
CIRCUIT_BREAKER_THRESHOLD=3

# n8n
DB_TYPE=postgres
DB_HOST=aurora.rds.amazonaws.com
DB_USER=<secret>
N8N_BASIC_AUTH_ACTIVE=false  # RBAC via FastAPI

# FastAPI Bridge
RBAC_MATRIX_PATH=/config/team-rbac-tool-matrix.yaml
OBSERVABILITY_ENDPOINT=https://cloudwatch.amazonaws.com
CIRCUIT_BREAKER_ENABLED=true
```

### Secrets Management
- All secrets in AWS Secrets Manager
- Containers mount as env vars (not files)
- Rotate secrets quarterly
- Audit log all secret access

---

## 7. Rollback Plan

**If EdgarTools container has bugs**:
1. Deployment failure detected (health checks fail)
2. Kubernetes auto-rollback to previous image version
3. Alert: rollback executed
4. Circuit breaker: serve cached data to users
5. Debug: investigate logs from CloudWatch
6. Fix: patch image, re-deploy in test environment
7. Retry: once verified, re-deploy to production

**If n8n workflows break**:
1. Liveness check fails
2. Kubernetes restart container
3. In-flight workflows: retry on resume
4. If restart loop detected (3+ restarts/hour): alert ops team
5. Rollback: previous container image version
6. Preserve workflow state (DB not modified)

---

## 8. Cost Optimization

**Container Registry**: Private ECR (AWS)
- Storage: ~2GB images = ~$1–2/month
- Data transfer: included with AWS

**Container Orchestration**: ECS or Kubernetes
- ECS Fargate: pay per CPU/memory/second (serverless)
- Kubernetes: EC2 instances (manage own capacity)
- Recommendation: Start with Fargate (simpler), migrate to K8s if cost > $500/month

**Cost Estimation** (sample):
- EdgarTools (3 replicas, 0.5 CPU, 512MB RAM): ~$20/month
- n8n (2 replicas, 1 CPU, 1GB RAM): ~$30/month
- FastAPI (2 replicas, 0.5 CPU, 512MB RAM): ~$20/month
- **Total**: ~$70/month (serverless, auto-scaling)

---

**Status**: Ready for Week 1 implementation
**Owner**: DevOps/Ops team (you oversee)
**Approval**: Required before Week 1 starts
