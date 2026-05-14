---
name: nazca-private-scoring
description: "Scores private companies across 29 dimensions for Nazca's investment pipeline. Trigger whenever the user: provides a company list or batch and asks to score, evaluate, or enrich; says 'run scoring', 'ingest this list', 'score these companies', or 'pick up where we left off'; mentions any of the 29 GUR variables (proxy revenue, headcount growth, capital efficiency, leadership pedigree, tier 1 investor, etc.); references a Harmonic export, Pitchbook list, or CSV with company data; asks about founder background, investor pedigree, or sector benchmarks for private companies; asks 'what's the score', 'what's missing', 'show gaps', or 'compare snapshots'. Also trigger at the start of any session involving private LatAm or US company investment analysis."
---

# Nazca Private Company Scorer

## What this skill does

**Ingest-first enrichment pipeline.** The user provides the company list — the skill does not
pull companies from external sources. It maps whatever data arrives (CSV, JSON, or a Harmonic
MCP response written to file) to the 29-variable schema, identifies exactly what is missing per
company, then enriches gaps in source-priority order — Harmonic batch → EDGAR → web search.

Core insight: **never call an API for a variable you already have.**

---

## Step 1: Session start — always do this first

Read the pipeline state:
```bash
cat "${NAZCA_FACTORY_DIR:-$HOME/Factory}/private-scoring/state.json"
```

If it doesn't exist yet, initialize:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py --setup
```

Then show status:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py --action status
```

Surface to the user:
- Total companies · how many scored · how many pending
- Harmonic calls used today and remaining (10-call/day limit)
- Recommended next action

---

## Step 2: Ingest — load the company batch

The user provides a company list. Three input methods:

### Method A — CSV file (Harmonic or Pitchbook export)
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action ingest \
  --file ~/Downloads/harmonic_export.csv \
  --source harmonic_csv \
  --cohort latam_ipo_q2 \
  --date 2026-05
```

`--source` options: `harmonic_csv` · `pitchbook` · `crunchbase` · `nazca_internal` · `auto`  
`--cohort` labels this batch for snapshot grouping and delta comparisons.  
`--date` sets the snapshot date (default: current month).

### Method B — JSON file (Harmonic MCP list response)

When the user provides a Harmonic list URN, call the MCP tool first, write the result to
a temp file, then ingest:

```python
# Step 1 — call Harmonic MCP (Claude executes this)
result = get_company_list_entries(list_id="urn:harmonic:saved_search:XXXXXX")
# OR: result = get_saved_search_companies_results(saved_search_id="XXXXXX")

# Step 2 — write result to temp file
with open("/tmp/harmonic_batch.json", "w") as f:
    json.dump(result, f)
```

```bash
# Step 3 — ingest
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action ingest \
  --file /tmp/harmonic_batch.json \
  --source harmonic_mcp \
  --cohort latam_ipo_q2 \
  --date 2026-05
```

The field mapper handles the Harmonic MCP response structure automatically.

### Method C — Inline JSON paste

When the user pastes a company list directly in the chat, write it to a temp file first:
```bash
# Write inline data to temp file (Claude does this)
cat > /tmp/inline_batch.json << 'EOF'
[
  {"name":"Neon","sector":"FinTech","stage":"Series D","country":"Brazil","headcount":2800},
  {"name":"Kavak","sector":"Marketplace","stage":"Series G+","country":"Mexico"}
]
EOF

python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action ingest --file /tmp/inline_batch.json --source nazca_internal --cohort my_cohort
```

**After ingest:** the script automatically creates a dated snapshot and prints a gap summary.

---

## Step 3: Snapshot + Gap analysis

Ingest always creates a snapshot. To create one manually or to refresh after enrichment:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action snapshot --cohort latam_ipo_q2 --date 2026-05
```

Then show what's missing per company, grouped by enrichment source:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action gaps
```

Read the gaps output carefully before calling any API:
- **Harmonic** — budget-check first. Shows calls needed.
- **EDGAR** — no limit, run anytime.
- **Web search** — no limit, run anytime.
- **Auto-computed** — fills automatically when dependencies (HC, funding) are recorded.
- **Missing from ingest** — re-export with a richer data source.

Compare two snapshots to see what changed:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action delta --cohort latam_ipo_q2 --from 2026-05 --to 2026-08
```

