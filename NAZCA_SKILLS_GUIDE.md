# Nazca Investment Skills — User Guide

**Skills:** `nazca-cohort-enrichment` · `nazca-private-scoring`  
**Repo:** `NZCAI/dannazca-skills`  
**Audience:** Nazca investment team  
**Updated:** 2026-05-14

---

## How these skills work

Both skills are loaded into every Claude Code session automatically — you don't invoke them
with a command. Just talk normally about companies, enrichment, or scoring and Claude detects
the context and activates the right skill.

**Key shared principle:** Sessions are stateless. These skills give Claude persistent memory
across sessions by reading and writing JSON state files on your machine.

---

# Skill 1 — nazca-cohort-enrichment

**What it solves:** Without this skill, every session starts from zero. Claude doesn't know
which companies are pending, which sources to use, or what was done last time.
With the skill, every session begins with a status read and surfaces exactly what to do next.

## User stories

### US-01 — Starting a session without losing context
> *"As an analyst, I want Claude to know where we left off so I don't have to re-explain the pipeline state at the start of every session."*

**How it works:** The skill reads `~/Factory/cohorts/nazca_enrichment_state.json` at session start
and surfaces: cohort sizes, pending company counts, dead sources, and recommended next action.

**Trigger phrases:**
- "Empieza la sesión"
- "Pick up where we left off"
- "What's pending?"
- "Starting fresh — what do we have?"

---

### US-02 — Adding companies to a cohort
> *"As an analyst, I want to add new companies to the LATAM_IPO watchlist without losing the previous list or history."*

**How it works:** Claude calls `cohort_manager.py --action add` with the new companies.
The membership list updates in state. Historical snapshots are never modified.

**Example conversation:**
```
User: Add Clara (FinTech, Mexico, private) and Kueski (FinTech, Mexico, private) to LATAM_IPO.
Claude: Calls --action add, confirms both added, shows updated cohort size.
```

**Trigger phrases:**
- "Agrega [company] al cohort [name]"
- "Add these companies to LATAM_IPO"
- "Put [list of companies] in Hot_Startups"

---

### US-03 — Tracking what changed between sessions (delta)
> *"As a portfolio manager, I want to know which companies moved significantly between May and August — who grew, who stagnated, who exited."*

**How it works:** Each enrichment run creates a dated snapshot. The delta command compares
two snapshots and shows per-company per-variable changes.

**Example conversation:**
```
User: What changed in LATAM_IPO between May and November?
Claude: Calls --action delta --from 2026-05 --to 2026-11
Output: Clara: HC grew +18%, funding recency worsened to -24mo. Neon: new entrant. Frubana: exited.
```

**Trigger phrases:**
- "¿Qué cambió entre mayo y agosto?"
- "Show me the delta for LATAM_IPO"
- "Who are the new entrants this quarter?"
- "Compare this snapshot to last quarter"

---

### US-04 — Source routing without thinking about it
> *"As an analyst, I want Claude to automatically use EDGAR for public companies and Harmonic for private — not waste Harmonic calls on tickers."*

**How it works:** The skill's source routing table is loaded into every session.
Claude checks company type (public = has ticker) before choosing a data source.

**Rule embedded in skill:**
- Public (US 10-K, LatAm 20-F) → EDGAR `edgar_trends` (no daily limit)
- Private (no ticker, VC-backed) → Harmonic MCP (10 calls/day)
- Dead forever: Financial Datasets API ($0 balance), Brightdata (HTTP 401)

**Trigger phrases:**
- "Enrich these companies" (Claude routes each automatically)
- "Get the financials for [public company]"
- "Pull traction for [private company]"

---

### US-05 — Session handoff at the end
> *"As an analyst, I want the next session to know what was done this session — without having to write notes manually."*

**How it works:** At session end, Claude runs `--action update-state` which writes last_run date,
company counts, and snapshots_available to the state file. The next session reads this.

**Trigger phrases:**
- "Session handoff"
- "Wrap up, save state"
- "We're done for today"

---

## Use cases

### UC-01 — Weekly pipeline review
**Who:** Analyst or PM  
**Frequency:** Weekly  
**Steps:**
1. Open Claude Code, start a new session
2. Say: *"Empieza la sesión — weekly pipeline review"*
3. Skill reads state → surfaces companies pending enrichment per cohort
4. Analyst enriches 2–3 companies (EDGAR for public, Harmonic for private)
5. Snapshot created automatically
6. Say: *"Session handoff"* → state updated for next session

