# nazca-private-scoring

**Owner:** @dan — Nazca Investment Team  
**Status:** v1.0 · Production  
**Coverage:** 29+ dimensions · Private companies · LatAm + US

---

## What this skill does

Scores private companies across 29 dimensions combining three data layers:

| Layer | Source | How |
|---|---|---|
| **Live** | Harmonic MCP | Headcount, growth, LinkedIn, founder backgrounds |
| **Live** | EDGAR MCP | Sector growth CAGR, market liquidity from public comps |
| **Live** | Web search | Reputation, legal flags, leadership depth |
| **Placeholder** | `company_inputs.json` | Funding, stage, year founded — from Pitchbook/Crunchbase exports |
| **Constants** | Bundled in skill | RPE, sector CAGR, EV multiples, Tier 1 investor lists |

The skill manages the pipeline so each session continues exactly where the last one stopped.

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

### Add companies to the scoring pipeline
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action add \
  --companies '[{"name":"Neon","sector":"FinTech","stage":"Series D","region":"LatAm","country":"Brazil"}]'
```

### Check pipeline status
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py --action status
```

### Record variable data (after pulling from Harmonic + web search)
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action record --company "Neon" \
  --data '{"headcount":2800,"hc_growth_90d_pct":4.2,"tier1_investor":true}'
```

### Compute score snapshot
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action score --company "Neon"
```

### Export full scorecard
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action export --company "Neon"
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
Harmonic MCP ──────────┐
EDGAR MCP ─────────────┤──► private_score_manager.py ──► scores/company.json
Web search ────────────┤         (records + computes)
company_inputs.json ───┘
         ↑
   Fill manually from
   Pitchbook / Crunchbase
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
  state.json                       ← pipeline: which companies, their status
  inputs/
    company_inputs.json            ← YOUR Pitchbook/Crunchbase data
    rpe_overrides.json             ← custom RPE calibration (optional)
  scores/
    [company_slug].json            ← per-company variable data + score snapshot
```
