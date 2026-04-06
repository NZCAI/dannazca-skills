#!/usr/bin/env python3
"""
context-manager skill: Token-efficient project context for Nazca Agentic System.
Enables multi-agent + multi-team coordination without embedding full documents.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

CONTEXT_PATH = Path("/Users/dannazca/Factory/dannazca-skills/governance/project-context.yaml")

def load_context() -> Dict[str, Any]:
    """Load current project context from YAML."""
    if not CONTEXT_PATH.exists():
        return {"error": "project-context.yaml not found"}
    with open(CONTEXT_PATH) as f:
        return yaml.safe_load(f)

def save_context(context: Dict[str, Any]) -> None:
    """Save updated context to YAML."""
    with open(CONTEXT_PATH, 'w') as f:
        yaml.dump(context, f, default_flow_style=False)

def load_state() -> Dict[str, Any]:
    """Return minimal project state (< 200 lines)."""
    ctx = load_context()
    if "error" in ctx:
        return ctx

    return {
        "project": ctx["project"],
        "current_phase": ctx["current_phase"],
        "current_sprint": ctx["current_sprint"],
        "owner": ctx["owner"],
        "team_count": len([t for t in ctx["team"] if isinstance(t, dict)]),
        "key_decisions": ctx["key_decisions"],
        "active_blockers": ctx["active_blockers"],
        "sprint_end": ctx.get("sprint_end"),
        "governance_docs": [d["name"] for d in ctx.get("governance_docs", [])],
        "next_milestone": ctx["milestones"][ctx["current_sprint"]] if ctx["current_sprint"] <= len(ctx["milestones"]) else None,
    }

def update_team(role: str, status: str, person: Optional[str] = None) -> Dict[str, Any]:
    """Update team member status."""
    ctx = load_context()
    if "error" in ctx:
        return ctx

    for member in ctx["team"]:
        if isinstance(member, dict) and member.get("role") == role:
            member["status"] = status
            if person:
                member["person"] = person
            break

    save_context(ctx)
    return {"status": "updated", "role": role, "new_status": status}

def log_decision(title: str, rationale: str, category: Optional[str] = None) -> Dict[str, Any]:
    """Log a project decision."""
    ctx = load_context()
    if "error" in ctx:
        return ctx

    decision = {
        "title": title,
        "rationale": rationale,
        "date": datetime.now().isoformat(),
        "category": category or "general"
    }

    if "decision_log" not in ctx:
        ctx["decision_log"] = []

    ctx["decision_log"].append(decision)
    save_context(ctx)
    return {"status": "logged", "decision": title}

def add_blocker(blocker: str, severity: str = "medium") -> Dict[str, Any]:
    """Track active blocker."""
    ctx = load_context()
    if "error" in ctx:
        return ctx

    ctx["active_blockers"].append({
        "issue": blocker,
        "severity": severity,
        "logged": datetime.now().isoformat()
    })
    save_context(ctx)
    return {"status": "blocker_added", "issue": blocker}

def remove_blocker(blocker_text: str) -> Dict[str, Any]:
    """Resolve a blocker."""
    ctx = load_context()
    if "error" in ctx:
        return ctx

    ctx["active_blockers"] = [
        b for b in ctx["active_blockers"]
        if not (isinstance(b, dict) and b.get("issue") == blocker_text)
    ]
    save_context(ctx)
    return {"status": "blocker_resolved", "issue": blocker_text}

def handoff(from_role: str, to_role: str, context_summary: str) -> Dict[str, Any]:
    """Log agent/team handoff."""
    ctx = load_context()
    if "error" in ctx:
        return ctx

    if "handoffs" not in ctx:
        ctx["handoffs"] = []

    ctx["handoffs"].append({
        "from": from_role,
        "to": to_role,
        "context": context_summary,
        "timestamp": datetime.now().isoformat()
    })
    save_context(ctx)
    return {"status": "handoff_logged", "from": from_role, "to": to_role}

def advance_sprint() -> Dict[str, Any]:
    """Move to next sprint (call at end of 2-week cycle)."""
    ctx = load_context()
    if "error" in ctx:
        return ctx

    current = ctx["current_sprint"]
    if current >= 4:
        return {"status": "error", "message": "All 4 sprints completed"}

    ctx["current_sprint"] = current + 1
    save_context(ctx)
    return {"status": "advanced", "new_sprint": current + 1}

def main(action: str, **kwargs) -> str:
    """CLI entry point."""
    actions = {
        "load-state": lambda: load_state(),
        "update-team": lambda: update_team(kwargs.get("role"), kwargs.get("status"), kwargs.get("person")),
        "log-decision": lambda: log_decision(kwargs.get("title"), kwargs.get("rationale"), kwargs.get("category")),
        "add-blocker": lambda: add_blocker(kwargs.get("blocker"), kwargs.get("severity", "medium")),
        "remove-blocker": lambda: remove_blocker(kwargs.get("blocker")),
        "handoff": lambda: handoff(kwargs.get("from"), kwargs.get("to"), kwargs.get("context")),
        "advance-sprint": lambda: advance_sprint(),
    }

    if action not in actions:
        return json.dumps({"error": f"Unknown action: {action}"})

    result = actions[action]()
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <action> [--key value ...]")
        sys.exit(1)

    action = sys.argv[1]
    kwargs = {}
    for i in range(2, len(sys.argv), 2):
        if sys.argv[i].startswith("--"):
            key = sys.argv[i][2:]
            value = sys.argv[i+1] if i+1 < len(sys.argv) else None
            kwargs[key] = value

    print(main(action, **kwargs))