**Value:** 10-minute session instead of 45-minute re-orientation.

---

### UC-02 — Adding companies after a scouting call
**Who:** Associate after a demo or intro call  
**Steps:**
1. *"I just met Sempli (FinTech, Colombia, private) and Kushki (FinTech, Ecuador, private) — add them to LATAM_IPO"*
2. Skill adds both to cohort, shows updated count
3. *"What do we need to enrich them?"*
4. Skill shows: need Harmonic traction pull + EDGAR sector benchmarks

**Value:** Companies are in the system before the next enrichment session.

---

### UC-03 — Quarterly IC report preparation
**Who:** Senior analyst  
**Steps:**
1. Run delta for all 4 cohorts between Q1 and Q2 snapshots
2. Identify top movers (HC growth, funding recency worsened, new entrants)
3. Export per-company variable data for the IC memo

**Value:** Reproducible, sourced data — no copy-paste from spreadsheets.

---

# Skill 2 — nazca-private-scoring

**What it solves:** Scoring private companies across 29 dimensions requires pulling from
3+ sources, mapping different field names, tracking what's been done, and never wasting
limited Harmonic calls on variables you already have. This skill manages all of that.

## User stories

### US-06 — Ingesting a company batch without re-entering data
> *"As an analyst, I want to drop a Harmonic CSV export or Pitchbook list and have it immediately mapped to our scoring schema — without reformatting or copy-pasting."*

**How it works:** `--action ingest` reads any CSV or JSON, maps column names via
`field_mappings.json`, and fills whatever variables it can find. No manual entry needed.

**Supported formats:** Harmonic CSV, Harmonic MCP list response, Pitchbook, Crunchbase, inline JSON

**Example conversation:**
```
User: [pastes 15 companies as JSON, or shares "harmonic_export.csv"]
Claude: Ingests file, maps fields, creates snapshot, shows gaps.
Output: "15 companies added. Neon: 19/31 variables filled. Clara: 12/31 filled."
```

**Trigger phrases:**
- "Tengo esta lista de compañías, scoreéalas"
- "Score these 12 companies" + pastes a list
- "I exported this from Harmonic" + shares file
- "Ingest this Pitchbook export"

---

### US-07 — Knowing exactly how many Harmonic calls I need before using any
> *"As an analyst respecting the 10-call/day Harmonic limit, I want to know how many calls the batch needs before I start — so I can plan across sessions."*

**How it works:** `--action gaps` shows per-company null variables by source,
and prints a budget summary: calls needed, calls remaining, and a fallback plan if over budget.

**Example output:**
```
Harmonic budget: 7/10 calls remaining today
Budget OK: can enrich all 3 pending companies (6 calls)
Action: call get_companies + get_people for each, then --action record
```
or:
```
Budget WARNING: only 3/7 companies fit today's Harmonic budget
4 companies → fall back to EDGAR + web search for remaining nulls
```

**Trigger phrases:**
- "¿Qué datos faltan?"
- "Show me the gaps"
- "How many Harmonic calls do I need?"
- "What's missing for [company]?"

---

### US-08 — Loading a Harmonic list directly from its URN
> *"As an analyst, I want to point Claude at a pre-created Harmonic list and have it automatically ingest all the companies with their traction data."*

**How it works:** User provides the Harmonic list URN → Claude calls
`get_company_list_entries(list_id=URN)` → writes result to `/tmp/harmonic_batch.json`
→ runs `--action ingest --source harmonic_mcp`. One command, no export step.

**Example conversation:**
```
User: "Load the Hot Startups Q2 list from Harmonic — the URN is urn:harmonic:saved_search:123456"
Claude: Calls Harmonic MCP → writes response → ingests → creates snapshot → shows gaps.
```

**Trigger phrases:**
- "Load this Harmonic list: [URN]"
- "Ingest saved search [ID] from Harmonic"
- "Pull the [list name] from Harmonic"

---

### US-09 — Scoring with Harmonic budget exhausted
> *"As an analyst who used 8/10 Harmonic calls today, I want to still make progress on the remaining companies using EDGAR and web search."*

