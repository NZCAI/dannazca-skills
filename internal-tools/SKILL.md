---
name: internal-tools
version: 1.0.0
status: minimal
description: Build or extend internal-facing tools with strong RBAC, audit logging, and operational safety nets.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
related-skills:
  - solid
  - service-integration
  - frontend-ui-integration
tags:
  - internal-tools
  - admin-interfaces
  - rbac
  - audit-logging
  - operational-safety
---

# Internal Tools

## Use This Skill When
- Delivering admin consoles, operator dashboards, or workflow utilities that run inside company infrastructure.
- Adding controls that mutate production data (bulk updates, feature toggles, incident tooling).
- Standardizing UX and security for staff-only interfaces.

## Required Inputs
1. Use case description and target personas (support, ops, finance, etc.).
2. Authentication and authorization architecture (SSO provider, role matrix, feature flag groups).
3. Data sources or APIs the tool reads/writes plus their rate limits and audit policies.
4. Operational safeguards (approvals, dry-run modes, confirmation dialogs, logging sinks).

## Workflow
1. Confirm least-privilege access: map roles to allowed actions, ensure all mutations require dual confirmation or dry-run evidence.
2. Scaffold UI/server using the internal tools starter (shared layout, table/grid components, form primitives) to keep UX consistent.
3. Implement API calls with typed clients, wrapping every mutation in idempotent operations and including requester metadata for auditing.
4. Persist audit trails (e.g., Postgres `admin_events`, Cloud Logging) for each action with before/after snapshots where permissible.
5. Add health/observability endpoints plus feature flags to disable risky controls quickly.
6. Write happy-path and failure-path tests: frontend component tests, backend unit tests, plus an end-to-end smoke script hitting the critical action.

## Verification
- Run lint/tests for both frontend and backend pieces (`npm run lint && npm run test`, `pytest tools/internal/tests`, etc.).
- Execute the smoke script against a staging environment, capturing screenshots/log excerpts for reviewers.
- Confirm audit records appear in the designated sink and RBAC denies unauthorized roles.

## Deliverables
- Tool UI/server changes with clearly documented permissions and safeguards.
- Tests plus smoke evidence attached to the PR or rollout doc.
- Runbook snippet covering enable/disable steps, monitoring links, and rollback procedure.
