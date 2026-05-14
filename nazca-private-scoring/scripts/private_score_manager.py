#!/usr/bin/env python3
"""
private_score_manager.py — Nazca Private Company Scorer

Ingest-first pipeline: load a company batch from any source (CSV, JSON, or a
Harmonic MCP export written to file), create a dated snapshot, identify gaps
by source, then enrich only what is missing.

Usage:
  python3 private_score_manager.py --setup
  python3 private_score_manager.py --action status [--company NAME]
  python3 private_score_manager.py --action ingest --file PATH [--source FORMAT] [--cohort NAME] [--date YYYY-MM]
  python3 private_score_manager.py --action gaps [--company NAME]
  python3 private_score_manager.py --action snapshot --cohort NAME [--date YYYY-MM]
  python3 private_score_manager.py --action delta --cohort NAME --from YYYY-MM --to YYYY-MM
  python3 private_score_manager.py --action record --company NAME --data '{...}'
  python3 private_score_manager.py --action score --company NAME
  python3 private_score_manager.py --action export --company NAME
  python3 private_score_manager.py --action update-state
"""

import argparse
import csv
import io
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
SNAPSHOTS_DIR = SCORING_DIR / "snapshots"

# Field mappings live next to this script → ../../data/field_mappings.json
SKILL_DIR = Path(__file__).parent.parent
FIELD_MAPPINGS_FILE = SKILL_DIR / "data" / "field_mappings.json"

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

STAGE_MULTIPLIER = {
    "Pre-Seed": 0.4, "Seed": 0.6, "Series A": 0.8, "Series B": 0.95,
    "Series C": 1.0, "Series D": 1.05, "Series E": 1.1,
    "Series F": 1.15, "Series G+": 1.2, "Pre-IPO": 1.25,
    "_default": 0.8,
}

TIME_TO_LIQUIDITY = {
    "Pre-IPO": -18, "Series G+": -30, "Series G": -30,
    "Series F": -36, "Series E": -48, "Series D": -60,
    "Series C": -84, "Series B": -108, "Series A": -132,
    "Seed": -156, "Pre-Seed": -180,
    "_default": -84,
}

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
    "proxy_revenue_usd", "proxy_fwd_12m_usd", "capital_efficiency",
    "fundamental_value_usd",
    "funding_raised_usd", "last_round_usd", "last_round_date", "stage",
    "headcount", "hc_growth_90d_pct", "hc_growth_180d_pct",
    "hc_growth_365d_pct", "linkedin_followers",
    "year_founded", "age_years", "funding_recency_mo", "time_to_liquidity_mo",
    "sector_cagr", "sector_growth_edgar", "sector_phase_2025",
    "sector_market_liquidity", "vs_public_sector_p50", "vs_cohort",
    "tier1_investor", "big_tech_experience", "latam_unicorn_experience",
    "top_vc_experience", "public_co_experience",
    "reputation_summary", "legal_flag", "leadership_pedigree",
]

# Source group for each variable — used by --action gaps
VARIABLE_SOURCES = {
    "harmonic": [
        "headcount", "hc_growth_90d_pct", "hc_growth_180d_pct",
        "hc_growth_365d_pct", "linkedin_followers",
        "big_tech_experience", "latam_unicorn_experience",
        "top_vc_experience", "public_co_experience", "leadership_pedigree",
    ],
    "edgar": [
        "sector_growth_edgar", "sector_market_liquidity",
    ],
    "web_search": [
        "reputation_summary", "legal_flag",
    ],
    "ingest": [
        "funding_raised_usd", "last_round_usd", "last_round_date",
        "stage", "year_founded", "tier1_investor", "sector_phase_2025",
    ],
    "computed": [
        "proxy_revenue_usd", "proxy_fwd_12m_usd", "capital_efficiency",
        "fundamental_value_usd", "age_years", "funding_recency_mo",
        "time_to_liquidity_mo", "sector_cagr", "vs_public_sector_p50",
        "vs_cohort",
    ],
}