**How it works:** The budget fallback rule is embedded in SKILL.md. When budget runs out:
- Harmonic-sourced traction variables → web search (noted as 0.70 confidence)
- Sector growth (`sector_growth_edgar`) → EDGAR, no limit
- Sector market liquidity → EDGAR, no limit
- Reputation, legal flag, pedigree → web search, no limit

Companies get a partial score (computed metrics still fill from headcount if available from ingest).

**Trigger phrases:**
- "We're out of Harmonic calls, keep going"
- "Use web search for the rest"
- "Continue without Harmonic"

---

### US-10 — Comparing company cohort across two time periods
> *"As a portfolio manager, I want to see how our Q2 private company pipeline evolved by Q3 — which metrics improved, which deteriorated."*

**How it works:** Two snapshots → `--action delta` → per-company per-variable table with % change.

**Example output:**
```
COHORT DELTA — LATAM_IPO_Q2
  2026-05 → 2026-08
  Neon    headcount        +10.7%   (2,800 → 3,100)
  Neon    proxy_revenue    +10.7%   ($382M → $423M)
  Clara   hc_growth_90d    -3.2pp   (8.5% → 5.3%)
  Kavak   funding_recency  -3mo     (-36 → -39)
```

---

## Use cases

### UC-04 — New deal intake from Harmonic watchlist
**Who:** Associate reviewing a Harmonic saved search  
**Steps:**
1. Pull Harmonic list URN from saved search
2. *"Load this Harmonic list: [URN]"*
3. Skill ingests, shows: 8 companies, 12/31 variables filled on average
4. `--action gaps` → 8 companies need 2 Harmonic calls each = 16 calls (needs 2 days)
5. Day 1: enrich 5 companies (10 calls). Day 2: enrich remaining 3.
6. EDGAR + web search fill sector and qualitative variables — no limit

**Value:** Structured intake in one conversation. No spreadsheet setup.

---

### UC-05 — Pre-IC scoring sprint
**Who:** Analyst preparing 3 companies for IC in 48 hours  
**Steps:**
1. Ingest 3 companies from Pitchbook export
2. `--action gaps` → each needs 2 Harmonic calls + EDGAR + web search
3. 6 Harmonic calls total → fits in one day
4. Run EDGAR for sector benchmarks (no limit)
5. Run web search for reputation + legal flags
6. `--action score` for each → score_summary JSON ready for IC memo

**Value:** 29-variable IC-ready scorecard in one session.

---

### UC-06 — Routine enrichment refresh (monthly)
**Who:** Any analyst, recurring  
**Steps:**
1. Re-ingest the same Harmonic list (updated HC data)
2. New snapshot created automatically with updated date
3. `--action delta` vs prior month → see who accelerated, who decelerated
4. Update scores for changed companies only

**Value:** Systematic tracking without re-doing all the work.

---

---

# How both skills work together

The two skills cover **different stages of the same pipeline**:

```
nazca-cohort-enrichment          nazca-private-scoring
─────────────────────────        ──────────────────────────────
Tracks WHICH companies           Scores HOW GOOD each company is
are in the pipeline              across 29 dimensions

Manages cohort membership        Manages variable collection
and time-series snapshots        and score computation

Knows what's pending             Knows what's null per source
across all cohorts               and how many API calls you need

Session continuity               Ingest-first, budget-aware
via state file reads             enrichment workflow
```

## Shared patterns (by design)

Both skills use:
- The same `NAZCA_FACTORY_DIR` env var and `~/Factory/` default
- The same snapshot pattern: dated JSON files for time-series comparison
- The same delta command: `--from YYYY-MM --to YYYY-MM`
- The same confidence floor: 0.75 (below = N/A, never a number)
- The same install pattern: `install.sh --yes` / `--uninstall`

## User stories — using both skills together

### US-11 — Unified session start
> *"As an analyst, I want one session start that tells me: what cohorts exist, what's pending enrichment, and which companies in the pipeline already have scoring data."*

**How it works:** Start with cohort-enrichment (session state) → identify private companies
with pending enrichment → switch to private-scoring (gaps check) → work from there.

