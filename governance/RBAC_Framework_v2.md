# RBAC Framework v2: Nazca Data Analysis System

**Version**: 2.0 (data-centric, corrected)
**Date**: 2026-03-24
**Scope**: Human team roles + Agent/Subagent roles

---

## Role Hierarchy

```
Admin (You)
├─ Data Scientist → S3 uploads, all MCPs
├─ ML Trainee → SageMaker, Lambda, S3, Postgres
├─ Automations Trainee → n8n flows + docs
├─ Investment Analyst → UI only
└─ Partner → Read system health + scores

Agents (Independent paths):
├─ Product Manager (Roadmap, dependency risk)
├─ Code-Reviewer (Pre-commit code reviews)
└─ AI-Data-Analyst (Edgar, Dropbox, Notion MCPs)
```

---

## Tools & Access Levels

| Tool | Admin | Data Scientist | ML Trainee | Auto Trainee | Analyst | Partner | AI-Data-Analyst |
|------|-------|---|---|---|---|---|---|
| **n8n** | ✓ | ✓ exec | - | ✓ design/maintain | - | - | - |
| **mcp-edgartools** | ✓ | ✓ query | - | - | ✗ | ✓ read-only | ✓ full |
| **Postgres** | ✓ | ✓ read/write | ✓ read/write | - | - | - | ✓ read |
| **S3** | ✓ | ✓ upload | ✓ upload | - | - | - | - |
| **Lambda** | ✓ | - | ✓ deploy/test | - | - | - | - |
| **SageMaker** | ✓ | - | ✓ train/deploy | - | - | - | - |
| **UI** | ✓ | ✓ | ✓ | ✓ | ✓ analyst mode | ✓ read-only | - |

---

## Role Definitions (Human Team)

### Admin (You)
- Full AWS access, all MCPs, governance control
- Manages PRD, roadmap, system health oversight

### Data Scientist
- Execute n8n automation flows
- Full mcp-edgartools query access
- Read/write Postgres (Aurora/RDS) for data updates
- Upload processed data to S3
- **Restriction**: Not full AWS access (no Lambda/SageMaker/EC2)

### ML Trainee
- S3 read/write (store models, datasets)
- EC2 access (compute, experiments)
- Lambda deploy/test (inference functions)
- SageMaker full access (training, hyperparameter tuning)
- Postgres read/write (model metadata, results)
- **Scope**: ML/data science work only

### Automations Trainee (2x)
- n8n: design, maintain, test, authorize pushes
- No MCP access (data science role handles that)
- Responsible for documentation + runbooks

### Investment Analyst
- UI only (analysis mode)
- Request data/reports via tickets
- Read analysis results, dashboards
- **Cannot**: Direct tool access

### Partner
- View system health (uptime, performance)
- View code review scores, readiness metrics
- View token usage, cost tracking
- Analytics dashboard read-only
- **Cannot**: Modify anything, access data

---

## Agent/Subagent Roles

### Product Manager Agent
- Access: PRD repo, roadmap docs, dependency tracking
- Permission: Read/write roadmap, update requirements
- Approver: You (admin) for roadmap changes

### Code-Reviewer Agent
- Access: Source code, PR metadata
- Permission: Comment, request changes (pre-commit)
- **Cannot**: Approve merges (humans do that)

### AI-Data-Analyst Agent
- Access: mcp-edgartools (full), Dropbox MCP, Notion MCP
- Permission: Run queries, extract data, create reports
- Scope: Financial analysis, competitive research, insights

---

## High-Risk Operations (Audit Logged)

| Operation | Who | Restriction | Notes |
|-----------|-----|-------------|-------|
| S3 upload | Data Scientist | Audit logged | Track data lineage |
| Edgar query | AI-Data-Analyst | Audit logged | Compliance tracking |
| n8n push | Auto Trainee | 2-approver gate | Your + peer review |
| System config change | Admin only | Audit logged | Any AWS permission change |

---

## Deny-by-Default Policy

✓ Explicit allow only — no implicit access
✓ New tools require governance PR (proposal + approval)
✓ Role escalation requires ticket + approval
✓ All high-risk ops logged to audit trail

---

## Quick Escalation Workflow

**Analyst needs Edgar access?**
1. Open issue: "Need Edgar query for X research"
2. Data Scientist or you approves
3. Add to AI-Data-Analyst agent prompt scope
4. Confirm access works

**ML Trainee needs EC2 instance?**
1. Request in ticket with use case
2. You approve (check cost/resource)
3. Grant temporary access (time-bound)

**New tool needed?**
1. Proposal: what tool, why, who accesses
2. Security check: does it fit architecture?
3. Add to governance repo
4. Enable in next deployment

---

**Status**: Ready for implementation
**Next**: Create team-rbac-tool-matrix.yaml and agent-rbac-tool-matrix.yaml
