# nazca-private-scoring

**Owner:** @dan — Nazca Investment Team  
**Status:** v1.0 · Production  
**Coverage:** 29+ dimensions · Private companies · LatAm + US

---

## What this skill does

**Ingest-first enrichment pipeline.** You bring the company list — the skill maps it to
the 29-variable schema, shows exactly what's missing per company and per source, then
enriches gaps in priority order. No redundant API calls: variables already present from
your export are never re-fetched.

| Layer | Source | How |
|---|---|---|
| **Ingest** | CSV / JSON / Harmonic MCP list | Your export, mapped automatically to schema |
| **Batch** | Harmonic MCP (10 calls/day) | 2 calls/company only for null traction + pedigree variables |
| **Unlimited** | EDGAR MCP | Sector CAGR + market liquidity, called once per sector |
| **Unlimited** | Web search | Reputation, legal flags, leadership depth |
| **Constants** | Bundled in skill | RPE, EV multiples, sector CAGR, Tier 1 lists |

Harmonic budget rule: check `--action gaps` before calling. If budget runs out mid-batch,
remaining nulls fall back automatically to EDGAR and web search.

---

## Prerequisites

**Required:**
- Claude Code with skills support (`~/.claude/skills/`)
- Python 3.9+
- Harmonic MCP configured in Claude Code
- EDGAR MCP (`edgartools`) configured in Claude Code

**Optional (enhances coverage):**
- Pitchbook export → paste into `company_inputs.json`
- LAVCA sector data → already bundled in `data/sector_phases_reference.json` (update quarterly)

**No Pitchbook or LAVCA API is required** — the skill uses portable placeholder files
that you fill from manual exports. The core scoring workflow runs without them (placeholder
variables are recorded as N/A and the score proceeds with available data).

---

## Installation

```bash
# 1. Clone
git clone https://github.com/NZCAI/dannazca-skills.git

# 2. Copy skill to Claude config
cp -R dannazca-skills/nazca-private-scoring ~/.claude/skills/

# 3. Initialize pipeline state + placeholder templates
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py --setup

# 4. Fill in your company data
open "${NAZCA_FACTORY_DIR:-$HOME/Factory}/private-scoring/inputs/company_inputs.json"

# 5. (Optional) Override Factory location
export NAZCA_FACTORY_DIR=~/my-custom-path  # default: ~/Factory

# 6. Restart Claude Code
```

Or use the installer (handles all steps):
```bash
bash dannazca-skills/nazca-private-scoring/install.sh
```

---

## Quick start

### 1. Ingest a company batch (CSV, JSON, or Harmonic MCP list)
```bash
# From a Harmonic CSV export
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action ingest --file ~/Downloads/harmonic_export.csv \
  --source harmonic_csv --cohort latam_ipo_q2 --date 2026-05

# From a Pitchbook export
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action ingest --file ~/Downloads/pitchbook_list.csv \
  --source pitchbook --cohort latam_ipo_q2

# From a Harmonic MCP list response (Claude writes MCP output to file first)
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action ingest --file /tmp/harmonic_batch.json \
  --source harmonic_mcp --cohort latam_ipo_q2
```

### 2. Check what's missing (before calling any API)
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py --action gaps
```

### 3. Record enrichment data (after Harmonic/EDGAR/web search)
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action record --company "Neon" \
  --data '{"headcount":2800,"hc_growth_90d_pct":4.2,"big_tech_experience":false}'
```

### 4. Score and snapshot
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action score --company "Neon"

python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action snapshot --cohort latam_ipo_q2 --date 2026-05
```

### 5. Compare two snapshots (delta)
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action delta --cohort latam_ipo_q2 --from 2026-05 --to 2026-08
```

---

## The 29 dimensions

