#!/usr/bin/env python3
"""
cohort_manager.py — Nazca Cohort State Manager

Manages enrichment state across sessions:
  - Reads/writes master state file (nazca_enrichment_state.json)
  - Creates/updates dated cohort snapshots
  - Handles add/remove company operations
  - Computes deltas between snapshots
  - Reports cohort status

Usage:
  python3 cohort_manager.py --setup
  python3 cohort_manager.py --action status [--cohort NAME]
  python3 cohort_manager.py --cohort LATAM_IPO --action snapshot --companies '[...]' [--date 2026-05]
  python3 cohort_manager.py --cohort LATAM_IPO --action add --companies '[...]'
  python3 cohort_manager.py --cohort LATAM_IPO --action remove --names '["Clara","Konfio"]'
  python3 cohort_manager.py --cohort LATAM_IPO --action delta --from 2026-05 --to 2026-11
  python3 cohort_manager.py --action update-state
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

COHORTS_DIR = Path("/Users/dannazca/Factory/cohorts")
STATE_FILE = COHORTS_DIR / "nazca_enrichment_state.json"
VARIABLE_REGISTRY_FILE = COHORTS_DIR / "variable_registry.json"

# ─── Default state structure ──────────────────────────────────────────────────

DEFAULT_STATE = {
    "version": "1.0",
    "last_updated": None,
    "dead_sources": [
        {"name": "Financial Datasets API", "reason": "$0 balance", "dead_since": "2026-05-07"},
        {"name": "Brightdata", "reason": "HTTP 401", "dead_since": "2026-04-01"}
    ],
    "cohorts": {
        "LATAM_IPO": {
            "description": "LatAm companies approaching or post-IPO",
            "last_run": None,
            "companies": [],
            "snapshots": []
        },
        "US_IPO": {
            "description": "US companies approaching or post-IPO",
            "last_run": None,
            "companies": [],
            "snapshots": []
        },
        "Hot_Startups": {
            "description": "High-momentum private startups — LatAm, US, blend",
            "last_run": None,
            "companies": [],
            "snapshots": []
        },
        "Publicas_GUR": {
            "description": "96 public comparable companies for OLS calibration",
            "last_run": None,
            "companies": [],
            "snapshots": []
        }
    }
}

DEFAULT_VARIABLE_REGISTRY = {
    "version": "1.0",
    "variables": {
        "revenue_usd":              {"source": "EDGAR", "fallback": "OLS model", "confidence_primary": 1.00, "confidence_fallback": 0.65, "applies_to": "all"},
        "gross_profit_usd":         {"source": "EDGAR", "fallback": None,        "confidence_primary": 1.00, "confidence_fallback": None, "applies_to": "public"},
        "gross_margin_pct":         {"source": "derived", "formula": "gross_profit / revenue", "confidence_primary": 0.95, "applies_to": "public"},
        "operating_income_usd":     {"source": "EDGAR", "fallback": None,        "confidence_primary": 1.00, "note": "N/A for IFRS 20-F", "applies_to": "public"},
        "operating_margin_pct":     {"source": "derived", "formula": "operating_income / revenue", "confidence_primary": 0.95, "applies_to": "public"},
        "net_income_usd":           {"source": "EDGAR", "fallback": None,        "confidence_primary": 0.90, "note": "Often N/A", "applies_to": "public"},
        "net_margin_pct":           {"source": "derived", "confidence_primary": 0.90, "applies_to": "public"},
        "total_assets_usd":         {"source": "EDGAR", "fallback": None,        "confidence_primary": 1.00, "applies_to": "public"},
        "total_liabilities_usd":    {"source": "EDGAR", "fallback": None,        "confidence_primary": 1.00, "applies_to": "public"},
        "debt_ratio":               {"source": "derived", "formula": "total_liabilities / total_assets", "confidence_primary": 0.95, "applies_to": "public"},
        "ev_revenue_multiple":      {"source": "Damodaran Jan 2026", "confidence_primary": 0.85, "applies_to": "all"},
        "revenue_cagr_2yr":         {"source": "EDGAR trends", "confidence_primary": 0.90, "applies_to": "public"},
        "capital_efficiency_score": {"source": "derived", "formula": "revenue/assets percentile within cohort", "confidence_primary": 0.85, "applies_to": "public"},
        "jurisdiction_risk_score":  {"source": "rules", "scale": "1-10", "confidence_primary": 0.80, "applies_to": "all"},
        "pricing_power_score":      {"source": "rules", "scale": "1-10", "confidence_primary": 0.80, "applies_to": "all"},
        "sector_growth_cagr":       {"source": "rules/constants", "confidence_primary": 0.85, "applies_to": "all"},
        "hc_momentum_90d":          {"source": "Harmonic", "confidence_primary": 0.85, "applies_to": "private"},
        "web_traffic_90d":          {"source": "Harmonic", "confidence_primary": 0.72, "note": "Below 0.75 → record as N/A", "applies_to": "private"},
        "linkedin_growth_180d":     {"source": "Harmonic", "confidence_primary": 0.80, "applies_to": "private"}
    },
    "confidence_floor": 0.75,
    "notes": "Variables below confidence_floor are recorded as N/A, not as a score. N/A means no data, not bad company."
}


# ─── I/O helpers ──────────────────────────────────────────────────────────────

def ensure_cohorts_dir():
    COHORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return None
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state: dict):
    ensure_cohorts_dir()
    state["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def load_snapshot(cohort: str, date: str) -> dict:
    path = COHORTS_DIR / f"{cohort}_{date}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def save_snapshot(cohort: str, date: str, snapshot: dict):
    ensure_cohorts_dir()
    path = COHORTS_DIR / f"{cohort}_{date}.json"
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)
    return path


# ─── Setup ────────────────────────────────────────────────────────────────────

def cmd_setup():
    ensure_cohorts_dir()
    if STATE_FILE.exists():
        print(f"State file already exists: {STATE_FILE}")
        print("Loading existing state...")
        state = load_state()
    else:
        state = DEFAULT_STATE.copy()
        save_state(state)
        print(f"✓ Created state file: {STATE_FILE}")

    if not VARIABLE_REGISTRY_FILE.exists():
        with open(VARIABLE_REGISTRY_FILE, "w") as f:
            json.dump(DEFAULT_VARIABLE_REGISTRY, f, indent=2)
        print(f"✓ Created variable registry: {VARIABLE_REGISTRY_FILE}")

    print(f"\nSetup complete. Cohorts available:")
    for name, meta in state["cohorts"].items():
        print(f"  {name}: {meta['description']}")


# ─── Status ───────────────────────────────────────────────────────────────────

def cmd_status(cohort_name: str = None):
    state = load_state()
    if not state:
        print("No state file found. Run: cohort_manager.py --setup")
        return

    print(f"\n{'='*60}")
    print(f"NAZCA ENRICHMENT STATE  (as of {state.get('last_updated', 'unknown')})")
    print(f"{'='*60}")

    dead = state.get("dead_sources", [])
    if dead:
        print(f"\n⚠️  Dead sources (skip these):")
        for s in dead:
            print(f"   • {s['name']}: {s['reason']}")

    cohorts = state.get("cohorts", {})
    targets = {cohort_name: cohorts[cohort_name]} if cohort_name and cohort_name in cohorts else cohorts

    print(f"\n{'─'*60}")
    needs_action = []

    for name, meta in targets.items():
        companies = meta.get("companies", [])
        total = len(companies)
        enriched = sum(1 for c in companies if c.get("enriched"))
        pending = total - enriched
        last_run = meta.get("last_run", "never")
        snapshots = meta.get("snapshots", [])

        flag = " ← NEEDS ACTION" if pending > 0 else ""
        print(f"\n  {name}")
        print(f"    Companies   : {total} total | {enriched} enriched | {pending} pending{flag}")
        print(f"    Last run    : {last_run}")
        print(f"    Snapshots   : {len(snapshots)} ({', '.join(snapshots) if snapshots else 'none'})")
        if pending > 0:
            needs_action.append(name)

    if needs_action:
        print(f"\n{'─'*60}")
        print(f"⚡ Next actions needed:")
        for name in needs_action:
            meta = cohorts[name]
            pending_companies = [c["name"] for c in meta.get("companies", []) if not c.get("enriched")]
            print(f"   {name}: enrich {len(pending_companies)} companies")
            if pending_companies[:5]:
                print(f"     First batch: {', '.join(pending_companies[:5])}")
    else:
        print(f"\n✓ All cohorts are up to date.")

    print(f"{'='*60}\n")


# ─── Snapshot ─────────────────────────────────────────────────────────────────

def cmd_snapshot(cohort_name: str, companies_json: str, date: str = None):
    if not date:
        date = datetime.now().strftime("%Y-%m")

    state = load_state()
    if not state:
        print("No state file. Run --setup first.")
        sys.exit(1)

    if cohort_name not in state["cohorts"]:
        print(f"Unknown cohort: {cohort_name}")
        print(f"Available: {list(state['cohorts'].keys())}")
        sys.exit(1)

    try:
        new_companies = json.loads(companies_json)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON for --companies: {e}")
        sys.exit(1)

    # Load existing snapshot if any (idempotent — don't re-enrich)
    existing = load_snapshot(cohort_name, date) or {"cohort": cohort_name, "date": date, "companies": {}}

    # Normalize incoming companies
    for c in new_companies:
        key = c.get("ticker") or c.get("name")
        if key not in existing["companies"]:
            existing["companies"][key] = {
                "name": c.get("name"),
                "ticker": c.get("ticker"),
                "sector": c.get("sector"),
                "region": c.get("region"),
                "country": c.get("country"),
                "enriched": False,
                "variables": {}
            }

    path = save_snapshot(cohort_name, date, existing)

    # Update state membership list
    state["cohorts"][cohort_name]["companies"] = [
        {"name": v["name"], "ticker": v.get("ticker"), "enriched": v.get("enriched", False)}
        for v in existing["companies"].values()
    ]
    if date not in state["cohorts"][cohort_name]["snapshots"]:
        state["cohorts"][cohort_name]["snapshots"].append(date)
    state["cohorts"][cohort_name]["last_run"] = datetime.now().strftime("%Y-%m-%d")
    save_state(state)

    enriched_count = sum(1 for c in existing["companies"].values() if c.get("enriched"))
    pending_count = len(existing["companies"]) - enriched_count
    print(f"✓ Snapshot saved: {path}")
    print(f"  {cohort_name} / {date}: {len(existing['companies'])} companies | {enriched_count} enriched | {pending_count} pending")


# ─── Add companies ────────────────────────────────────────────────────────────

def cmd_add(cohort_name: str, companies_json: str):
    state = load_state()
    if not state:
        print("No state file. Run --setup first.")
        sys.exit(1)

    try:
        new_companies = json.loads(companies_json)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)

    existing_names = {c["name"] for c in state["cohorts"][cohort_name]["companies"]}
    added = []
    for c in new_companies:
        if c["name"] not in existing_names:
            state["cohorts"][cohort_name]["companies"].append(
                {"name": c["name"], "ticker": c.get("ticker"), "enriched": False}
            )
            added.append(c["name"])

    save_state(state)
    print(f"✓ Added to {cohort_name}: {', '.join(added) if added else 'none (all already present)'}")
    total = len(state["cohorts"][cohort_name]["companies"])
    print(f"  Cohort now has {total} companies")


# ─── Remove companies ─────────────────────────────────────────────────────────

def cmd_remove(cohort_name: str, names_json: str):
    state = load_state()
    if not state:
        print("No state file. Run --setup first.")
        sys.exit(1)

    try:
        names_to_remove = set(json.loads(names_json))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)

    before = len(state["cohorts"][cohort_name]["companies"])
    state["cohorts"][cohort_name]["companies"] = [
        c for c in state["cohorts"][cohort_name]["companies"]
        if c["name"] not in names_to_remove
    ]
    after = len(state["cohorts"][cohort_name]["companies"])
    save_state(state)
    print(f"✓ Removed {before - after} companies from {cohort_name}")
    print(f"  Cohort now has {after} companies")
    print(f"  Note: Historical snapshots are not modified — they reflect membership at time of capture.")


# ─── Delta ────────────────────────────────────────────────────────────────────

def cmd_delta(cohort_name: str, from_date: str, to_date: str):
    snap_from = load_snapshot(cohort_name, from_date)
    snap_to = load_snapshot(cohort_name, to_date)

    if not snap_from:
        print(f"No snapshot found: {cohort_name}/{from_date}")
        sys.exit(1)
    if not snap_to:
        print(f"No snapshot found: {cohort_name}/{to_date}")
        sys.exit(1)

    companies_from = snap_from.get("companies", {})
    companies_to = snap_to.get("companies", {})

    keys_from = set(companies_from.keys())
    keys_to = set(companies_to.keys())

    new_entrants = keys_to - keys_from
    exits = keys_from - keys_to
    retained = keys_from & keys_to

    print(f"\nDelta: {cohort_name}  {from_date} → {to_date}")
    print(f"{'─'*50}")

    if new_entrants:
        print(f"\n➕ New entrants ({len(new_entrants)}): {', '.join(sorted(new_entrants))}")
    if exits:
        print(f"\n➖ Exits ({len(exits)}): {', '.join(sorted(exits))}")

    if retained:
        print(f"\n📊 Variable changes (retained companies: {len(retained)})")
        numeric_vars = [
            "revenue_usd", "gross_margin_pct", "operating_margin_pct",
            "net_margin_pct", "debt_ratio", "ev_revenue_multiple",
            "capital_efficiency_score", "jurisdiction_risk_score",
            "pricing_power_score"
        ]
        movers = []
        for key in sorted(retained):
            c_from = companies_from[key].get("variables", {})
            c_to = companies_to[key].get("variables", {})
            changes = []
            for var in numeric_vars:
                v1 = c_from.get(var)
                v2 = c_to.get(var)
                if v1 is not None and v2 is not None and v1 != 0:
                    pct_change = (v2 - v1) / abs(v1) * 100
                    if abs(pct_change) >= 5:
                        changes.append(f"{var}: {v1:.2f}→{v2:.2f} ({pct_change:+.1f}%)")
            if changes:
                movers.append((key, changes))

        if movers:
            for company, changes in movers:
                print(f"\n  {company}:")
                for ch in changes:
                    print(f"    {ch}")
        else:
            print("  No significant changes (>5%) detected in retained companies.")

    print(f"\n{'─'*50}")
    print(f"Summary: {len(new_entrants)} in | {len(exits)} out | {len(retained)} retained\n")


# ─── Update state ─────────────────────────────────────────────────────────────

def cmd_update_state():
    """Recompute enriched/pending counts from snapshot files and write to state."""
    state = load_state()
    if not state:
        print("No state file. Run --setup first.")
        sys.exit(1)

    for cohort_name, meta in state["cohorts"].items():
        snapshots = meta.get("snapshots", [])
        if not snapshots:
            continue
        latest = sorted(snapshots)[-1]
        snap = load_snapshot(cohort_name, latest)
        if not snap:
            continue
        companies = snap.get("companies", {})
        state["cohorts"][cohort_name]["companies"] = [
            {"name": v["name"], "ticker": v.get("ticker"), "enriched": v.get("enriched", False)}
            for v in companies.values()
        ]

    save_state(state)
    print(f"✓ State updated from snapshot files: {STATE_FILE}")
    cmd_status()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Nazca Cohort Manager")
    parser.add_argument("--setup", action="store_true", help="Initialize cohorts dir and state file")
    parser.add_argument("--cohort", help="Cohort name (e.g. LATAM_IPO)")
    parser.add_argument("--action", choices=["status", "snapshot", "add", "remove", "delta", "update-state"],
                        help="Action to perform")
    parser.add_argument("--companies", help="JSON array of company objects")
    parser.add_argument("--names", help="JSON array of company names (for --action remove)")
    parser.add_argument("--date", help="Snapshot date YYYY-MM (default: current month)")
    parser.add_argument("--from", dest="from_date", help="Start date for delta (YYYY-MM)")
    parser.add_argument("--to", dest="to_date", help="End date for delta (YYYY-MM)")
    args = parser.parse_args()

    if args.setup:
        cmd_setup()
        return

    action = args.action
    if not action:
        parser.print_help()
        return

    if action == "status":
        cmd_status(args.cohort)
    elif action == "snapshot":
        if not args.cohort or not args.companies:
            print("--action snapshot requires --cohort and --companies")
            sys.exit(1)
        cmd_snapshot(args.cohort, args.companies, args.date)
    elif action == "add":
        if not args.cohort or not args.companies:
            print("--action add requires --cohort and --companies")
            sys.exit(1)
        cmd_add(args.cohort, args.companies)
    elif action == "remove":
        if not args.cohort or not args.names:
            print("--action remove requires --cohort and --names")
            sys.exit(1)
        cmd_remove(args.cohort, args.names)
    elif action == "delta":
        if not args.cohort or not args.from_date or not args.to_date:
            print("--action delta requires --cohort, --from, and --to")
            sys.exit(1)
        cmd_delta(args.cohort, args.from_date, args.to_date)
    elif action == "update-state":
        cmd_update_state()


if __name__ == "__main__":
    main()
