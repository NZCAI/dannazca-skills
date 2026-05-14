# Variable Registry — nazca-private-scoring

Full source priority, confidence rules, and edge cases for all 29+ scoring dimensions.

---

## Confidence tiers

| Tier | Range | Meaning |
|---|---|---|
| Verified | 0.90–1.00 | Primary source, no transformation |
| High | 0.80–0.89 | One transformation or one assumption |
| Medium | 0.75–0.79 | Two transformations or indirect source |
| Below floor | < 0.75 | Recorded as **N/A** (not as a score) |

**Confidence floor: 0.75.** Variables below this are stored as qualitative notes, never used in quantitative comparisons.

---

## Group A — Financial / Proxy

### `proxy_revenue_usd`
- **Formula:** HC × RPE_sector × stage_mult
- **Confidence:** 0.65 → recorded as *estimate*, never as verified revenue
- **Edge cases:**
  - HC from Harmonic lags 30–60 days — state this explicitly when reporting
  - If company has multiple business lines, use primary sector RPE
  - For holding companies or conglomerates: not applicable, record N/A

### `proxy_fwd_12m_usd`
- **Formula:** proxy_revenue_usd × (1 + sector_CAGR)
- **Confidence:** 0.60 — compound of two low-confidence inputs
- **Note:** Use only as directional indicator, not valuation anchor

### `capital_efficiency`
- **Formula:** proxy_revenue_usd / funding_raised_usd
- **Healthy range:** 0.5–1.0 (SaaS benchmark). Above 1.0 = excellent. Below 0.3 = concern.
- **Confidence:** 0.65 (limited by proxy revenue)

### `fundamental_value_usd`
- **Formula:** proxy_revenue_usd × EV_revenue_multiple
- **Confidence:** 0.60
- **Note:** Use Damodaran sector multiple adjusted for LatAm/region discount if applicable

---

## Group B — Funding / Stage

### `funding_raised_usd`
- **Source:** Crunchbase export in `company_inputs.json`
- **Confidence:** 0.90 for US companies, 0.80 for LatAm (Crunchbase coverage gaps)
- **Edge case:** Some rounds are not disclosed — record what's available, note "may be understated"

### `last_round_usd` / `last_round_date`
- **Source:** `company_inputs.json`
- **Confidence:** 0.90 if from Crunchbase/Pitchbook, 0.75 if from press release only

### `stage`
- **Source:** `company_inputs.json`
- **Confidence:** 0.90 if from Pitchbook, 0.80 if inferred from round size
- **Round → Stage mapping:** <$2M=Pre-Seed, $2-15M=Seed, $15-50M=A, $50-150M=B, $150-400M=C, $400M+=D+

---

## Group C — Traction (Harmonic)

### `headcount`
- **Source:** Harmonic `get_companies` → `headcount` field
- **Confidence:** 0.90
- **Edge case:** Harmonic counts LinkedIn profiles, not official headcount. May include contractors.
  Divide by 1.1 if company is known to use heavy contractor base.

### `hc_growth_90d_pct` / `hc_growth_180d_pct` / `hc_growth_365d_pct`
- **Source:** Harmonic `headcount_growth_{N}_days`
- **Confidence:** 0.85
- **Interpretation:**
  - 90d > 5%: strong momentum
  - 90d < 0%: contraction signal (verify before flagging)
  - 365d > 30%: hypergrowth
  - 365d < 5%: stagnation (context-dependent for late-stage)

### `linkedin_followers`
- **Source:** Harmonic `linkedin_follower_count`
- **Confidence:** 0.80
- **Use:** Signal for brand strength, not a scoring variable on its own

---

## Group D — Temporal

### `age_years`
- **Formula:** 2026 − year_founded
- **Confidence:** 0.95
- **Interpretation by stage:** Series B at age < 3 = fast; age > 8 = slow relative to stage

### `funding_recency_mo`
- **Formula:** −(months since last_round_date). Negative = months ago.
- **Confidence:** 0.90
- **Signal:** < −18 months with no new round = runway risk flag (check cash position)

### `time_to_liquidity_mo`
- **Source:** Built-in stage lookup. Negative = months to expected IPO/exit.
- **Confidence:** 0.80
- **Table:** Pre-IPO=−18, G+=−30, F=−36, E=−48, D=−60, C=−84, B=−108, A=−132, Seed=−156

---

## Group E — Benchmarks

### `sector_cagr`
- **Source:** Built-in constants (calibrated from EDGAR public comps, updated annually)
- **Confidence:** 0.85