**Example flow:**
```
User: "Empieza la sesión"

→ cohort-enrichment activates:
   LATAM_IPO: 12 companies, 3 pending enrichment
   Hot_Startups: 8 companies, 5 pending enrichment

→ User: "Show me the scoring gaps for the Hot_Startups pending companies"

→ private-scoring activates:
   5 companies, 15/31 variables on average
   Harmonic: 10 calls needed (fits today)
   EDGAR + web: run now, no limit
```

---

### US-12 — Enrichment result feeds both systems
> *"As an analyst, after enriching a company, I want both the cohort tracker and the scoring pipeline to be updated."*

**How it works:**
1. Pull Harmonic traction for company X
2. `private-scoring --action record --company X --data {...}` → variables saved
3. `cohort-enrichment --action snapshot --cohort LATAM_IPO` → cohort state updated
4. Both state files reflect the new data

**Example:**
```
User: "I just enriched Neon — headcount 3,100, HC growth 12% 90d, Sequoia lead"

→ Claude records to private-scoring scores/neon.json
→ Claude updates cohort-enrichment snapshot for LATAM_IPO
→ Both systems now show Neon as enriched
```

---

### US-13 — Quarterly portfolio review using both skills
> *"As a PM, I want a quarterly view: which companies moved cohorts, which improved scores, which have new flags."*

**How it works:**
1. `cohort-enrichment delta`: who entered/exited each cohort this quarter
2. `private-scoring delta`: how did scores change for companies that stayed
3. Combined output: movers by cohort + score trajectory per company

**Example IC-ready summary:**
```
LATAM_IPO Q2→Q3:
  New entrants: Nuvemshop (moved from Hot_Startups)
  Exits: Frubana (removed, score deteriorated)
  
  Score changes (stayed):
  Neon:  HC +10.7%, proxy revenue +10.7%, legal_flag still false ✓
  Clara: HC growth slowed (-3pp), funding recency worsened to -29mo ⚠️
  Kavak: No change — re-enrich pending (Harmonic data stale >90d)
```

---

### US-14 — Graduated company workflow (Hot_Startups → LATAM_IPO)
> *"As an analyst, I want to move a company from the Hot_Startups watchlist to the LATAM_IPO pipeline when it meets scoring thresholds."*

**How it works:**
1. `private-scoring --action score --company Nuvemshop` → score summary shows
   capital_efficiency = 0.8, tier1_investor = true, hc_growth_365d = 45%
2. Analyst decides: ready for LATAM_IPO
3. `cohort-enrichment --action add --cohort LATAM_IPO --companies [Nuvemshop]`
4. `cohort-enrichment --action remove --cohort Hot_Startups --names [Nuvemshop]`
5. Both systems updated, history preserved in both snapshot chains

---

## Use cases — combined

### UC-07 — Monday morning pipeline review (15 min)
**Both skills active in one session**

1. *"Start the session"*
   - cohort-enrichment: shows 3 cohorts, 7 companies pending
2. *"Show scoring gaps for the 7 pending"*
   - private-scoring: gaps output, 14 Harmonic calls needed (2 days)
3. *"Enrich the 5 that fit today's Harmonic budget"*
   - Pull Harmonic for 5 companies → record → score each
   - EDGAR sector data (no limit) → record for all 7
4. *"Update both snapshots"*
   - private-scoring snapshot → cohort-enrichment snapshot
5. *"Session handoff"*
   - Both state files saved

---

### UC-08 — New deal sourced from Pitchbook screen
**Intake to score in one session**

1. Export Pitchbook results as CSV
2. *"Ingest this Pitchbook export"* (private-scoring)
   - 8 companies, 10/31 variables filled on average
3. *"Add these 8 to Hot_Startups"* (cohort-enrichment)
   - Cohort updated, membership tracked
4. *"Show gaps"* (private-scoring)
   - 8 × 2 = 16 Harmonic calls — plan across 2 days
5. Session 1: enrich 5. Session 2: enrich remaining 3 + web search all.
6. Both systems reflect enrichment progress between sessions.

---

### UC-09 — IC memo data pull
**Both skills provide sourced, reproducible data**

1. `cohort-enrichment`: export snapshot for LATAM_IPO Q2
2. `private-scoring`: export score_summary for each company in snapshot
3. Combined output: IC memo table with all 29 variables, confidence levels, sources
4. All numbers are traceable (EDGAR file, Harmonic pull date, web search query)

**Value:** IC memo backed by primary sources, not analyst memory.
