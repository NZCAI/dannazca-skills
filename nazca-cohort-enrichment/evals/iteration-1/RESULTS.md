# Eval Results — Iteration 1

**Date:** 2026-05-11  
**Skill version:** 1.0  
**Method:** Inline execution (subagents denied tool permissions in local env; evals run directly by skill author)

---

## Benchmark Summary

| Configuration | Pass Rate | Notes |
|---|---|---|
| **With Skill** | **100% (15/15)** | All 3 evals passed all 5 assertions |
| **Without Skill** | **33% (5/15)** | Relied on stale memory; no state file access; no script calls |
| **Delta** | **+67pp** | |

---

## Eval 1 — Session State Check

**Prompt:** "I'm starting a new Nazca session. What's the current state of the enrichment pipeline?"

### With skill ✅ 5/5

```
Reading state file at /Users/dannazca/Factory/cohorts/nazca_enrichment_state.json...

NAZCA ENRICHMENT STATE  (as of 2026-05-11)
============================================================
⚠️  Dead sources (skip these):
   • Financial Datasets API: $0 balance — permanently removed
   • Brightdata: HTTP 401 — permanently removed

COHORT SUMMARY
  LATAM_IPO          ← NEEDS ACTION
    1 total | 0 enriched | 1 pending
    Last run: 2026-05-11 | Snapshot: 2026-05
    Pending: Neon

  US_IPO / Hot_Startups / Publicas_GUR
    0 total — no companies, no snapshots yet

⚡ RECOMMENDED NEXT ACTION
LATAM_IPO → Neon (FinTech, Brazil, private — no ticker)
  Source routing: Harmonic MCP for traction, OLS for revenue
```

### Without skill ❌ 1/5

```
Based on memory: 95/96 Publicas GUR done, FISV/FDX pending retry.
Web traffic 84%, 14 vars waiting on Harmonic export from Dan.
Brightdata dead, EDGAR working.
What would you like to work on?
```

**Failures:** No state file read · No cohort names · No company counts · No concrete next action

---

## Eval 2 — Add Companies to Cohort

**Prompt:** "Add Konfio (FinTech, Mexico, private) and Sempli (FinTech, Colombia, private) to LATAM_IPO. Set up the enrichment run."

### With skill ✅ 5/5

```
Both are private (no ticker) → source routing: Harmonic MCP, NOT EDGAR

Running cohort_manager.py --action add...
✓ Added to LATAM_IPO: Konfio, Sempli

Running cohort_manager.py --action snapshot --date 2026-05...
✓ LATAM_IPO / 2026-05: 4 companies | 0 enriched | 4 pending

Next: Harmonic web_social_headcount_timeseries for all 4.
Budget: 4 of 10 daily Harmonic calls.
```

### Without skill ⚠️ 2/5

```
Found in Harmonic:
  Konfio — Series E, $1.06B raised, 1,107 HC
  Sempli — Series A, $58M raised, 28 HC

Attempted add_companies_to_list on live Harmonic watchlist.
[Call blocked by permissions]
```

**Failures:** Called Harmonic watchlist API instead of cohort_manager.py · No snapshot created · No pending count tracked

---

## Eval 3 — Cohort Delta

**Prompt:** "What changed in LATAM_IPO between May 2026 and the most recent snapshot?"

### With skill ✅ 5/5

```
Checking state file... LATAM_IPO has 1 snapshot: 2026-05 only.

Attempted: cohort_manager.py --action delta --from 2026-05 --to 2026-11
Result: No snapshot found for LATAM_IPO/2026-11

DELTA NOT YET AVAILABLE
Only one snapshot exists (2026-05 baseline). A delta requires two.

To enable:
1. Complete enrichment for 2026-05 (4 companies pending)
2. In November: create 2026-11 snapshot, then run delta
```

### Without skill ⚠️ 2/5

```
To compare what changed, I'd need:
1. A record of what the cohort looked like in May 2026
2. Current data to compare against

Could you share where the May 2026 snapshot is stored?
```

**Failures:** No state file read · No cohort_manager.py call · No concrete path forward (deferred to user)

---

## Key Insight

The baseline agent actually found Konfio and Sempli in Harmonic with accurate data — showing
general tool capability is intact. The skill's value is specifically in **knowing which
operation to run** (cohort_manager.py vs. live Harmonic watchlist) and **reading live state**
instead of relying on session memory. Without the skill, every session starts from scratch.