# ─── Default state ────────────────────────────────────────────────────────────

DEFAULT_STATE = {
    "version": "1.1",
    "last_updated": None,
    "pipeline": {},
    "harmonic_calls_today": 0,
    "harmonic_calls_date": None,
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def ensure_dirs():
    for d in [SCORING_DIR, INPUTS_DIR, SCORES_DIR, SNAPSHOTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def load_state() -> dict:
    if not STATE_FILE.exists():
        return dict(DEFAULT_STATE)
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state: dict):
    state["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def company_slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("/", "-")

def company_file(name: str) -> Path:
    return SCORES_DIR / f"{company_slug(name)}.json"

def snapshot_file(cohort: str, date: str) -> Path:
    slug = cohort.lower().replace(" ", "_")
    return SNAPSHOTS_DIR / f"{slug}_{date}.json"

def load_company(name: str) -> dict:
    f = company_file(name)
    return json.load(open(f)) if f.exists() else {}

def save_company(name: str, data: dict):
    data["_last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(company_file(name), "w") as f:
        json.dump(data, f, indent=2)

def completeness(variables: dict) -> tuple[int, int]:
    filled = sum(1 for k in ALL_VARIABLES if variables.get(k) is not None)
    return filled, len(ALL_VARIABLES)

def load_field_mappings() -> dict:
    if not FIELD_MAPPINGS_FILE.exists():
        return {}
    with open(FIELD_MAPPINGS_FILE) as f:
        return json.load(f)

def track_harmonic_calls(state: dict, count: int):
    today = datetime.now().strftime("%Y-%m-%d")
    if state.get("harmonic_calls_date") != today:
        state["harmonic_calls_today"] = 0
        state["harmonic_calls_date"] = today
    state["harmonic_calls_today"] = state.get("harmonic_calls_today", 0) + count

# ─── Derived metric computation ───────────────────────────────────────────────

def compute_derived(v: dict, sector: str, stage: str) -> dict:
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
            yr, mo = map(int, str(last_round_date)[:7].split("-"))
            months_ago = (2026 - yr) * 12 + (5 - mo)
            v["funding_recency_mo"] = -abs(months_ago)
        except Exception:
            pass

    v["sector_cagr"] = cagr
    v["time_to_liquidity_mo"] = ttl
    return v

# ─── Field mapper ─────────────────────────────────────────────────────────────

def map_row(row: dict, mappings: dict, source: str) -> dict:
    """Map a raw row dict to internal schema using field_mappings.json."""
    source_map = mappings.get(source, {})
    if not source_map:
        # Auto-detect: try all sources, return first match with a name
        for src_name, src_map in mappings.items():
            if src_name.startswith("_"):
                continue
            mapped = _apply_map(row, src_map)
            if mapped.get("name"):
                return mapped
        # Fallback: assume keys already match schema
        return {k: v for k, v in row.items() if k in ALL_VARIABLES or k in ("name", "sector", "region", "country", "stage")}
    return _apply_map(row, source_map)

def _apply_map(row: dict, src_map: dict) -> dict:
    result = {}
    norm_row = {k.strip(): v for k, v in row.items()}
    norm_map = {k.strip().lower(): v for k, v in src_map.items()}
    schema_keys = set(ALL_VARIABLES) | {"name", "sector", "region", "country", "stage", "cohort"}
    for raw_key, raw_val in norm_row.items():
        if raw_val in (None, "", "N/A", "n/a", "-"):
            continue
        schema_key = norm_map.get(raw_key.strip().lower())
        # Passthrough: key already matches a schema variable name
        if not schema_key and raw_key.strip() in schema_keys:
            schema_key = raw_key.strip()
        if schema_key:
            result[schema_key] = _coerce(schema_key, raw_val)
    return result

def _coerce(key: str, val):
    """Best-effort type coercion."""
    if val is None:
        return None
    int_keys = {"headcount", "linkedin_followers", "year_founded"}
    float_keys = {
        "funding_raised_usd", "last_round_usd", "hc_growth_90d_pct",
        "hc_growth_180d_pct", "hc_growth_365d_pct", "capital_efficiency",
    }
    bool_keys = {
        "tier1_investor", "big_tech_experience", "latam_unicorn_experience",
        "top_vc_experience", "public_co_experience", "legal_flag",
    }
    if key in int_keys:
        try:
            return int(str(val).replace(",", "").split(".")[0])
        except Exception:
            return val
    if key in float_keys:
        try:
            return float(str(val).replace(",", "").replace("%", ""))
        except Exception:
            return val
    if key in bool_keys:
        if isinstance(val, bool):
            return val
        return str(val).lower() in ("true", "yes", "1", "sí", "si")
    return val

# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_setup():
    ensure_dirs()

    if not STATE_FILE.exists():
        save_state(dict(DEFAULT_STATE))
        print(f"✓ Created state file: {STATE_FILE}")
    else:
        print(f"  State file already exists: {STATE_FILE}")

    placeholder = INPUTS_DIR / "company_inputs.json"
    if not placeholder.exists():
        template = {
            "_instructions": (
                "Preferred ingest method: export CSV from Harmonic/Pitchbook/Crunchbase "
                "and run --action ingest --file export.csv --source harmonic_csv. "
                "Or use --action ingest --file harmonic_response.json --source harmonic_mcp "
                "after writing a Harmonic list MCP response to file. "
                "This file is an alternative for manual one-off additions."
            ),
            "_template_version": "1.1",
            "companies": []
        }
        with open(placeholder, "w") as f:
            json.dump(template, f, indent=2)
        print(f"✓ Created inputs template: {placeholder}")

    rpe_file = INPUTS_DIR / "rpe_overrides.json"
    if not rpe_file.exists():
        with open(rpe_file, "w") as f:
            json.dump({
                "_instructions": "Override RPE per sector. Leave empty to use built-in v3.2 constants.",
                "overrides": {}
            }, f, indent=2)
        print(f"✓ Created RPE overrides template: {rpe_file}")

    print(f"\nSetup complete.")
    print(f"  State     : {STATE_FILE}")
    print(f"  Snapshots : {SNAPSHOTS_DIR}/")
    print(f"  Scores    : {SCORES_DIR}/")
    print(f"\nNext: ingest a company list:")
    print(f"  python3 private_score_manager.py --action ingest --file companies.csv --source harmonic_csv --cohort my_cohort")


def cmd_status(args):
    state = load_state()
    pipeline = state.get("pipeline", {})

    today = datetime.now().strftime("%Y-%m-%d")
    harmonic_used = state.get("harmonic_calls_today", 0) if state.get("harmonic_calls_date") == today else 0
    harmonic_remaining = max(0, 10 - harmonic_used)

    print()
    print("=" * 64)
    print(f"NAZCA PRIVATE SCORING PIPELINE  ({today})")
    print(f"Harmonic: {harmonic_used}/10 calls used today · {harmonic_remaining} remaining")
    print("=" * 64)

    if not pipeline:
        print("\n  Pipeline is empty. Run --action ingest to load a company batch.")
        print("=" * 64)
        return

    target = args.company
    companies = {target: pipeline[target]} if target and target in pipeline else pipeline

    total = len(pipeline)
    scored = sum(1 for d in pipeline.values() if d.get("status") == "scored")
    pending = total - scored

    print(f"\n  {total} companies · {scored} scored · {pending} pending\n")

    for name, meta in companies.items():
        icon = "✓" if meta.get("status") == "scored" else "⏳"
        filled = meta.get("variables_filled", 0)
        n_vars = len(ALL_VARIABLES)
        pct = int(filled / n_vars * 100)
        cohort_tag = f" [{meta['cohort']}]" if meta.get("cohort") else ""
        print(f"  {icon} {name}{cohort_tag}")
        print(f"     {meta.get('sector','?')} · {meta.get('stage','?')} · {meta.get('region','?')}")
        print(f"     {filled}/{n_vars} variables ({pct}%)")
        if meta.get("score_date"):
            print(f"     Scored: {meta['score_date']}")
        print()

    print("=" * 64)
    if pending:
        print(f"\n⚡ {pending} pending. Run --action gaps for enrichment plan.")
    print()


def cmd_ingest(args):
    """
    Load a company batch from a CSV or JSON file and record variables.
    Auto-detects format from file extension; use --source to force a mapping.
    Creates a dated snapshot after ingesting.
    """
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    mappings = load_field_mappings()
    source = args.source or ("harmonic_csv" if path.suffix.lower() == ".csv" else "auto")
    cohort = args.cohort or "pipeline"
    date = args.date or datetime.now().strftime("%Y-%m")

    # Parse file
    rows = []
    if path.suffix.lower() == ".csv":
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    else:
        with open(path) as f:
            raw = json.load(f)
        if isinstance(raw, list):
            rows = raw
        elif isinstance(raw, dict) and "companies" in raw:
            rows = raw["companies"] if isinstance(raw["companies"], list) else list(raw["companies"].values())
        elif isinstance(raw, dict):
            rows = list(raw.values())

    if not rows:
        print("Error: no rows found in file.")
        sys.exit(1)

    state = load_state()
    pipeline = state.setdefault("pipeline", {})

    added, updated, skipped = [], [], []

    for row in rows:
        mapped = map_row(row if isinstance(row, dict) else {}, mappings, source)
        name = mapped.pop("name", None) or mapped.pop("company", None)
        if not name:
            skipped.append(str(row)[:60])
            continue

        name = str(name).strip()
        sector = mapped.get("sector", "")
        stage = mapped.get("stage", "")
        region = mapped.get("region", "")
        country = mapped.get("country", "")

        if name not in pipeline:
            pipeline[name] = {
                "sector": sector, "stage": stage,
                "region": region, "country": country,
                "cohort": cohort,
                "status": "pending", "variables_filled": 0,
                "added_date": datetime.now().strftime("%Y-%m-%d"),
                "score_date": None,
            }
            added.append(name)
        else:
            # Update meta fields if provided
            for f in ("sector", "stage", "region", "country"):
                if mapped.get(f):
                    pipeline[name][f] = mapped[f]
            if not pipeline[name].get("cohort"):
                pipeline[name]["cohort"] = cohort
            updated.append(name)

        # Record variable data
        company_data = load_company(name)
        company_data.setdefault("variables", {})
        company_data["variables"].update({k: v for k, v in mapped.items() if k in ALL_VARIABLES})

        # Compute derived metrics
        s = pipeline[name].get("sector", "")
        st = pipeline[name].get("stage", "")
        company_data["variables"] = compute_derived(company_data["variables"], s, st)

        filled, _ = completeness(company_data["variables"])
        pipeline[name]["variables_filled"] = filled
        save_company(name, company_data)

    save_state(state)

    # Print summary
    print(f"\n✓ Ingest complete ({path.name}, source={source})")
    print(f"  Added   : {len(added)}")
    print(f"  Updated : {len(updated)}")
    print(f"  Skipped : {len(skipped)} (no name field)")
    print()

    # Show per-company fill summary
    all_names = added + updated
    for name in all_names[:20]:  # cap display at 20
        data = load_company(name)
        filled, total = completeness(data.get("variables", {}))
        print(f"  {name}: {filled}/{total} variables filled")
    if len(all_names) > 20:
        print(f"  ... and {len(all_names)-20} more")

    # Auto-create snapshot
    print()
    snap_args = argparse.Namespace(cohort=cohort, date=date)
    cmd_snapshot(snap_args, silent=False)


def cmd_gaps(args):
    """Show per-company null variables grouped by enrichment source."""
    state = load_state()
    pipeline = state.get("pipeline", {})

    if not pipeline:
        print("Pipeline is empty.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    harmonic_used = state.get("harmonic_calls_today", 0) if state.get("harmonic_calls_date") == today else 0
    harmonic_remaining = max(0, 10 - harmonic_used)

    target = args.company
    companies = {target: pipeline[target]} if target and target in pipeline else pipeline

    harmonic_needed = 0

    print()
    print("=" * 64)
    print(f"NAZCA SCORING — GAP ANALYSIS  ({today})")
    print("=" * 64)

    for name, meta in companies.items():
        data = load_company(name)
        v = data.get("variables", {})

        nulls_by_source = {s: [] for s in VARIABLE_SOURCES}
        filled = []

        for var in ALL_VARIABLES:
            val = v.get(var)
            if val is not None:
                filled.append(var)
                continue
            for src, src_vars in VARIABLE_SOURCES.items():
                if var in src_vars:
                    nulls_by_source[src].append(var)
                    break

        total = len(ALL_VARIABLES)
        pct = int(len(filled) / total * 100)
        print(f"\n  {name}  ({meta.get('sector','?')} · {meta.get('stage','?')} · {meta.get('region','?')})")
        print(f"  {'─'*58}")
        print(f"  ✓ Filled  {len(filled)}/{total} ({pct}%)")

        if nulls_by_source["harmonic"]:
            n = len(nulls_by_source["harmonic"])
            calls = 2  # 1 get_companies + 1 get_people
            harmonic_needed += calls
            print(f"  ✗ Harmonic    ({calls} calls needed)")
            print(f"      {', '.join(nulls_by_source['harmonic'])}")

        if nulls_by_source["edgar"]:
            print(f"  ✗ EDGAR       (no daily limit)")
            print(f"      {', '.join(nulls_by_source['edgar'])}")

        if nulls_by_source["web_search"]:
            print(f"  ✗ Web search  (no daily limit)")
            print(f"      {', '.join(nulls_by_source['web_search'])}")

        if nulls_by_source["ingest"]:
            print(f"  ✗ Missing from ingest  (re-ingest with richer export)")
            print(f"      {', '.join(nulls_by_source['ingest'])}")

        if nulls_by_source["computed"]:
            print(f"  ⟳ Auto-computed  (will fill when dependencies are recorded)")
            print(f"      {', '.join(nulls_by_source['computed'])}")

    # Budget summary
    print()
    print("=" * 64)
    print(f"  Harmonic budget: {harmonic_remaining}/10 calls remaining today")
    companies_to_enrich = harmonic_needed // 2
    if harmonic_needed > 0:
        if harmonic_remaining >= harmonic_needed:
            print(f"  Budget OK: can enrich all {companies_to_enrich} pending companies today")
            print(f"  Action: call get_companies + get_people for each, then --action record")
        else:
            can_do = harmonic_remaining // 2
            cant_do = companies_to_enrich - can_do
            print(f"  Budget WARNING: only {can_do}/{companies_to_enrich} companies fit today's Harmonic budget")
            print(f"  {cant_do} companies → fall back to EDGAR + web search for remaining nulls")
    else:
        print(f"  No Harmonic calls needed — enrich via EDGAR + web search only")
    print()


def cmd_snapshot(args, silent=False):
    """Create a dated snapshot of all pipeline companies (or a named cohort)."""
    state = load_state()
    pipeline = state.get("pipeline", {})
    cohort = args.cohort
    date = args.date if hasattr(args, "date") and args.date else datetime.now().strftime("%Y-%m")

    # Filter by cohort if specified and not "pipeline"
    if cohort and cohort != "pipeline":
        members = {n: m for n, m in pipeline.items() if m.get("cohort") == cohort}
    else:
        members = pipeline

    if not members:
        if not silent:
            print(f"No companies found for cohort '{cohort}'.")
        return

    snap = {
        "cohort": cohort,
        "date": date,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "company_count": len(members),
        "companies": {},
    }

    for name in members:
        data = load_company(name)
        snap["companies"][name] = {
            "meta": pipeline.get(name, {}),
            "variables": data.get("variables", {}),
        }

    out = snapshot_file(cohort, date)
    with open(out, "w") as f:
        json.dump(snap, f, indent=2)

    if not silent:
        print(f"✓ Snapshot created: {out}")
        print(f"  Cohort: {cohort} · Date: {date} · Companies: {len(members)}")

    # Track snapshot in state
    state.setdefault("snapshots", [])
    entry = {"cohort": cohort, "date": date, "file": str(out), "count": len(members)}
    existing = [s for s in state["snapshots"] if not (s["cohort"] == cohort and s["date"] == date)]
    state["snapshots"] = existing + [entry]
    save_state(state)


def cmd_delta(args):
    """Compare two snapshots for the same cohort and show per-company variable changes."""
    cohort = args.cohort
    date_from = getattr(args, "from_date", None) or getattr(args, "from", None)
    date_to = args.to

    f1 = snapshot_file(cohort, date_from)
    f2 = snapshot_file(cohort, date_to)

    for f, label in [(f1, date_from), (f2, date_to)]:
        if not f.exists():
            print(f"Error: snapshot not found for cohort='{cohort}' date='{label}'")
            print(f"  Expected: {f}")
            print(f"  Run: --action snapshot --cohort {cohort} --date {label}")
            sys.exit(1)

    with open(f1) as f:
        snap1 = json.load(f)
    with open(f2) as f:
        snap2 = json.load(f)

    cos1 = set(snap1["companies"])
    cos2 = set(snap2["companies"])
    new_entrants = cos2 - cos1
    exits = cos1 - cos2
    common = cos1 & cos2

    print()
    print("=" * 64)
    print(f"COHORT DELTA — {cohort.upper()}")
    print(f"  {date_from}  →  {date_to}")
    print("=" * 64)

    if new_entrants:
        print(f"\n  New entrants ({len(new_entrants)}): {', '.join(sorted(new_entrants))}")
    if exits:
        print(f"  Exits ({len(exits)}): {', '.join(sorted(exits))}")

    numeric_vars = [
        "proxy_revenue_usd", "proxy_fwd_12m_usd", "fundamental_value_usd",
        "capital_efficiency", "headcount", "hc_growth_90d_pct",
        "hc_growth_180d_pct", "hc_growth_365d_pct", "linkedin_followers",
        "funding_recency_mo",
    ]

    print(f"\n  {'Company':<22} {'Variable':<28} {date_from:>10} {date_to:>10} {'Δ':>10}")
    print(f"  {'─'*22} {'─'*28} {'─'*10} {'─'*10} {'─'*10}")

    for name in sorted(common):
        v1 = snap1["companies"][name].get("variables", {})
        v2 = snap2["companies"][name].get("variables", {})
        printed_name = False
        for var in numeric_vars:
            a = v1.get(var)
            b = v2.get(var)
            if a is None and b is None:
                continue
            if a == b:
                continue
            label = name if not printed_name else ""
            printed_name = True
            a_str = f"{a:,.0f}" if isinstance(a, (int, float)) else str(a or "—")
            b_str = f"{b:,.0f}" if isinstance(b, (int, float)) else str(b or "—")
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                pct = ((b - a) / abs(a) * 100) if a else 0
                delta_str = f"{pct:+.1f}%"
            else:
                delta_str = "changed"
            print(f"  {label:<22} {var:<28} {a_str:>10} {b_str:>10} {delta_str:>10}")

    print()


def cmd_record(args):
    name = args.company
    try:
        new_data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: --data must be valid JSON. {e}")
        sys.exit(1)

    state = load_state()
    if name not in state.get("pipeline", {}):
        print(f"Error: '{name}' not in pipeline. Run --action ingest first.")
        sys.exit(1)

    company_data = load_company(name)
    company_data.setdefault("variables", {})
    company_data["variables"].update(new_data)

    meta = state["pipeline"][name]
    sector = new_data.get("sector") or meta.get("sector", "")
    stage = new_data.get("stage") or meta.get("stage", "")
    company_data["variables"] = compute_derived(company_data["variables"], sector, stage)

    filled, total = completeness(company_data["variables"])
    meta["variables_filled"] = filled

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
        print(f"Error: No variables for '{name}'. Run --action ingest or --action record first.")
        sys.exit(1)

    meta = state["pipeline"][name]
    v = compute_derived(v, meta.get("sector", ""), meta.get("stage", ""))

    score_summary = {
        "company": name,
        "score_date": datetime.now().strftime("%Y-%m-%d"),
        "sector": meta.get("sector", ""),
        "stage": meta.get("stage", ""),
        "region": meta.get("region", ""),
        "key_metrics": {k: v.get(k) for k in [
            "proxy_revenue_usd", "proxy_fwd_12m_usd", "capital_efficiency",
            "fundamental_value_usd", "headcount", "hc_growth_90d_pct",
            "hc_growth_180d_pct", "hc_growth_365d_pct", "age_years",
            "funding_recency_mo", "time_to_liquidity_mo", "sector_cagr",
            "tier1_investor", "big_tech_experience", "latam_unicorn_experience",
            "top_vc_experience", "public_co_experience", "legal_flag",
        ]},
        "qualitative": {k: v.get(k) for k in [
            "reputation_summary", "leadership_pedigree", "sector_market_liquidity",
        ]},
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
    data = load_company(args.company)
    if not data:
        print(f"Error: No data found for '{args.company}'.")
        sys.exit(1)
    print(json.dumps(data, indent=2))


def cmd_update_state():
    state = load_state()
    pipeline = state.get("pipeline", {})
    n = 0
    for name, meta in pipeline.items():
        data = load_company(name)
        if data:
            filled, _ = completeness(data.get("variables", {}))
            meta["variables_filled"] = filled
            if data.get("score_summary"):
                meta["status"] = "scored"
                meta["score_date"] = data["score_summary"].get("score_date")
            n += 1
    save_state(state)
    print(f"✓ Updated state for {n} companies.")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Nazca Private Company Scorer v1.1")
    p.add_argument("--setup", action="store_true")
    p.add_argument("--action", choices=[
        "status", "ingest", "gaps", "snapshot", "delta",
        "record", "score", "export", "update-state",
    ])
    p.add_argument("--company")
    p.add_argument("--companies")
    p.add_argument("--cohort", default="pipeline")
    p.add_argument("--file")
    p.add_argument("--source", help="Field mapping source: harmonic_csv|harmonic_mcp|pitchbook|crunchbase|nazca_internal|auto")
    p.add_argument("--date", help="Snapshot date YYYY-MM")
    p.add_argument("--from", dest="from_date", help="Delta: from date YYYY-MM")
    p.add_argument("--to", help="Delta: to date YYYY-MM")
    p.add_argument("--data", help="JSON object of variable values")
    args = p.parse_args()

    if args.setup:
        cmd_setup()
    elif args.action == "status":
        cmd_status(args)
    elif args.action == "ingest":
        if not args.file:
            print("--action ingest requires --file PATH")
            sys.exit(1)
        cmd_ingest(args)
    elif args.action == "gaps":
        cmd_gaps(args)
    elif args.action == "snapshot":
        cmd_snapshot(args)
    elif args.action == "delta":
        if not args.from_date or not args.to:
            print("--action delta requires --from YYYY-MM --to YYYY-MM")
            sys.exit(1)
        cmd_delta(args)
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
