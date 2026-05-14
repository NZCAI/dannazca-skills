---
name: nazca-private-scoring
description: "Scores private companies across 29 dimensions for Nazca's investment pipeline. Trigger whenever the user: says 'score', 'evaluate', or 'run scoring' for a company; mentions any of the 29 GUR variables (proxy revenue, headcount growth, capital efficiency, leadership pedigree, etc.); references Harmonic data for a private company; asks about founder background, investor tier, or pedigree; hands you a company name or list and asks for a GUR score, investment score, or comparable analysis; says 'what's the score for', 'compare these companies', 'add to scoring pipeline', or 'pick up where we left off on scoring'. Also trigger at the start of any session where the user is doing investment analysis on private LatAm or US companies."
---

# Nazca Private Company Scorer

## What this skill does

Scores private companies across **29 dimensions** combining live Harmonic data,
portable placeholder files (Pitchbook, LAVCA, Crunchbase), and web search.

Each dimension maps to a specific source. The skill manages the data collection
workflow so every session picks up exactly where the previous left off.

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

Then run status to surface what needs action:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py --action status
```

Surface to the user:
- Total companies in pipeline, how many are scored vs pending
- For each pending company: which variable groups are missing
- Recommended next source to hit (priority: Harmonic → Placeholder files → Web search)

---

## Step 2: Source routing — which source for which variable

| Variable group | Source | Live / Placeholder | Daily limit |
|---|---|---|---|
| Headcount, HC growth 90/180/365d | Harmonic MCP | **Live** | 10 calls/day |
| LinkedIn followers | Harmonic MCP | **Live** | — |
| Leadership 'prior experiences' field | Harmonic MCP | **Live** | — |
| Funding raised, last round, stage | `inputs/company_inputs.json` | Placeholder | — |
| Year founded, country, sector | `inputs/company_inputs.json` | Placeholder | — |
| Tier 1 investor check | `inputs/company_inputs.json` + `data/tier1_investors_reference.json` | Placeholder + constants | — |
| Sector phase 2025 | `data/sector_phases_reference.json` + `inputs/company_inputs.json` | Constants + placeholder | — |
| Sector CAGR, Time-to-Liquidity | Built-in constants (script) | Constants | — |
| Sectorial growth (EDGAR) | `edgar_trends` on public comps in same sector | **Live** (EDGAR) | None |
| Sector market liquidity (EDGAR) | `edgar_trends` on sector comparables | **Live** (EDGAR) | None |
| Proxy Revenue, Fwd 12m, Capital Efficiency, Fundamental Value | Computed from above | Computed | — |
| Big Tech / LatAm Unicorn / Top VC / Public Co experience | Harmonic 'prior experiences' → parse against `data/tier1_investors_reference.json` | **Live** | — |
| Reputation summary | Web search | **Live** | — |
| Legal flag | Web search | **Live** | — |
| Leadership pedigree & CFO track record | Harmonic 'prior experiences' + web search | **Live** | — |

**Harmonic 10-call/day limit:** prioritize companies with the most missing variables.
Each call to `get_companies` or `get_people` counts as 1 call.

---

## Step 3: Variable registry — all 29 dimensions

### Group A — Financial / Proxy (computed from HC + constants)
| # | Variable | Formula | Confidence |
|---|---|---|---|
| 1 | `proxy_revenue_usd` | HC × RPE_sector × stage_mult | 0.65 |
| 2 | `proxy_fwd_12m_usd` | proxy × (1 + sector_CAGR) | 0.60 |
| 3 | `capital_efficiency` | proxy / funding_raised | 0.65 |
| 4 | `fundamental_value_usd` | proxy × EV/Rev_sector | 0.60 |

**RPE constants (built into script — v3.2):**
- AIML/Space: $250k/HC | SaaS: $220k | FinTech: $130k | HealthTech: $160k
- E-Commerce: $55k | Marketplace: $70k | Logistics: $80k | CleanTech: $120k

**Stage multipliers:** Pre-Seed 0.4 · Seed 0.6 · A 0.8 · B 0.95 · C 1.0 · D 1.05 · E+ 1.1 · Pre-IPO 1.25

**EV/Revenue (Damodaran Jan 2026):**
- AIML: 18× | SaaS: 8.5× | FinTech: 5× | HealthTech: 6× | E-Commerce: 2.5× | Logistics: 2×

### Group B — Funding / Stage (placeholder: Crunchbase / Pitchbook)
| # | Variable | Source | Confidence |
|---|---|---|---|
| 5 | `funding_raised_usd` | `company_inputs.json` | 0.90 |
| 6 | `last_round_usd` | `company_inputs.json` | 0.90 |
| 7 | `last_round_date` | `company_inputs.json` | 0.90 |
| 8 | `stage` | `company_inputs.json` | 0.90 |

### Group C — Traction (Harmonic MCP — live)
| # | Variable | Harmonic field | Confidence |
|---|---|---|---|
| 9 | `headcount` | `headcount` | 0.90 |
| 10 | `hc_growth_90d_pct` | `headcount_growth_90_days` | 0.85 |
| 11 | `hc_growth_180d_pct` | `headcount_growth_180_days` | 0.85 |
| 12 | `hc_growth_365d_pct` | `headcount_growth_365_days` | 0.85 |
| 13 | `linkedin_followers` | `linkedin_follower_count` | 0.80 |

Call pattern: `get_companies` with company name → extract traction fields.

### Group D — Temporal (computed)
| # | Variable | Formula | Confidence |
|---|---|---|---|
| 14 | `year_founded` | from `company_inputs.json` | 0.95 |
| 15 | `age_years` | 2026 − year_founded | 0.95 |
| 16 | `funding_recency_mo` | −(months since last_round_date) | 0.90 |
| 17 | `time_to_liquidity_mo` | lookup by stage: Pre-IPO=−18, G+=−30, F=−36, E=−48, D=−60, C=−84 | 0.80 |

### Group E — Benchmarks (constants + EDGAR + computed)
| # | Variable | Source | Confidence |
|---|---|---|---|
| 18 | `sector_cagr` | Built-in constants | 0.85 |
| 19 | `sector_growth_edgar` | `edgar_trends` on 3 public sector comps | 0.90 |
| 20 | `sector_phase_2025` | `sector_phases_reference.json` + `company_inputs.json` | 0.80 |
| 21 | `sector_market_liquidity` | EDGAR: EV/Rev trend for sector comps last 3yr | 0.85 |
| 22 | `vs_public_sector_p50` | proxy / median public sector revenue | 0.75 |
| 23 | `vs_cohort` | proxy / median of all companies in pipeline with same sector | 0.75 |

For `sector_growth_edgar` and `sector_market_liquidity`: use `edgar_trends` on 2-3
representative public companies in the same sector and region. Extract revenue CAGR
and EV/Revenue trend. No daily limit on EDGAR.

### Group F — Qualitative Binary (Harmonic + reference lists)
| # | Variable | Method | Confidence |
|---|---|---|---|
| 24 | `tier1_investor` | Check investors in `company_inputs.json` against `tier1_investors_reference.json` | 0.90 |
| 25 | `big_tech_experience` | Parse Harmonic 'prior experiences' → match `big_tech_companies` list | 0.85 |
| 26 | `latam_unicorn_experience` | Parse Harmonic 'prior experiences' → match `latam_unicorns` list | 0.85 |
| 27 | `top_vc_experience` | Parse Harmonic 'prior experiences' → match `global_tier1` or `latam_tier1` lists | 0.85 |
| 28 | `public_co_experience` | Parse Harmonic 'prior experiences' → match `public_cos_latam_relevant` | 0.85 |

**How to parse 'prior experiences':** Pull `founders` and `leadership` from Harmonic.
For each person, read their work history. Check each employer name (case-insensitive
substring) against the reference lists in `data/tier1_investors_reference.json`.
Set the binary = `true` if ANY founder or C-suite exec matches.

### Group G — Qualitative Open (Web search + Harmonic)
| # | Variable | Source | Confidence |
|---|---|---|---|
| 29 | `reputation_summary` | Web search: "[Company] review site trust controversy" | 0.70 |
| 30 | `legal_flag` | Web search: "[Company] lawsuit regulatory SEC fine" | 0.75 |
| 31 | `leadership_pedigree` | Harmonic founders/CEO bio + web search for depth | 0.75 |

**Confidence floor: 0.75.** Variables below this threshold are recorded as `N/A`, not scored.
`proxy_revenue_usd` (0.65) and all computed proxies are always recorded as estimates, never
treated as verified revenue. `reputation_summary` (0.70) is recorded as a qualitative note.

---

## Step 4: Scoring operations

### Add companies to pipeline
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action add \
  --companies '[
    {"name":"Neon","sector":"FinTech","stage":"Series D","region":"LatAm","country":"Brazil"},
    {"name":"Kavak","sector":"Marketplace","stage":"Series G+","region":"LatAm","country":"Mexico"}
  ]'
```

