# nazca-cohort-enrichment

**Owner:** @dan — Nazca Investment Team  
**Status:** v1.0 · Production  
**Last eval:** 2026-05-11 · 100% pass rate (15/15 assertions)

---

## What this skill does

Manages Nazca's investment data enrichment pipeline across Claude sessions.

The core problem it solves: without this skill, every new session starts from scratch —
Claude doesn't know what cohorts exist, what's been enriched, what's pending, or which
data source to use for which company type. With the skill, every session begins by reading
live state and surfaces exactly what needs action next.

**Three things this skill makes reliable:**

1. **Session continuity** — reads the master state file at session start, surfaces pending
   companies, dead sources, and the recommended next action
2. **Source routing** — knows that public companies → EDGAR (no daily limit), private
   companies → Harmonic (10-call/day limit), and never wastes calls on the wrong source
3. **Cohort time series** — adds, removes, and snapshots companies without losing history.
   A delta between two snapshots shows exactly what changed per company, per variable

---

## File structure

```
nazca-cohort-enrichment/
├── SKILL.md                          ← Skill instructions loaded into every session
├── scripts/
│   └── cohort_manager.py             ← CLI for state + snapshot management
├── references/
│   └── variable_registry.md          ← Full source priority, confidence rules, edge cases
└── evals/
    ├── evals.json                    ← Test cases + benchmark results
    └── iteration-1/
        └── RESULTS.md                ← Qualitative eval outputs, with vs. without skill
```

---

## Quick start

### First-time setup (creates state file + variable registry)
```bash
python3 scripts/cohort_manager.py --setup
```

### Every session start
```bash
# The skill does this automatically — reads state and surfaces what's pending
cat /Users/dannazca/Factory/cohorts/nazca_enrichment_state.json
python3 scripts/cohort_manager.py --action status
```

### Add companies to a cohort
```bash
python3 scripts/cohort_manager.py \
  --cohort LATAM_IPO \
  --action add \
  --companies '[{"name":"Neon","sector":"FinTech","region":"LatAm","country":"Brazil"}]'
```

### Create a dated snapshot (for time-series tracking)
```bash
python3 scripts/cohort_manager.py \
  --cohort LATAM_IPO \
  --action snapshot \
  --companies '[...]' \
  --date 2026-05
```

### Compare two snapshots (delta)
```bash
python3 scripts/cohort_manager.py \
  --cohort LATAM_IPO --action delta \
  --from 2026-05 --to 2026-11
```

### Remove companies (membership changes don't modify historical snapshots)
```bash
python3 scripts/cohort_manager.py \
  --cohort LATAM_IPO --action remove \
  --names '["Frubana","Justo"]'
```

---

## Cohorts

| Cohort | Description | Type |
|---|---|---|
| `LATAM_IPO` | LatAm companies approaching or post-IPO | Private + Public |
| `US_IPO` | US companies approaching or post-IPO | Public |
| `Hot_Startups` | High-momentum private startups — LatAm, US, blend | Private |
| `Publicas_GUR` | 96 public comparables for OLS calibration | Public |

---

## Source routing

| Company type | Primary source | Fallback | Notes |
|---|---|---|---|
| Public (US 10-K) | EDGAR `edgar_trends` | OLS model | No daily call limit |
| Public (LatAm 20-F) | EDGAR `edgar_trends` | OLS model | operating_income = N/A is expected |
| Public (BRL/CNY reporter) | EDGAR + auto FX divide | OLS model | Ratio 4.5–7.0 → BRL, 6.5–8.5 → CNY |
| Private (any) | Harmonic MCP | OLS model | **10-call/day limit** |

**Dead sources (never retry):**
- Financial Datasets API — $0 balance since 2026-05-07
- Brightdata — HTTP 401 since ~2026-04

---

## Variable confidence floor

Any variable with confidence < 0.75 is recorded as `N/A` — not as a score.  
`N/A` = no verifiable data. It does not penalize the company.

| Group | Variables | Confidence |
|---|---|---|
| EDGAR financials | revenue, gross_profit, margins, assets, liabilities, debt_ratio | 0.90–1.00 |
| Valuation | ev_revenue_multiple (Damodaran), revenue_cagr_2yr | 0.85–0.90 |
| Rules-based scores | jurisdiction_risk, pricing_power, sector_growth_cagr, capital_efficiency | 0.80–0.85 |
| Harmonic traction | hc_momentum_90d, linkedin_growth_180d | 0.80–0.85 |
| Harmonic web traffic | web_traffic_90d | **0.72 → always N/A** |
| OLS revenue (private) | revenue_usd (estimated) | **0.65 → always N/A** |

Full rules in [`references/variable_registry.md`](references/variable_registry.md).

---

## State files (live — not in this repo)

```
/Users/dannazca/Factory/cohorts/
  nazca_enrichment_state.json     ← master state: all cohorts, counts, last_run
  variable_registry.json          ← machine-readable source priority per variable
  LATAM_IPO_2026-05.json          ← snapshot: company list + enriched variables
  Publicas_GUR_2026-05.json       ← 96 public comparables snapshot
  ...
```

The `cohort_manager.py` script reads and writes these files. They are not versioned here
because they contain live pipeline state that changes every session.

---

## Related scripts (in `/Users/dannazca/Factory/`)

| Script | Purpose |
|---|---|
| `enrich_publicas_gur.py` | Public company enrichment manager — CLI + JSON cache |
| `build_publicas_gur_excel.py` | 5-sheet Excel builder from enrichment cache |
| `nazca_revenue_engine.py` | OLS revenue model for private companies |
| `nazca_tag_engine.py` | 25-tag behavioral scorer |
| `harmonic_timeseries_cache.py` | Harmonic traction data cache |

---

## Eval results

**Iteration 1 (2026-05-11):** With skill 100% · Without skill 33% · Delta +67pp

The key finding: without the skill, Claude correctly identified companies in Harmonic
but called the wrong operation (live Harmonic watchlist API instead of cohort_manager.py)
and had no awareness of the local state file. With the skill, all three test scenarios
(session start, add companies, cohort delta) executed correctly on the first attempt.

See [`evals/iteration-1/RESULTS.md`](evals/iteration-1/RESULTS.md) for full outputs.
