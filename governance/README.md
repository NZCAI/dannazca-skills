# Governance — Document Index

This folder is the single source of truth for Nazca system governance, architecture, and RBAC policy.

**Last updated:** April 8, 2026

---

## Active Documents

### Architecture & Specification

| File | Purpose | Audience |
|------|---------|----------|
| `Nazca_Technical_Specification_v2.md` | Full technical architecture — system components, MCP topology, workflow specs (5A, 5B, Market Analysis), software requirements | Engineers, Data Scientists |
| `Nazca_System_Architecture_with_Delivery_Dates.md` | Visual system architecture + sprint delivery timeline, checkpoint criteria, critical path | All team members |

### Governance Blueprint

| File | Purpose | Audience |
|------|---------|----------|
| `Nazca_Governance_Blueprint_v1.md` | **LEAN version** — quick-reference governance: RBAC framework summary, observability overview, delivery roadmap summary | Team leads, Ops, Governance owners |
| `Nazca_Governance_Blueprint_v1_extended.md` | **EXTENDED version** — detailed governance policies: workflow execution model, RBAC matrix, data source access control, error handling, data privacy, governance checklist | Data Scientists, Compliance |

### Policy Frameworks

| File | Purpose |
|------|---------|
| `RBAC_Framework_v2.md` | Role definitions, permission categories, enforce rules |
| `RBAC_Implementation_Guide_v2.md` | How to implement RBAC at the FastAPI middleware layer |
| `Observability_Framework.md` | Trace propagation schema, governance event logging spec, token tracking model |
| `Containerization_Policy.md` | Docker strategy, resilience patterns, SLOs, deployment policies |
| `project-context.yaml` | Active project metadata, sprint state, decision log |

### RBAC Matrices (`rbac/`)

| File | Purpose |
|------|---------|
| `rbac/team-rbac-tool-matrix.yaml` | Human team role → tool permission mappings (machine-readable) |
| `rbac/agent-rbac-tool-matrix.yaml` | AI agent role → tool permission mappings (machine-readable) |

---

## Archive (`archive/`)

Historical documents preserved for reference — **not active specs, do not use for implementation.**

| File | Why Archived |
|------|-------------|
| `8-Week-Technical-Roadmap.md` | Superseded by `Nazca_System_Architecture_with_Delivery_Dates.md` |
| `Architectural_Feedback.md` | Point-in-time design review artifact (March 2026) |
| `Architectural_Feedback_v2.md` | Point-in-time design review artifact (March 2026) |

---

## Document Relationships

```
Nazca_Technical_Specification_v2.md     ←──── defines WHAT to build
        ↕ cross-references
Nazca_Governance_Blueprint_v1.md        ←──── defines WHO / governance / delivery
        ↓ "see extended for details"
Nazca_Governance_Blueprint_v1_extended.md

Nazca_System_Architecture_with_Delivery_Dates.md  ←── visual roadmap, references both above
```

Both blueprint documents are intentionally maintained in two versions (LEAN + EXTENDED) for context efficiency — the LEAN version is loaded by default for quick lookups; the EXTENDED version is loaded when detailed policy is needed.