### Record variable data for a company
After pulling from Harmonic, placeholders, and web search, record all in one call:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action record \
  --company "Neon" \
  --data '{
    "headcount": 2800,
    "hc_growth_90d_pct": 4.2,
    "hc_growth_180d_pct": 9.1,
    "hc_growth_365d_pct": 22.0,
    "linkedin_followers": 45000,
    "funding_raised_usd": 900000000,
    "last_round_usd": 300000000,
    "last_round_date": "2022-06",
    "stage": "Series D",
    "year_founded": 2018,
    "tier1_investor": true,
    "big_tech_experience": false,
    "latam_unicorn_experience": true,
    "top_vc_experience": true,
    "public_co_experience": false,
    "reputation_summary": "Strong NPS, no major controversies, regulated by Banco Central do Brasil",
    "legal_flag": false,
    "leadership_pedigree": "CEO David Vélez — Stanford MBA, Sequoia partner. CTO Edward Wible — Princeton CS."
  }'
```

The script auto-computes: `proxy_revenue_usd`, `proxy_fwd_12m_usd`, `capital_efficiency`,
`fundamental_value_usd`, `age_years`, `funding_recency_mo`, `time_to_liquidity_mo`, `sector_cagr`.

### Compute and save score snapshot
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action score --company "Neon"
```

