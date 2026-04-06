---
name: service-integration
version: 1.0.0
status: minimal
description: Extend or wire backend services in a shared monorepo while respecting ownership boundaries, observability, and rollout safeguards.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
related-skills:
  - solid
  - internal-tools
tags:
  - backend-development
  - service-architecture
  - observability
  - integration-testing
  - rollout-safeguards
---

# Service Integration

## Use This Skill When
- A feature spans multiple services or requires changes to shared protobuf/GraphQL contracts.
- You must call into an owned dependency (payments, auth, notification fanout, etc.) from another service.
- The work touches production pathways that need explicit rollout, alerting, and dashboards.

## Required Inputs
1. Source issue or RFC describing the integration scenario and success metrics.
2. Owning team directories (e.g., `services/payments`, `services/notifications`).
3. API/interface contracts (proto files, OpenAPI specs, thrift IDLs) and versioning rules.
4. Observability requirements: log fields, metrics, traces, alerts, and dashboards that must be updated.

## Workflow
1. Identify ownership boundaries: confirm which service exposes the contract versus consumes it and whether changes need cross-team approval.
2. Update shared interfaces first (proto/OpenAPI). Regenerate clients/servers via the repo’s codegen script (e.g., `bazel run //:generate`, `buf generate`).
3. Implement service logic behind a configuration flag or gradual rollout control (percentage rollout, region allowlist, etc.).
4. Add persistence or cache migrations with backwards-compatible states; include rollback notes.
5. Instrument the path with structured logs, metrics, and traces aligned to SLO dashboards. Ensure alert thresholds exist for the new signals.
6. Extend regression, contract, and integration tests (unit tests under each service plus multi-service smoke tests if supported by the repo’s test harness).
7. Update playbooks/runbooks with the new steps if the integration affects on-call procedures.

## Verification
- Run unit tests for each touched service (e.g., `go test ./...`, `pytest services/payments/tests`, or `cargo test -p service`).
- Execute contract/integration tests (`make integration-test`, `docker compose up test-runner`, etc.) when available.
- Validate that new metrics/logs are emitted locally or in staging by hitting the endpoint with sample payloads.

## Deliverables
- Updated interface definitions plus regenerated artifacts checked into the repo.
- Service code changes guarded by rollout controls with documented fallback steps.
- Tests and observability artifacts proving the path works before shipping.
