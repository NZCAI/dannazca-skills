---
name: nazca-cohort-enrichment
description: "Manages Nazca's investment data enrichment pipeline: cohort tracking, variable registry, source routing, and session handoff. Always use this skill at the start of any Nazca session involving companies, watchlists, or metrics. Trigger whenever the user: mentions enriching companies or a list (even casually like 'run the enrichment' or 'update the watchlist'); references any cohort by name (LATAM_IPO, US_IPO, Hot_Startups, Publicas_GUR); asks what changed between periods or wants a delta comparison; adds or removes companies from a list; asks 'what's the state of...' or 'what's pending'; says 'session handoff' or 'starting fresh' or 'pick up where we left off'. Also trigger when the user hands you a list of company names and asks for financial metrics, risk scores, or GUR variables — even without explicitly saying 'enrich'."
---

# Nazca Cohort Enrichment

## What this skill does

Tracks enrichment state across sessions for Nazca's investment pipeline. The core
insight: **variables are permanent, companies are inputs, cohorts are named lists
that evolve over time**.

- Variables never change — their source priority is defined here once
- Companies are always passed in by the user — never hardcoded
- A cohort (`LATAM_IPO`) is just a name for a list; its members and size change
- Each enrichment run stores a dated snapshot, building a time series per cohort

---

## Step 1: Session start — always do this first

Read the state file:
```bash
cat /Users/dannazca/Factory/cohorts/nazca_enrichment_state.json
```

If it doesn't exist yet, run the setup script:
```bash
python3 /Users/dannazca/Library/Application\ Support/Claude/local-agent-mode-sessions/skills-plugin/73b8d0f3-e35b-45a5-b276-47df6b20cbd4/b4500c34-58f5-4cc3-a37e-8b540d1d2ef9/skills/nazca-cohort-enrichment/scripts/cohort_manager.py --setup
```

Then surface to the user:
- All cohorts: name, last_run, company_count, enriched_count, pending_count
- Any cohort with pending_count > 0 → flag as needs action
- Dead sources (never retry these): Financial Datasets API ($0 balance), Brightdata (HTTP 401)
- Recommended next action

---

## Step 2: Source routing — which source for which company

The source depends on whether the company is **public** (has a ticker, US-listed) or
**private** (no ticker, VC-backed startup).

| Company type | Primary source | Fallback |
|---|---|---|
| Public (US 10-K) | EDGAR `edgar_trends` | OLS model |
| Public (LatAm 20-F) | EDGAR `edgar_trends` | OLS model |
| Public (BRL reporter) | EDGAR, auto-normalize ÷FX | OLS model |
| Private (any) | Harmonic MCP | OLS model |
| Any | Rules-based scores | — |

**BRL/CNY detection:** If `edgar_revenue / source_revenue` is in range 4.5–7.0 → BRL.
If 6.5–8.5 → CNY. Script auto-divides all EDGAR monetary fields by that ratio.

**IFRS 20-F filers** (most LatAm public companies): `operating_income` and `net_income`
return N/A from EDGAR. This is expected — not an error. `gross_profit`, `total_assets`,
`total_liabilities` work fine.

---

## Step 3: Variable registry (compact)

Full detail in `references/variable_registry.md`. Quick reference:

### Financial — EDGAR (public) or OLS model (private)
| Variable | Confidence | Notes |
|---|---|---|
| `revenue_usd` | 1.00 (EDGAR) / 0.65 (OLS) | OLS uses HC × RPE × stage_mult |
| `gross_profit_usd` | 1.00 (EDGAR) | N/A for many IFRS filers |
| `gross_margin_pct` | 0.95 | gross_profit / revenue_source |
| `operating_income_usd` | 1.00 (EDGAR) | N/A for IFRS 20-F |
| `operating_margin_pct` | 0.95 | |
| `net_income_usd` | 0.90 (EDGAR) | Often N/A |
| `net_margin_pct` | 0.90 | |
| `total_assets_usd` | 1.00 (EDGAR) | |
| `total_liabilities_usd` | 1.00 (EDGAR) | |
| `debt_ratio` | 0.95 | total_liabilities / total_assets |
| `capital_efficiency_score` | 0.85 | revenue/assets, percentile-ranked *within cohort* |

### Valuation — Damodaran + EDGAR trends
| Variable | Confidence | Source |
|---|---|---|
| `ev_revenue_multiple` | 0.85 | Damodaran Jan 2026, by sector + region |
| `revenue_cagr_2yr` | 0.90 | EDGAR trends CAGR field |