| # | Variable | Source | Type |
|---|---|---|---|
| 1 | Proxy Revenue (USD) | Computed: HC × RPE × stage_mult | Quantitative |
| 2 | Proxy Fwd 12m (USD) | Computed: proxy × (1 + sector_CAGR) | Quantitative |
| 3 | Capital Efficiency | Computed: proxy / funding_raised | Ratio |
| 4 | Fundamental Value (USD) | Computed: proxy × EV/Rev_sector | Quantitative |
| 5 | Funding Raised (USD) | Placeholder: Crunchbase/Pitchbook | Quantitative |
| 6 | Last Round (USD) | Placeholder | Quantitative |
| 7 | Last Round Date | Placeholder | Date |
| 8 | Stage | Placeholder | Categorical |
| 9 | Headcount | Harmonic MCP | Quantitative |
| 10 | HC Growth 90d (%) | Harmonic MCP | Percentage |
| 11 | HC Growth 180d (%) | Harmonic MCP | Percentage |
| 12 | HC Growth 365d (%) | Harmonic MCP | Percentage |
| 13 | LinkedIn Followers | Harmonic MCP | Quantitative |
| 14 | Year Founded | Placeholder | Integer |
| 15 | Age (years) | Computed: 2026 − year_founded | Integer |
| 16 | Funding Recency (−mo) | Computed from last_round_date | Integer |
| 17 | Time-to-Liquidity (−mo) | Constants by stage | Integer |
| 18 | Sector CAGR | Built-in constants | Percentage |
| 19 | Sectorial Growth (EDGAR) | EDGAR public comp CAGR | Percentage |
| 20 | Sector Phase 2025 | LAVCA + Pitchbook reference | Categorical |
| 21 | Sector Market Liquidity | EDGAR EV/Rev trend | Qualitative |
| 22 | vs Public Sector p50 | Computed: proxy / sector median | Ratio |
| 23 | vs Cohort | Computed: proxy / pipeline median | Ratio |
| 24 | Tier 1 Investor | Placeholder + reference list | Binary |
| 25 | Big Tech Experience | Harmonic prior exp. → parse | Binary |
| 26 | LatAm Unicorn Experience | Harmonic prior exp. → parse | Binary |
| 27 | Top VC Experience | Harmonic prior exp. → parse | Binary |
| 28 | Public Co Experience | Harmonic prior exp. → parse | Binary |
| 29 | Reputation Summary | Web search | Qualitative |
| 30 | Legal Flag | Web search | Binary + note |
| 31 | Leadership Pedigree | Harmonic bio + web search | Qualitative |

---

## Data flow

```
CSV / JSON / Harmonic list ──► --action ingest ──► snapshot + gap analysis
                                                          │
                      ┌───────────────────────────────────┤
                      │                                   │
               Harmonic MCP                         EDGAR + web search
           (budget check first,                   (no limit, fills remaining
            2 calls/company)                       nulls after Harmonic)
                      │                                   │
                      └───────────────┬───────────────────┘
                                      │
                               --action record
                               --action score
                               --action snapshot
```

---

## Source routing summary

| Source | Daily limit | Variables |
|---|---|---|
| Harmonic MCP | **10 calls/day** | Headcount, growth, LinkedIn, prior experiences |
| EDGAR MCP | None | Sector growth CAGR, market liquidity |
| Web search | None | Reputation, legal flag, leadership depth |
| Placeholder file | None | Funding, stage, year founded, investors |
| Constants (built-in) | None | RPE, sector CAGR, EV multiples, stage multipliers |

**Harmonic budget:** 2 calls per company (1 for traction, 1 for founders). Max 5 companies/day.  
**Fallback:** when budget exhausted, remaining Harmonic-sourced variables fall back to web search (lower confidence, noted as 0.70).

---

## File structure

```
nazca-private-scoring/
├── SKILL.md                      ← Claude instructions (loaded every session)
├── README.md                     ← This file
├── install.sh                    ← Idempotent installer
├── scripts/
│   └── private_score_manager.py  ← Pipeline CLI
├── data/
│   ├── sector_phases_reference.json   ← LAVCA + Pitchbook phases (update quarterly)
│   └── tier1_investors_reference.json ← Tier 1 lists for pedigree parsing
└── references/
    └── variable_registry.md      ← Full variable definitions + edge cases
```

**Live state (not in repo — created by --setup):**
```
~/Factory/private-scoring/
  state.json                       ← pipeline: companies, statuses, Harmonic call budget
  inputs/
    company_inputs.json            ← manual overrides (prefer --action ingest for batches)
    rpe_overrides.json             ← custom RPE calibration (optional)
  snapshots/
    latam_ipo_q2_2026-05.json      ← dated snapshot (all companies + variables)
    latam_ipo_q2_2026-08.json      ← next snapshot (enables --action delta)
  scores/
    [company_slug].json            ← per-company variable data + score_summary
```
