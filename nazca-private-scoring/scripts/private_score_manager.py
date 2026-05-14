#!/usr/bin/env python3
"""
private_score_manager.py — Nazca Private Company Scorer

Manages the scoring pipeline for private companies across 29 dimensions.
Reads live data from Harmonic MCP and merges with placeholder files
(Pitchbook, LAVCA, Crunchbase exports, internal Nazca Wiki).

Usage:
  python3 private_score_manager.py --setup
  python3 private_score_manager.py --action status [--company NAME]
  python3 private_score_manager.py --action add --companies '[...]'
  python3 private_score_manager.py --action record --company "Neon" --data '{...}'
  python3 private_score_manager.py --action score --company "Neon"
  python3 private_score_manager.py --action export --company "Neon"
  python3 private_score_manager.py --action update-state
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

_factory_default = Path.home() / "Factory"
FACTORY_DIR = Path(os.environ.get("NAZCA_FACTORY_DIR", str(_factory_default)))
SCORING_DIR = FACTORY_DIR / "private-scoring"
STATE_FILE = SCORING_DIR / "state.json"
INPUTS_DIR = SCORING_DIR / "inputs"
SCORES_DIR = SCORING_DIR / "scores"

# ─── Sector constants ─────────────────────────────────────────────────────────

SECTOR_CAGR = {
    "AIML": 0.45, "AI": 0.45, "Space": 0.45,
    "SaaS": 0.23, "B2BSaaS": 0.23,
    "ECommerce": 0.21, "E-Commerce": 0.21, "Marketplace": 0.21,
    "HealthTech": 0.135, "Health": 0.135,
    "FinTech": 0.09, "Fintech": 0.09,
    "CleanTech": 0.085, "Climate": 0.085,
    "Logistics": 0.024,
    "PropTech": -0.15,
}

# RPE = Revenue Per Employee (USD) — from Nazca OLS v3.2 calibration
# Override in inputs/rpe_overrides.json for custom calibration
RPE_SECTOR = {
    "AIML": 250000, "AI": 250000,
    "SaaS": 220000, "B2BSaaS": 220000,
    "FinTech": 130000, "Fintech": 130000,
    "HealthTech": 160000, "Health": 160000,
    "ECommerce": 55000, "E-Commerce": 55000, "Marketplace": 70000,
    "Logistics": 80000,
    "CleanTech": 120000, "Climate": 120000,
    "PropTech": 90000,
    "Space": 300000,
    "_default": 120000,
}

# Stage multiplier applied on top of RPE
STAGE_MULTIPLIER = {
    "Pre-Seed": 0.4, "Seed": 0.6, "Series A": 0.8, "Series B": 0.95,
    "Series C": 1.0, "Series D": 1.05, "Series E": 1.1,
    "Series F": 1.15, "Series G+": 1.2, "Pre-IPO": 1.25,
    "_default": 0.8,
}

# Time-to-liquidity in months by stage (negative = months to IPO/exit)
TIME_TO_LIQUIDITY = {
    "Pre-IPO": -18, "Series G+": -30, "Series G": -30,
    "Series F": -36, "Series E": -48, "Series D": -60,
    "Series C": -84, "Series B": -108, "Series A": -132,
    "Seed": -156, "Pre-Seed": -180,
    "_default": -84,
}

# EV/Revenue multiples by sector (Damodaran Jan 2026 + Nazca adjustments)
EV_REVENUE_MULTIPLE = {
    "AIML": 18.0, "AI": 18.0, "SaaS": 8.5, "B2BSaaS": 8.5,
    "FinTech": 5.0, "Fintech": 5.0, "ECommerce": 2.5, "E-Commerce": 2.5,
    "Marketplace": 4.0, "HealthTech": 6.0, "Health": 6.0,
    "Logistics": 2.0, "CleanTech": 4.5, "Climate": 4.5,
    "PropTech": 3.0, "Space": 10.0,
    "_default": 5.0,
}

# ─── Variable registry ────────────────────────────────────────────────────────

ALL_VARIABLES = [
    # Financial / Proxy (computed)
    "proxy_revenue_usd", "proxy_fwd_12m_usd", "capital_efficiency",
    "fundamental_value_usd",
    # Funding (placeholder — Crunchbase / Pitchbook)
    "funding_raised_usd", "last_round_usd", "last_round_date", "stage",
    # Traction (Harmonic MCP)
    "headcount", "hc_growth_90d_pct", "hc_growth_180d_pct",
    "hc_growth_365d_pct", "linkedin_followers",
    # Temporal (computed or placeholder)
    "year_founded", "age_years", "funding_recency_mo", "time_to_liquidity_mo",
    # Benchmarks (constants + EDGAR + computed)
    "sector_cagr", "sector_growth_edgar", "sector_phase_2025",
    "sector_market_liquidity", "vs_public_sector_p50", "vs_cohort",
    # Qualitative binary (Harmonic + web search)
    "tier1_investor", "big_tech_experience", "latam_unicorn_experience",
    "top_vc_experience", "public_co_experience",
    # Qualitative open (web search + Harmonic)
    "reputation_summary", "legal_flag", "leadership_pedigree",
]

HARMONIC_VARIABLES = [
    "headcount", "hc_growth_90d_pct", "hc_growth_180d_pct",
    "hc_growth_365d_pct", "linkedin_followers",
    "big_tech_experience", "latam_unicorn_experience",
    "top_vc_experience", "public_co_experience", "leadership_pedigree",
]

PLACEHOLDER_VARIABLES = [
    "funding_raised_usd", "last_round_usd", "last_round_date",
    "stage", "year_founded", "tier1_investor",
    "sector_phase_2025",  # from LAVCA + Pitchbook
]

COMPUTED_VARIABLES = [
    "proxy_revenue_usd", "proxy_fwd_12m_usd", "capital_efficiency",
    "fundamental_value_usd", "age_years", "funding_recency_mo",
    "time_to_liquidity_mo", "sector_cagr", "vs_public_sector_p50",
    "vs_cohort",
]

WEB_SEARCH_VARIABLES = [
    "reputation_summary", "legal_flag", "sector_growth_edgar",
    "sector_market_liquidity",
]

# ─── Default state ────────────────────────────────────────────────────────────

DEFAULT_STATE = {
    "version": "1.0",
    "last_updated": None,
    "pipeline": {},
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def ensure_dirs():
    SCORING_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    SCORES_DIR.mkdir(parents=True, exist_ok=True)

def load_state():
    if not STATE_FILE.exists():
        return dict(DEFAULT_STATE)
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    state["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def company_file(name: str) -> Path:
    slug = name.lower().replace(" ", "_").replace("/", "-")
    return SCORES_DIR / f"{slug}.json"

def load_company(name: str) -> dict:
    f = company_file(name)
    if not f.exists():
        return {}
    with open(f) as fh:
        return json.load(fh)

def save_company(name: str, data: dict):
    data["_last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(company_file(name), "w") as f:
        json.dump(data, f, indent=2)

def load_inputs_placeholder() -> dict:
    p = INPUTS_DIR / "company_inputs.json"
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)

def completeness(variables: dict) -> tuple[int, int]:
    filled = sum(1 for k in ALL_VARIABLES if variables.get(k) is not None)
    return filled, len(ALL_VARIABLES)

# ─── Derived metric computation ───────────────────────────────────────────────

def compute_derived(v: dict, sector: str, stage: str) -> dict:
    """Fill computed variables from raw inputs. Returns updated dict."""
    rpe = RPE_SECTOR.get(sector, RPE_SECTOR["_default"])
    stage_mult = STAGE_MULTIPLIER.get(stage, STAGE_MULTIPLIER["_default"])
    cagr = SECTOR_CAGR.get(sector, 0.10)
    ev_rev = EV_REVENUE_MULTIPLE.get(sector, EV_REVENUE_MULTIPLE["_default"])
    ttl = TIME_TO_LIQUIDITY.get(stage, TIME_TO_LIQUIDITY["_default"])

    hc = v.get("headcount")
    funding = v.get("funding_raised_usd")
    year_founded = v.get("year_founded")
    last_round_date = v.get("last_round_date")

    if hc:
        proxy = hc * rpe * stage_mult
        v["proxy_revenue_usd"] = round(proxy)
        v["proxy_fwd_12m_usd"] = round(proxy * (1 + cagr))
        v["fundamental_value_usd"] = round(proxy * ev_rev)
        if funding:
            v["capital_efficiency"] = round(proxy / funding, 3)

    if year_founded:
        v["age_years"] = 2026 - int(year_founded)

    if last_round_date:
        try:
            yr, mo = map(int, str(last_round_date).split("-"))
            months_ago = (2026 - yr) * 12 + (5 - mo)  # May 2026 = current
            v["funding_recency_mo"] = -abs(months_ago)
        except Exception:
            pass

    v["sector_cagr"] = cagr
    v["time_to_liquidity_mo"] = ttl

    return v

# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_setup():
    ensure_dirs()

    # Write state file
    if not STATE_FILE.exists():
        save_state(dict(DEFAULT_STATE))
        print(f"✓ Created state file: {STATE_FILE}")
    else:
        print(f"  State file already exists: {STATE_FILE}")

    # Write placeholder template
    placeholder = INPUTS_DIR / "company_inputs.json"
    if not placeholder.exists():
        template = {
            "_instructions": (
                "Fill this file with data from Pitchbook, LAVCA, or Crunchbase exports. "
                "One entry per company. Null = not yet available. "
                "Run private_score_manager.py --action update-state after editing."
            ),
            "_template_version": "1.0",
            "companies": {
                "ExampleCo": {
                    "funding_raised_usd": None,
                    "last_round_usd": None,
                    "last_round_date": "YYYY-MM",
                    "stage": "Series B",
                    "year_founded": None,
                    "sector": "FinTech",
                    "country": "Mexico",
                    "region": "LatAm",
                    "tier1_investor": False,
                    "tier1_investor_names": [],
                    "sector_phase_2025_lavca": None,
                    "sector_phase_2025_pitchbook": None,
                    "notes": ""
                }
            }
        }
        with open(placeholder, "w") as f:
            json.dump(template, f, indent=2)
        print(f"✓ Created placeholder template: {placeholder}")
    else:
        print(f"  Placeholder template already exists: {placeholder}")

    # Write RPE overrides template
    rpe_file = INPUTS_DIR / "rpe_overrides.json"
    if not rpe_file.exists():
        with open(rpe_file, "w") as f:
            json.dump({
                "_instructions": "Override default RPE values per sector. Leave empty to use built-in constants.",
                "overrides": {}
            }, f, indent=2)
        print(f"✓ Created RPE overrides template: {rpe_file}")

    print(f"\nSetup complete.")
    print(f"  State    : {STATE_FILE}")
    print(f"  Inputs   : {INPUTS_DIR}/")
    print(f"  Scores   : {SCORES_DIR}/")
    print(f"\nNext step: fill {INPUTS_DIR}/company_inputs.json with Pitchbook/LAVCA/Crunchbase data.")


def cmd_status(args):
    state = load_state()
    pipeline = state.get("pipeline", {})

    print()
    print("=" * 60)
    print(f"NAZCA PRIVATE SCORING PIPELINE  (as of {datetime.now().strftime('%Y-%m-%d')})")
    print("=" * 60)

    if not pipeline:
        print("\n  No companies in pipeline. Use --action add to add companies.")
        print("=" * 60)
        return

    target = args.company
    companies = {target: pipeline[target]} if target and target in pipeline else pipeline

    pending = [n for n, d in pipeline.items() if d.get("status") != "scored"]
    scored = [n for n, d in pipeline.items() if d.get("status") == "scored"]

    print(f"\n  Total: {len(pipeline)} | Scored: {len(scored)} | Pending: {len(pending)}")
    print()

    for name, meta in companies.items():
        status_icon = "✓" if meta.get("status") == "scored" else "⏳"
        filled = meta.get("variables_filled", 0)
        total = len(ALL_VARIABLES)
        pct = int(filled / total * 100) if total else 0
        print(f"  {status_icon} {name}")
        print(f"     Sector: {meta.get('sector','?')} | Stage: {meta.get('stage','?')} | Region: {meta.get('region','?')}")
        print(f"     Variables: {filled}/{total} ({pct}%) | Status: {meta.get('status','pending')}")
        if meta.get("score_date"):
            print(f"     Last scored: {meta['score_date']}")
        print()

    print("=" * 60)

    if pending:
        print(f"\n⚡ Action needed: {len(pending)} companies not yet scored.")
        print("   Priority: Harmonic → then fill placeholders → then web search")
    print()


def cmd_add(args):
    companies = json.loads(args.companies)
    state = load_state()
    pipeline = state.setdefault("pipeline", {})

    added = []
    for co in companies:
        name = co.get("name")
        if not name:
            print(f"  Skipping entry with no name: {co}")
            continue
        if name not in pipeline:
            pipeline[name] = {
                "sector": co.get("sector", ""),
                "stage": co.get("stage", ""),
                "region": co.get("region", ""),
                "country": co.get("country", ""),
                "status": "pending",
                "variables_filled": 0,
                "added_date": datetime.now().strftime("%Y-%m-%d"),
                "score_date": None,
            }
            added.append(name)
            print(f"✓ Added: {name}")
        else:
            print(f"  Already in pipeline: {name}")

    save_state(state)
    if added:
        print(f"\n  {len(added)} companies added. Run --action status to see pipeline.")


def cmd_record(args):
    name = args.company
    try:
        new_data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: --data must be valid JSON. {e}")
        sys.exit(1)

    state = load_state()
    if name not in state.get("pipeline", {}):
        print(f"Error: '{name}' not in pipeline. Add it first with --action add.")
        sys.exit(1)

    # Load existing company data
    company_data = load_company(name)
    company_data.setdefault("variables", {})

    # Merge new data
    company_data["variables"].update(new_data)

    # Get sector/stage from pipeline meta (override with incoming data if provided)
    meta = state["pipeline"][name]
    sector = new_data.get("sector") or meta.get("sector", "")
    stage = new_data.get("stage") or meta.get("stage", "")

    # Compute derived metrics
    company_data["variables"] = compute_derived(company_data["variables"], sector, stage)

    # Update pipeline meta
    filled, total = completeness(company_data["variables"])
    meta["variables_filled"] = filled
    if filled == total:
        meta["status"] = "complete"

    save_company(name, company_data)
    save_state(state)

    print(f"✓ Recorded {len(new_data)} variables for {name}")
    print(f"  Completeness: {filled}/{total} ({int(filled/total*100)}%)")


def cmd_score(args):
    name = args.company
    state = load_state()
    if name not in state.get("pipeline", {}):
        print(f"Error: '{name}' not in pipeline.")
        sys.exit(1)

    company_data = load_company(name)
    v = company_data.get("variables", {})

    if not v:
        print(f"Error: No variables recorded for {name}. Run --action record first.")
        sys.exit(1)

    meta = state["pipeline"][name]
    sector = meta.get("sector", "")
    stage = meta.get("stage", "")

    # Recompute derived metrics with latest data
    v = compute_derived(v, sector, stage)

    # Build score summary
    score_summary = {
        "company": name,
        "score_date": datetime.now().strftime("%Y-%m-%d"),
        "sector": sector,
        "stage": stage,
        "region": meta.get("region", ""),
        "key_metrics": {
            "proxy_revenue_usd": v.get("proxy_revenue_usd"),
            "proxy_fwd_12m_usd": v.get("proxy_fwd_12m_usd"),
            "capital_efficiency": v.get("capital_efficiency"),
            "fundamental_value_usd": v.get("fundamental_value_usd"),
            "headcount": v.get("headcount"),
            "hc_growth_90d_pct": v.get("hc_growth_90d_pct"),
            "hc_growth_180d_pct": v.get("hc_growth_180d_pct"),
            "hc_growth_365d_pct": v.get("hc_growth_365d_pct"),
            "age_years": v.get("age_years"),
            "funding_recency_mo": v.get("funding_recency_mo"),
            "time_to_liquidity_mo": v.get("time_to_liquidity_mo"),
            "sector_cagr": v.get("sector_cagr"),
            "tier1_investor": v.get("tier1_investor"),
            "big_tech_experience": v.get("big_tech_experience"),
            "latam_unicorn_experience": v.get("latam_unicorn_experience"),
            "top_vc_experience": v.get("top_vc_experience"),
            "public_co_experience": v.get("public_co_experience"),
            "legal_flag": v.get("legal_flag"),
        },
        "qualitative": {
            "reputation_summary": v.get("reputation_summary"),
            "leadership_pedigree": v.get("leadership_pedigree"),
            "sector_market_liquidity": v.get("sector_market_liquidity"),
        },
    }

    company_data["variables"] = v
    company_data["score_summary"] = score_summary
    save_company(name, company_data)

    meta["status"] = "scored"
    meta["score_date"] = score_summary["score_date"]
    meta["variables_filled"], _ = completeness(v)
    save_state(state)

    print(f"✓ Score snapshot saved for {name}")
    print()
    print(json.dumps(score_summary, indent=2))


def cmd_export(args):
    name = args.company
    data = load_company(name)
    if not data:
        print(f"Error: No data found for '{name}'. Has it been recorded and scored?")
        sys.exit(1)
    print(json.dumps(data, indent=2))


def cmd_update_state():
    state = load_state()
    pipeline = state.get("pipeline", {})
    updated = 0
    for name, meta in pipeline.items():
        data = load_company(name)
        if data:
            filled, _ = completeness(data.get("variables", {}))
            meta["variables_filled"] = filled
            if data.get("score_summary"):
                meta["status"] = "scored"
                meta["score_date"] = data["score_summary"].get("score_date")
            updated += 1
    save_state(state)
    print(f"✓ Updated state for {updated} companies.")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Nazca Private Company Scorer")
    p.add_argument("--setup", action="store_true")
    p.add_argument("--action", choices=["status", "add", "record", "score", "export", "update-state"])
    p.add_argument("--company", help="Company name")
    p.add_argument("--companies", help="JSON array of company objects")
    p.add_argument("--data", help="JSON object of variable values to record")
    args = p.parse_args()

    if args.setup:
        cmd_setup()
    elif args.action == "status":
        cmd_status(args)
    elif args.action == "add":
        if not args.companies:
            print("--action add requires --companies '[...]'")
            sys.exit(1)
        cmd_add(args)
    elif args.action == "record":
        if not args.company or not args.data:
            print("--action record requires --company NAME and --data '{...}'")
            sys.exit(1)
        cmd_record(args)
    elif args.action == "score":
        if not args.company:
            print("--action score requires --company NAME")
            sys.exit(1)
        cmd_score(args)
    elif args.action == "export":
        if not args.company:
            print("--action export requires --company NAME")
            sys.exit(1)
        cmd_export(args)
    elif args.action == "update-state":
        cmd_update_state()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
