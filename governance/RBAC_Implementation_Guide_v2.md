# RBAC Implementation Guide v2

**Version**: 2.0 (data-centric)
**Date**: 2026-03-24
**For**: Nazca Data Analysis System

---

## Quick Reference: Who Has Access?

| Role | Edgar | S3 | n8n | Postgres | UI | SageMaker |
|------|-------|----|----|----------|----|----|
| Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Data Scientist | ✓ query | ✓ upload | ✓ exec | ✓ r/w | ✓ | - |
| ML Trainee | - | ✓ | - | ✓ r/w | ✓ | ✓ |
| Auto Trainee | - | - | ✓ maintain | - | ✓ | - |
| Analyst | - | - | - | - | ✓ read-only | - |
| Partner | - | - | - | - | ✓ health only | - |

---

## Common Workflows

### Workflow 1: Analyst Needs Data Report
```
1. Analyst opens ticket: "Need Edgar analysis on company X"
2. You (admin) review
3. You task AI-Data-Analyst agent: "Extract 10-K filings for X, create report"
4. Agent runs Edgar queries (logged), generates markdown report
5. Report saved to S3, link sent to analyst
```

### Workflow 2: ML Trainee Deploys Model
```
1. ML Trainee trains model in SageMaker
2. Exports to S3
3. Deploys Lambda inference function
4. All logged to governance trail
```

### Workflow 3: Automations Trainee Updates n8n Flow
```
1. Auto Trainee designs flow in n8n (test environment)
2. Documents changes
3. Opens governance PR (n8n flow update)
4. Requires 2 approvals (you + peer review)
5. Merge to main → deployed
```

### Workflow 4: Data Scientist Uploads Data
```
1. Data Scientist processes raw data locally
2. Uploads to S3 with versioning
3. Action logged: "alice@company.com uploaded market_data_2026-03-24.csv"
4. Postgres updated with metadata
```

---

## Access Request Process

**Analyst needs Edgar access?**
- Escalation not available (Design choice: Data Scientist queries, AI-Data-Analyst agent queries)
- Workaround: Open ticket → You invoke AI-Data-Analyst agent

**ML Trainee needs EC2 instance?**
- Request in ticket (what for, how long)
- You approve
- Temporary access granted + time-bound

**New tool needed?**
- Proposal: tool name, use case, who accesses
- You evaluate (security, architecture fit)
- Add to governance repo
- Deploy in next release

---

## Approval Checklist

**Before granting new access:**
- [ ] Does it fit the data access pattern (not live execution)?
- [ ] Is it time-bound or permanent?
- [ ] Who is responsible for using it correctly?
- [ ] How is it logged/audited?

---

## Troubleshooting

**Problem**: Analyst can't see dashboard
- Check: Does analyst have UI access? Yes (analyst_mode: true)
- Check: Is dashboard data populated? (Check S3/Postgres)
- Solution: Load data from S3 or refresh Postgres

**Problem**: Data Scientist can't upload to S3
- Check: Role is data_scientist? Yes
- Check: S3 write permission? Yes
- Check: AWS credentials? (Check local AWS config)
- Solution: Verify IAM role in AWS console

**Problem**: ML Trainee can't run SageMaker job
- Check: Role is ml_trainee? Yes
- Check: SageMaker access? Yes
- Check: IAM role has SageMaker permissions? (Check AWS console)
- Solution: Add SageMaker IAM policy to ml_trainee role

**Problem**: Auto Trainee PR blocked
- Check: Is PR to n8n flows? Yes
- Check: Are there 2 approvals? No
- Solution: You + peer must review + approve

---

## Deployment Timeline

**Week 1:**
- [ ] Deploy team RBAC (team-rbac-tool-matrix.yaml)
- [ ] Grant Data Scientist S3 + Edgar access
- [ ] Test n8n execution

**Week 2:**
- [ ] Enable ML Trainee SageMaker + Lambda
- [ ] Enable Automations Trainee n8n maintenance
- [ ] Verify audit logging works

**Week 3:**
- [ ] Enable Analyst UI access
- [ ] Enable Partner system health view
- [ ] Deploy AI-Data-Analyst agent

**Week 4:**
- [ ] Monitor audit logs for issues
- [ ] Collect team feedback
- [ ] Refine policies as needed

---

## Audit Logging Destinations

- **n8n pushes**: GitHub commit log + governance PR
- **Edgar queries**: CloudWatch + governance audit trail
- **S3 uploads**: CloudWatch + versioning metadata
- **Config changes**: Git history + audit log

---

## Next Steps

1. ✅ RBAC_Framework_v2.md — Role hierarchy defined
2. ✅ team-rbac-tool-matrix.yaml — Team permissions defined
3. ✅ agent-rbac-tool-matrix.yaml — Agent permissions defined
4. **↓ Next**:
   - Deploy RBAC to FastAPI Bridge MCP
   - Set up audit logging
   - Create dashboards for monitoring
   - Run pilot with Data Scientist
   - Gather feedback + iterate

---

**Status**: Ready for deployment
**Questions?** Open issue in governance repo