### `sector_growth_edgar`
- **Source:** `edgar_trends` on 2–3 public sector comparables
- **Confidence:** 0.90
- **Method:** Pull 3-year revenue time series → compute CAGR → average across 2–3 comps
- **Preferred comps by sector:**
  - FinTech/LatAm: NU, StoneCo, DLocal
  - SaaS: pick from Publicas_GUR cohort matching sector
  - HealthTech: use HALLAZGOS_PUBLICAS benchmark

### `sector_market_liquidity`
- **Source:** EDGAR trends on sector EV/Revenue multiples
- **Confidence:** 0.85
- **Output:** Qualitative: "expanding" / "stable" / "contracting" + 1-sentence rationale
- **Method:** Compare current Damodaran multiple vs 2yr ago for same sector

### `sector_phase_2025`
- **Source:** `data/sector_phases_reference.json` (primary) + `company_inputs.json` (override)
- **Confidence:** 0.80
- **Values:** Early / Growth / Late / Mature

### `vs_public_sector_p50`
- **Formula:** proxy_revenue_usd / median_public_sector_revenue
- **Source:** HALLAZGOS_PUBLICAS benchmark for sector median
- **Confidence:** 0.75 (limited by proxy confidence)
- **Interpretation:** > 1.0 = above median, < 0.3 = very early stage

### `vs_cohort`
- **Formula:** proxy_revenue_usd / median(pipeline companies in same sector)
- **Confidence:** 0.75
- **Note:** Only meaningful when ≥ 3 companies in same sector are scored

---

## Group F — Qualitative Binary

### `tier1_investor`
- **Source:** `company_inputs.json` investor list → match against `data/tier1_investors_reference.json`
- **Confidence:** 0.90
- **Rule:** True if ANY lead investor (not just participant) appears in the tier1 lists
- **LatAm note:** Include both `global_tier1` and `latam_tier1` lists

### `big_tech_experience`
- **Source:** Harmonic founders + leadership 'prior experiences' → parse against `big_tech_companies` list
- **Confidence:** 0.85
- **Rule:** True if ANY founder or C-suite exec (CEO, CTO, CPO, CFO) spent ≥1 year at a Big Tech company
- **Do not count:** internships, consulting gigs, or vendor relationships

### `latam_unicorn_experience`
- **Source:** Harmonic prior experiences → `latam_unicorns` list
- **Confidence:** 0.85
- **Rule:** True if any founder/exec was employee #1–500 OR a director/VP+ at a LatAm unicorn

### `top_vc_experience`
- **Source:** Harmonic prior experiences → `global_tier1` or `latam_tier1` lists
- **Confidence:** 0.85
- **Rule:** True if any founder was a Partner, Principal, or Analyst at a Tier 1 VC

### `public_co_experience`
- **Source:** Harmonic prior experiences → `public_cos_latam_relevant` list
- **Confidence:** 0.85
- **Rule:** True if CFO or CEO previously held a VP/Director+ role at a public company

---

## Group G — Qualitative Open

### `reputation_summary`
- **Source:** Web search
- **Confidence:** 0.70 → always recorded as qualitative note, never numeric
- **Search query:** `"[Company name]" site:trustpilot.com OR site:glassdoor.com OR "controversy" OR "complaint"`
- **Output format:** 1–2 sentences. Example: "Strong Glassdoor rating (4.2/5), no public controversies. Regulated by Banco Central do Brasil."

### `legal_flag`
- **Source:** Web search
- **Confidence:** 0.75
- **Search query:** `"[Company name]" lawsuit OR "regulatory action" OR "SEC" OR "fine" OR "penalty" site:reuters.com OR site:ft.com OR site:wsj.com`
- **Rule:** True = any active or resolved regulatory action or material lawsuit. Add brief note.
- **False ≠ clear** — means no public record found, not that no issues exist

### `leadership_pedigree`
- **Source:** Harmonic founder/CEO bio + web search
- **Confidence:** 0.75
- **Output:** 2–4 sentence narrative. Include: founder background, relevant exits or scale experience, CFO's public company or later-stage experience, any board member strength.
- **For CFO track record:** specifically note if CFO has led an IPO or Series D+ fundraise before.

---

## Data source availability

| Source | Access method | Requires setup |
|---|---|---|
| Harmonic | MCP tool (configured in Claude Code) | Yes — Harmonic MCP must be configured |
| EDGAR | MCP tool (edgartools) | Yes — EDGAR MCP must be configured |
| Crunchbase/Pitchbook | `inputs/company_inputs.json` (manual export) | Fill file manually |
| LAVCA | `data/sector_phases_reference.json` (shipped, update quarterly) | None |
| Web search | Claude web search | None |
| Constants | Built into `private_score_manager.py` | None |
