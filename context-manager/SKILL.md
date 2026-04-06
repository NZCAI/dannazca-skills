# context-manager Skill

Load and manage project context for Nazca Agentic System development. Enables token-efficient multi-agent + multi-team coordination.

## Purpose

Provide unified project state to Claude agents and Factory.ai CLI without requiring full document re-reads. Reduces context size by 60–80% compared to embedding full governance documents.

## Features

- **Load project state** — Current phase, sprint, team status, decisions
- **Update context** — Track who's working on what, active blockers
- **Link governance docs** — Reference RBAC, observability, containerization policies
- **Team handoff support** — Agent-to-agent context propagation
- **Token-efficient** — <200 lines per output by design

## Usage

### Load Current Context
```bash
factory.ai skill run context-manager --action load-state
```

Returns:
- Current sprint + phase
- Active team members
- Key decisions + blockers
- Governance doc links

### Update Team Status
```bash
factory.ai skill run context-manager --action update-team \
  --role ml_trainee --status onboarding --person alice
```

### Track Decision
```bash
factory.ai skill run context-manager --action log-decision \
  --title "EdgarTools HTTP fallback pattern" \
  --rationale "Simpler than stdio, supports resilience"
```

### Agent Handoff
```bash
factory.ai skill run context-manager --action handoff \
  --from "data-scientist" \
  --to "code-reviewer" \
  --context "Sprint 2 observability implementation"
```

## Files

- `/Users/dannazca/Factory/dannazca-skills/context-manager/main.py` — Skill implementation (~120 lines)
- `/Users/dannazca/Factory/dannazca-skills/governance/project-context.yaml` — State file (source of truth)
- `/Users/dannazca/Factory/dannazca-skills/context-manager/SKILL.md` — This file

## Integration

**Claude**: Agents invoke via `/context-manager` or skill tool
**Factory.ai CLI**: Invoke via `factory.ai skill run context-manager`

## Notes

- `project-context.yaml` is version-controlled (track decisions in git)
- Skill only edits context file, never modifies governance docs directly
- All outputs < 200 lines (token efficiency requirement)
- Team members update status via skill (single source of truth)
