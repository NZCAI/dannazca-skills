# FastAPI Bridge — ECS Fargate Deployment Handoff

**Date**: April 9, 2026
**Sprint**: S2 — Week 1 (Apr 9 – Apr 22)
**Owner**: admin
**Status**: Phase 2 (Observability) — ECS Fargate Live ✅
**Related Documents**:
- `Nazca_Technical_Specification_v2.md` — FastAPI Bridge architecture
- `Nazca_System_Architecture_with_Delivery_Dates.md` — Checkpoint 2 delivery timeline
- `Containerization_Policy.md` — Docker strategy
- `project-context.yaml` — Master state file (updated this session)

---

## Summary

The FastAPI Bridge container was deployed to AWS ECS Fargate on April 9, 2026 — ahead of the April 27 target. The service is publicly accessible and healthy. This document captures all decisions, fixes, and operational details needed to continue from this point.

---

## What Was Deployed

| Resource | Value |
|----------|-------|
| ECS Cluster | `nazca-cluster` (us-east-1) |
| ECS Service | `nazca-fastapi-service` |
| Task Definition | `nazca-fastapi:1` |
| CPU / Memory | 512 vCPU / 1024 MB |
| Launch Type | Fargate |
| Public URL | `http://32.192.36.164:8000` (**ephemeral**) |
| ECR Image | `159903201031.dkr.ecr.us-east-1.amazonaws.com/nazca-fastapi-bridge:latest` |
| Image Platform | `linux/amd64` |
| CloudWatch Logs | `/ecs/nazca-fastapi` |
| Security Group | `sg-0707d5ef2fea66692` (inbound TCP 8000 from 0.0.0.0/0) |
| Subnet | `subnet-0f2f31f4051702e41` (us-east-1a, public) |
| VPC | `vpc-01fb6b08b8454ce02` |

### Health Check Results (verified Apr 9)

```
GET /health  → {"status":"healthy","version":"0.1.0"}
GET /ready   → {"status":"ready","database":"connected","edgartools":"mock"}
POST /auth/* → 401 (auth working correctly)
```

---

## IAM Role Created

**Role**: `ecsTaskExecutionRole`
- Trust policy: `ecs-tasks.amazonaws.com`
- Managed policy: `AmazonECSTaskExecutionRolePolicy` (ECR pull + CloudWatch logs)
- Inline policy: `SecretsManagerAccess` — `GetSecretValue` on `nazca/fastapi-bridge/prod`

---

## Secrets Manager

**Secret**: `nazca/fastapi-bridge/prod`
**ARN**: `arn:aws:secretsmanager:us-east-1:159903201031:secret:nazca/fastapi-bridge/prod-TLUdFw`

Keys injected into ECS task at runtime:
- `OPENAI_API_KEY`
- `JWT_SECRET_KEY`
- `EDGAR_IDENTITY`

> **Fix applied this session**: `EDGAR_IDENTITY` key had a trailing tab character in Secrets Manager (stored as `"EDGAR_IDENTITY\t"`), causing `ResourceInitializationError` on ECS task launch. Fixed by rewriting the secret with Python `json.loads(raw, strict=False)` + `.strip()` on all keys.

---

## Critical: Image Platform for ECS Fargate

The original ECR image was built on Apple Silicon (arm64), which is incompatible with ECS Fargate (linux/amd64). Rebuilt and pushed with:

```bash
docker buildx build --platform linux/amd64 \
  --tag 159903201031.dkr.ecr.us-east-1.amazonaws.com/nazca-fastapi-bridge:latest \
  --push .
```

**Rule going forward**: All ECR pushes for Fargate must use `--platform linux/amd64`. This does not affect the local dev container (`docker compose -f docker-compose.dev.yml up`), which continues to use the native arm64 image.

---

## Known Limitations

| Limitation | Severity | Mitigation |
|------------|----------|------------|
| Task IP is ephemeral (changes on restart) | Medium | Add ALB before team rollout (Sprint 2) |
| SQLite has no persistence on ECS (no EFS) | Low | PostgreSQL migration at Checkpoint 4 |
| LangGraph agent nodes return mock outputs | Medium | Dedicated session — pipeline is E2E functional |

---

## Deferred Items (Do Not Start Unless Asked)

| Item | Reason Deferred |
|------|----------------|
| ALB / stable HTTPS URL | Sprint 2 — base ECS deployment confirmed first |
| Real LLM calls in agent nodes | Needs dedicated session |
| Intelligence Desk Stage 2 (FastAPI auth) | Follows this deployment |
| Celery + Redis job queue | Checkpoint 4 |
| PostgreSQL migration | Checkpoint 4 |
| n8n automation wiring | Checkpoint 3 |
| EdgarTools MCP container | Second container after FastAPI stable |
| AWS credentials rotation | `AKIASKOXZG4DVI5MWF7H` was shared — rotate in IAM console |

---

## How to Restart / Redeploy

```bash
# Rebuild and push (always use linux/amd64)
cd /Users/dannazca/Factory/fastapi-bridge
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  159903201031.dkr.ecr.us-east-1.amazonaws.com
docker buildx build --platform linux/amd64 \
  --tag 159903201031.dkr.ecr.us-east-1.amazonaws.com/nazca-fastapi-bridge:latest \
  --push .

# Force redeploy existing service
aws ecs update-service --cluster nazca-cluster \
  --service nazca-fastapi-service \
  --force-new-deployment --region us-east-1

# Wait for stability
aws ecs wait services-stable \
  --cluster nazca-cluster \
  --services nazca-fastapi-service --region us-east-1

# Get new public IP
TASK_ARN=$(aws ecs list-tasks --cluster nazca-cluster \
  --service-name nazca-fastapi-service --region us-east-1 \
  --query "taskArns[0]" --output text)
ENI_ID=$(aws ecs describe-tasks --cluster nazca-cluster --tasks $TASK_ARN \
  --region us-east-1 \
  --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" \
  --output text)
aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID \
  --query "NetworkInterfaces[0].Association.PublicIp" --output text --region us-east-1
```

---

## Next Session Focus

1. **ALB** — stable HTTPS URL for the team (prerequisite for Intelligence Desk Stage 2)
2. **Intelligence Desk Stage 2** — wire FastAPI auth into the Streamlit UI
3. **CloudWatch Dashboards** — per-role observability for team access
4. **Governance Event Logging** — audit trail for all workflow triggers