### Export full scorecard (for reporting)
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py \
  --action export --company "Neon"
```

---

## Step 5: Scoring workflow — execution sequence per company

Run in this order to minimize Harmonic calls:

### Phase 1 — Placeholder data (0 API calls)
1. Read `${NAZCA_FACTORY_DIR:-$HOME/Factory}/private-scoring/inputs/company_inputs.json`
2. Extract: `funding_raised_usd`, `last_round_usd`, `last_round_date`, `stage`,
   `year_founded`, `tier1_investor`, `sector_phase_2025_lavca`, `sector_phase_2025_pitchbook`
3. Check `data/tier1_investors_reference.json` to validate tier1_investor claim
4. Read `data/sector_phases_reference.json` for sector phase if not in company_inputs

### Phase 2 — Harmonic MCP (counts against 10-call/day limit)
5. Call `get_companies` with company name → extract traction metrics
6. Parse `headcount`, `hc_growth_90d_pct`, `hc_growth_180d_pct`, `hc_growth_365d_pct`,
   `linkedin_followers`
7. Call `get_people` for founders + CEO → extract 'prior experiences' work history
8. Parse prior experiences against reference lists → set binary variables 25–28

**One company = 2 Harmonic calls.** With 10-call/day limit: max 5 companies/day.

### Phase 3 — EDGAR (no daily limit)
9. Identify 2–3 public companies in the same sector+region
10. Call `edgar_trends` on each → extract revenue CAGR and gross margin trends
11. Compute `sector_growth_edgar` (average CAGR across comps)
12. Compute `sector_market_liquidity` (trend in EV/Rev multiples, qualitative: expanding/contracting/stable)

### Phase 4 — Web search (no limit)
13. Search "[Company name] reputation review trust"
    → write 1–2 sentence `reputation_summary`
14. Search "[Company name] lawsuit regulatory fine penalty"
    → set `legal_flag`: true/false + brief note
15. Search "[CEO name] [Company] background" for leadership depth
    → supplement Harmonic bio with external context

### Phase 5 — Record and score
16. Run `--action record` with all collected data
17. Run `--action score` to compute derived metrics and save snapshot

---

## Step 6: Session end — always do this

After scoring any companies, update the state:
```bash
python3 ~/.claude/skills/nazca-private-scoring/scripts/private_score_manager.py --action update-state
```

Then give the user a summary:
- Companies scored this session
- Companies remaining (and what's blocking each)
- Harmonic calls used today (reminder of daily limit)

---

## Placeholder files (do not hardcode — read from disk)

These files live in `${NAZCA_FACTORY_DIR:-$HOME/Factory}/private-scoring/inputs/`.
They are **not in this repo** — they contain live deal data and must be filled by
each team member from their Pitchbook/LAVCA/Crunchbase exports.

| File | Purpose |
|---|---|
| `company_inputs.json` | Funding, stage, year founded, investors — from Crunchbase/Pitchbook |
| `rpe_overrides.json` | Custom RPE values if OLS calibration differs from defaults |

**Reference data** (ships with the skill — update each quarter):

| File | Purpose |
|---|---|
| `data/sector_phases_reference.json` | LAVCA + Pitchbook sector phase by region |
| `data/tier1_investors_reference.json` | Tier 1 investor lists, tech company lists for pedigree parsing |

---

## File layout

```
~/Factory/private-scoring/   (or $NAZCA_FACTORY_DIR/private-scoring/)
  state.json                           ← pipeline state (all companies, statuses)
  inputs/
    company_inputs.json                ← Pitchbook/LAVCA/Crunchbase data (fill manually)
    rpe_overrides.json                 ← custom RPE calibration (optional)
  scores/
    neon.json                          ← per-company variable data + score snapshot
    kavak.json
    ...
```