---

## Step 4: Variable registry — all 29 dimensions

### Group A — Financial / Proxy (auto-computed — never call an API for these)
| # | Variable | Formula | Confidence |
|---|---|---|---|
| 1 | `proxy_revenue_usd` | HC × RPE_sector × stage_mult | 0.65 (estimate) |
| 2 | `proxy_fwd_12m_usd` | proxy × (1 + sector_CAGR) | 0.60 |
| 3 | `capital_efficiency` | proxy / funding_raised | 0.65 |
| 4 | `fundamental_value_usd` | proxy × EV/Rev_sector | 0.60 |

RPE constants (v3.2): AIML $250k · SaaS $220k · FinTech $130k · HealthTech $160k · E-Com $55k · Marketplace $70k · Logistics $80k · CleanTech $120k  
Stage multipliers: Pre-Seed 0.4 · Seed 0.6 · A 0.8 · B 0.95 · C 1.0 · D 1.05 · E+ 1.1 · Pre-IPO 1.25  
EV/Rev (Damodaran Jan 2026): AIML 18× · SaaS 8.5× · FinTech 5× · HealthTech 6× · E-Com 2.5× · Logistics 2×

### Group B — Funding / Stage (from ingest — Crunchbase / Pitchbook / CSV)
| # | Variable | Ingest field | Confidence |
|---|---|---|---|
| 5 | `funding_raised_usd` | Total Raised / Total Funding Amount | 0.90 |
| 6 | `last_round_usd` | Last Round Size / Last Deal Size | 0.90 |
| 7 | `last_round_date` | Last Funding Date / Last Deal Date | 0.90 |
| 8 | `stage` | Last Funding Type / Deal Type | 0.90 |

### Group C — Traction (Harmonic MCP — batch per company)
| # | Variable | Harmonic field | Confidence |
|---|---|---|---|
| 9 | `headcount` | headcount | 0.90 |
| 10 | `hc_growth_90d_pct` | headcount_growth_90_days | 0.85 |
| 11 | `hc_growth_180d_pct` | headcount_growth_180_days | 0.85 |
| 12 | `hc_growth_365d_pct` | headcount_growth_365_days | 0.85 |
| 13 | `linkedin_followers` | linkedin_follower_count | 0.80 |

### Group D — Temporal (auto-computed from ingest data)
| # | Variable | Formula | Confidence |
|---|---|---|---|
| 14 | `year_founded` | from ingest | 0.95 |
| 15 | `age_years` | 2026 − year_founded | 0.95 |
| 16 | `funding_recency_mo` | −(months since last_round_date) | 0.90 |
| 17 | `time_to_liquidity_mo` | Stage lookup: Pre-IPO=−18, G+=−30, F=−36, E=−48, D=−60, C=−84 | 0.80 |

### Group E — Benchmarks (constants + EDGAR + computed)
| # | Variable | Source | Confidence |
|---|---|---|---|
| 18 | `sector_cagr` | Built-in constants | 0.85 |
| 19 | `sector_growth_edgar` | EDGAR `edgar_trends` on 2–3 public comps | 0.90 |
| 20 | `sector_phase_2025` | `data/sector_phases_reference.json` | 0.80 |
| 21 | `sector_market_liquidity` | EDGAR EV/Rev trend, qualitative | 0.85 |
| 22 | `vs_public_sector_p50` | proxy / median public sector revenue | 0.75 |
| 23 | `vs_cohort` | proxy / median of pipeline companies in same sector | 0.75 |

### Group F — Qualitative Binary (Harmonic + reference lists)
| # | Variable | Method | Confidence |
|---|---|---|---|
| 24 | `tier1_investor` | From ingest investors list → match `data/tier1_investors_reference.json` | 0.90 |
| 25 | `big_tech_experience` | Harmonic 'prior experiences' → match `big_tech_companies` list | 0.85 |
| 26 | `latam_unicorn_experience` | Harmonic prior exp. → match `latam_unicorns` | 0.85 |
| 27 | `top_vc_experience` | Harmonic prior exp. → match `global_tier1` / `latam_tier1` | 0.85 |
| 28 | `public_co_experience` | Harmonic prior exp. → match `public_cos_latam_relevant` | 0.85 |