### Scores — rules-based (no API call needed)
| Variable | Confidence | Method |
|---|---|---|
| `jurisdiction_risk_score` (1–10) | 0.80 | US=8, Global=7, LatAm=5, EM=4 |
| `pricing_power_score` (1–10) | 0.80 | GM>70%→9, 50–70%→7, 30–50%→5, 15–30%→3, <15%→1 |
| `sector_growth_cagr` | 0.85 | AIML/Space 45%, SaaS 23%, E-Com 21%, HealthTech 13.5%, FinTech 9%, CleanTech 8.5%, Logistics 2.4%, PropTech -15% |

### Traction — Harmonic only (private companies)
| Variable | Confidence | |
|---|---|---|
| `hc_momentum_90d` | 0.85 | Headcount % change 90d |
| `web_traffic_90d` | 0.72 | Web traffic % change 90d |
| `linkedin_growth_180d` | 0.80 | LinkedIn follower % change 180d |

**Confidence floor: 0.75.** Any variable below this threshold is recorded as N/A,
not as a score. N/A means "no data" — not "bad company".

---

## Step 4: Cohort operations

### Create or update a snapshot

A snapshot is one enrichment run for a named list at a point in time. Call:

```bash
python3 .../scripts/cohort_manager.py \
  --cohort LATAM_IPO \
  --action snapshot \
  --companies '[{"name":"Neon","ticker":null,"sector":"FinTech","region":"LatAm","country":"Brazil"},...]' \
  --date 2026-05
```

If the snapshot file already exists for that cohort+month, it is **updated** (not replaced).
Companies already enriched in the cache are skipped.

### Add or remove companies from a cohort

```bash
# Add
python3 .../scripts/cohort_manager.py --cohort LATAM_IPO --action add \
  --companies '[{"name":"Clara","sector":"FinTech","region":"LatAm"}]'

# Remove
python3 .../scripts/cohort_manager.py --cohort LATAM_IPO --action remove \
  --names '["Frubana","Justo"]'
```

The cohort membership list lives in the state file. Historical snapshots are never
modified — they reflect who was in the list at that moment.

### Query delta between two snapshots

```bash
python3 .../scripts/cohort_manager.py \
  --cohort LATAM_IPO --action delta \
  --from 2026-05 --to 2026-11
```

Output: per-variable change per company, quartile movers, new entrants, exits.

### Show cohort status

```bash
python3 .../scripts/cohort_manager.py --cohort LATAM_IPO --action status
```

---

## Step 5: Enrichment workflow

### For public companies (ticker available, US-listed)

1. Call `edgar_trends` with all 7 concepts in one call:
   ```
   concepts: ["revenue","gross_profit","operating_income","net_income",
              "total_assets","total_liabilities","equity"]
   period: "annual", periods: 3
   ```
2. Parse response → compute derived metrics → store in cohort snapshot
3. Apply rules-based scores (no API call)

Reference existing enrichment script:
```bash
python3 /Users/dannazca/Factory/enrich_publicas_gur.py --batch 10
```

### For private companies (no ticker, VC-backed)

1. Pull from Harmonic MCP: `get_company_list_entries` or `get_companies`
2. Get traction via: `web_social_headcount_timeseries` (10-call/day Harmonic limit)
3. Estimate revenue via OLS model:
   ```bash
   # In Python: from nazca_revenue_engine import estimate_revenue
   # revenue = HC × RPE_sector × stage_multiplier × region_beta
   ```
4. Score 25 behavioral tags via `nazca_tag_engine.py`
5. Apply rules-based scores

---

## Step 6: Session end — always do this

After any enrichment run, update the state file:

```bash
python3 .../scripts/cohort_manager.py --action update-state
```

This writes: last_run date, company counts, variables_available, snapshots_available.
The next session reads this file in Step 1 — this is the entire handoff mechanism.

---

## Existing scripts (do not duplicate — import or call these)

| Script | Purpose |
|---|---|
| `/Users/dannazca/Factory/enrich_publicas_gur.py` | Public company enrichment manager (CLI + cache) |
| `/Users/dannazca/Factory/build_publicas_gur_excel.py` | Builds 5-sheet Excel from cache |
| `/Users/dannazca/Factory/nazca_revenue_engine.py` | OLS revenue model for private companies |
| `/Users/dannazca/Factory/nazca_tag_engine.py` | 25-tag behavioral scorer |
| `/Users/dannazca/Factory/harmonic_timeseries_cache.py` | Harmonic traction data cache |
| `/Users/dannazca/Factory/cohorts/` | All cohort state and snapshot files |

---

## File layout

```
/Users/dannazca/Factory/cohorts/
  nazca_enrichment_state.json          ← master state (all cohorts)
  variable_registry.json               ← source priority per variable
  LATAM_IPO_2026-05.json               ← snapshot: who was in the list + their metrics
  LATAM_IPO_2026-11.json               ← next snapshot (time series begins here)
  US_IPO_2026-05.json
  Hot_Startups_2026-05.json
  Publicas_GUR_2026-05.json            ← the 96 public comparables
```