**Parsing rule:** call `get_people` for founders + C-suite. For each person's work history,
check employer names (case-insensitive substring) against `data/tier1_investors_reference.json`.
Binary = true if ANY qualifying person matches. One `get_people` call per company.

### Group G — Qualitative open (web search)
| # | Variable | Query | Confidence |
|---|---|---|---|
| 29 | `reputation_summary` | "[Company] review trust glassdoor trustpilot" | 0.70 (note only) |
| 30 | `legal_flag` | "[Company] lawsuit regulatory fine penalty site:reuters.com OR ft.com" | 0.75 |
| 31 | `leadership_pedigree` | "[CEO name] [Company] background" | 0.75 |

**Confidence floor: 0.75.** Variables below this are stored as qualitative notes, not numeric scores.

---

## Step 5: Enrichment workflow — budget-aware, no redundant calls

**Rule: check `--action gaps` output before calling any API. Never call an API for a
variable already filled from ingest.**

### Harmonic enrichment (budget check first)

```
gaps output shows: N companies need Harmonic, requires 2N calls
state.json shows: X calls used today, 10-X remaining

If 2N ≤ (10-X): enrich all N companies via Harmonic now.
If 2N > (10-X): enrich floor((10-X)/2) companies, route the rest to EDGAR + web search.
```

For each company within budget, make exactly 2 Harmonic calls:
1. `get_companies` (or `get_company_list_entries`) → extract traction (Groups C)
2. `get_people` → extract founders/CEO prior experiences → parse Groups F

Record immediately after each company (do not batch record at the end):
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action record --company "CompanyName" \
  --data '{"headcount":2800,"hc_growth_90d_pct":4.2,...}'
```

### EDGAR enrichment (no limit — run for all companies, once per sector)

EDGAR sector data is shared across all companies in the same sector — call once, apply to all:
1. Identify unique sectors in the pipeline
2. For each sector, call `edgar_trends` on 2–3 representative public comps
3. Extract revenue CAGR → `sector_growth_edgar`
4. Extract EV/Rev trend → `sector_market_liquidity` (qualitative: expanding / stable / contracting)
5. Record for all companies in that sector at once

### Web search fallback (no limit — fill remaining nulls)

For companies where Harmonic budget was exhausted OR for Group G variables:
- `reputation_summary`: search the company name + trust/review keywords
- `legal_flag`: search company name + regulatory/lawsuit keywords
- `leadership_pedigree`: search CEO/founder name for background depth
- Any Harmonic Group F binaries not filled: attempt via web search (lower confidence — note as 0.70)

---

## Step 6: Score + session end

After enrichment, score each company:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action score --company "CompanyName"
```

Create a post-enrichment snapshot to capture the updated state:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action snapshot --cohort my_cohort --date 2026-05
```

Update pipeline state:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action update-state
```

Give the user a session summary:
- Companies scored this session
- Harmonic calls consumed today (X/10)
- Companies remaining and what's blocking each
- Next recommended action

---

## File layout

```
~/Factory/private-scoring/   (or $NAZCA_FACTORY_DIR/private-scoring/)
  state.json                           ← pipeline state: all companies, call budget, statuses
  inputs/
    company_inputs.json                ← manual overrides (prefer --action ingest for batches)
    rpe_overrides.json                 ← custom RPE calibration (optional)
  snapshots/
    latam_ipo_q2_2026-05.json          ← dated snapshot: all companies + variables at that point
    latam_ipo_q2_2026-08.json          ← next snapshot (enables delta comparison)
  scores/
    neon.json                          ← per-company: variables + score_summary
    kavak.json
```

**Reference data (ships with skill — update quarterly):**
- `data/field_mappings.json` — maps CSV/JSON export columns to schema
- `data/sector_phases_reference.json` — LAVCA + Pitchbook sector phases
- `data/tier1_investors_reference.json` — Tier 1 lists for pedigree parsing
