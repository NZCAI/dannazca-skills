# Variable Registry — Nazca Enrichment Pipeline

Full source-priority rules, confidence logic, and derivation formulas for every variable
tracked across cohorts. The compact table in SKILL.md is the working reference; this file
is the authoritative spec for edge cases and cross-source decisions.

---

## Table of Contents

1. [Confidence Rules](#1-confidence-rules)
2. [Financial Variables — EDGAR](#2-financial-variables--edgar)
3. [Valuation Variables — Damodaran](#3-valuation-variables--damodaran)
4. [Rules-Based Scores](#4-rules-based-scores)
5. [Traction Variables — Harmonic](#5-traction-variables--harmonic)
6. [OLS Revenue Estimate — Private Companies](#6-ols-revenue-estimate--private-companies)
7. [Currency Normalization](#7-currency-normalization)
8. [IFRS vs GAAP Gaps](#8-ifrs-vs-gaap-gaps)
9. [Data Quality Flags](#9-data-quality-flags)

---

## 1. Confidence Rules

**Floor: 0.75.** Any variable with confidence < 0.75 is recorded as `N/A`, not as a score.
`N/A` means no verifiable data — it does NOT penalize the company. N/A values are excluded
from comparisons that require the variable.

| Confidence band | Meaning |
|---|---|
| 1.00 | Direct from primary filing (EDGAR XBRL, no transformation) |
| 0.90–0.99 | Primary source with one derivation step (ratio from two EDGAR fields) |
| 0.80–0.89 | Primary source with an additional assumption (Damodaran sector table, etc.) |
| 0.75–0.79 | Rules-based from validated constant (sector CAGR, jurisdiction map) |
| < 0.75 | Record as N/A — do not score |

---

## 2. Financial Variables — EDGAR

**Source:** `mcp__edgartools__edgar_trends`  
**Single call per company (most efficient):**
```
concepts: ["revenue","gross_profit","operating_income","net_income",
           "total_assets","total_liabilities","equity"]
period: "annual", periods: 3
```

| Variable | Confidence | Source | Notes |
|---|---|---|---|
| `revenue_usd` | 1.00 (EDGAR) / 0.65 (OLS) | EDGAR or OLS fallback | OLS is below floor — flagged |
| `gross_profit_usd` | 1.00 | EDGAR | Often available even for IFRS filers |
| `gross_margin_pct` | 0.95 | derived: gross_profit / revenue_denominator | Use source_revenue when EDGAR revenue is anomalous |
| `operating_income_usd` | 1.00 | EDGAR | **N/A for IFRS 20-F — expected, not an error** |
| `operating_margin_pct` | 0.95 | derived | N/A when operating_income is N/A |
| `net_income_usd` | 0.90 | EDGAR | Often N/A for both GAAP and IFRS |
| `net_margin_pct` | 0.90 | derived | N/A when net_income is N/A |
| `total_assets_usd` | 1.00 | EDGAR | Reliable for all filer types |
| `total_liabilities_usd` | 1.00 | EDGAR | Reliable for all filer types |
| `debt_ratio` | 0.95 | derived: total_liabilities / total_assets | See IFRS bug note below |

**Known edge cases:**
- **CRWD, SNOW, DDOG revenue anomaly:** `edgar_trends` returns RPO or partial-period value. Use `source_revenue` from original Excel as the margin denominator. Set flag `"EDGAR revenue anomaly — using source_revenue as denominator"`.
- **SOUN, PL assets=liabilities bug:** edgartools IFRS mapping returns the same XBRL tag for both fields. Record `debt_ratio` as N/A, set flag `"assets=liabilities anomaly — debt_ratio unreliable"`.
- **FY offset (CHWY, PATH, CHPT, PL):** Jan/Apr fiscal year end — EDGAR returns FY2025=CY2024. Data is correct; note the offset.

---

## 3. Valuation Variables — Damodaran

Source: Damodaran Jan 2026 dataset, sector × region tables. **No API call needed.**

### ev_revenue_multiple — Confidence: 0.85

| Sector | US / Global | LatAm / EM |
|---|---|---|
| SaaS | 11.4× | 8.0× |
| AIML | 11.4× | 8.0× |
| FinTech | 6.5× | 4.5× |
| HealthTech | 5.3× | 3.7× |
| CleanTech | 7.9× | 5.5× |
| Space | 3.6× | 2.5× |
| E-Commerce | 2.1× | 1.5× |
| EdTech | 2.0× | 1.4× |
| Logistics | 1.7× | 1.2× |
| PropTech | 0.8× | 0.6× |

Apply US/Global for US-listed domestic companies; LatAm/EM for foreign private issuers.

### revenue_cagr_2yr — Confidence: 0.90

- **Source:** EDGAR trends — computed across 3 annual periods
- **Formula:** `(revenue_year_n / revenue_year_n-2) ^ 0.5 − 1`

---

## 4. Rules-Based Scores

No API call required. Compute deterministically from known fields.

### jurisdiction_risk_score (1–10) — Confidence: 0.80

Higher = lower risk.

| Region / Country | Score |
|---|---|
| US | 8 |
| Global (multi-jurisdiction HQ) | 7 |
| LatAm (Brazil, Mexico, Colombia, Chile, Argentina…) | 5 |
| EM excluding LatAm / China | 4 |

### pricing_power_score (1–10) — Confidence: 0.80

Requires `gross_margin_pct`. If N/A → pricing_power_score = N/A.

| Gross margin | Score | Rationale |
|---|---|---|
| > 70% | 9 | Strong software / platform economics |
| 50–70% | 7 | Above-average pricing power |
| 30–50% | 5 | Moderate — typical services/marketplace |
| 15–30% | 3 | Limited — thin margin business |
| < 15% | 1 | Commodity / price-taker |

### sector_growth_cagr — Confidence: 0.85

| Sector | CAGR |
|---|---|
| AIML | 45% |
| Space | 45% |
| SaaS | 23% |
| E-Commerce | 21% |
| HealthTech | 13.5% |
| FinTech | 9% |
| EdTech | 9% |
| CleanTech | 8.5% |
| Logistics | 2.4% |
| PropTech | −15% |

### capital_efficiency_score (1–10) — Confidence: 0.85

- **Formula:** `raw = revenue_usd / total_assets_usd`
- **Ranking:** percentile **within cohort** (not global)
- **Mapping:** Q4 ≥75th pct → 9, Q3 50–75th → 7, Q2 25–50th → 5, Q1 <25th → 3
- **Important:** Compute only after all companies in the cohort have both fields. This is a cohort-relative score — do not compute per company in isolation.

---

## 5. Traction Variables — Harmonic

Applies to **private companies only**. Public companies use EDGAR financials instead.

**Daily limit:** `web_social_headcount_timeseries` = 10 calls/day. Budget carefully.

| Variable | Confidence | Notes |
|---|---|---|
| `hc_momentum_90d` | 0.85 | Headcount % change over 90-day window |
| `web_traffic_90d` | **0.72** | **Below floor → always record as N/A** |
| `linkedin_growth_180d` | 0.80 | LinkedIn follower % change over 180-day window |

`web_traffic_90d` is tracked but never scored — use only for directional signal in analyst notes.

---

## 6. OLS Revenue Estimate — Private Companies

Used only when: no EDGAR filing AND Harmonic headcount is available.  
**Confidence: 0.65** — below the 0.75 floor. Do not use as an individual company score.
Acceptable as a cohort-level aggregate where uncertainty averages down.

**Formula:**
```
log(revenue_usd) = 13.43
  + 0.8605 × log(headcount)
  + 0.2152 × log(company_age_years)
  + β_sector
  + β_region × stage_discount
```

**Sector betas (β_sector):**

| Sector | β |
|---|---|
| SaaS | +0.41 |
| AIML | +0.35 |
| Space | +0.28 |
| FinTech | +0.22 |
| HealthTech | +0.18 |
| E-Commerce | +0.09 |
| EdTech | +0.05 |
| Logistics | −0.04 |
| CleanTech | −0.11 |

**Region betas (β_region):** US = 0 (baseline), LatAm = −0.31, EM (non-LatAm) = −0.44

**Stage multipliers:** Pre-A × 0.55 · Series A × 0.75 · Series B × 0.90 · Series C+ × 1.00

---

## 7. Currency Normalization

EDGAR reports in the company's reporting currency. Auto-detection applies when
`source_revenue` (USD-validated, from Excel or Harmonic) is available.

**Detection logic:**
1. Compute `ratio = edgar_revenue / source_revenue`
2. Apply rule:

| Ratio range | Inferred currency | Action |
|---|---|---|
| 4.5 – 7.0 | BRL (Brazilian Real) | Divide all EDGAR monetary fields by `ratio` |
| 6.5 – 8.5 | CNY (Chinese Yuan) | Divide all EDGAR monetary fields by `ratio` |
| 700 – 950 | CLP (Chilean Peso) | **Flag only — do NOT auto-divide** (outside safe band) |
| ~1.0 | USD | No action |

When normalizing, divide: `gross_profit`, `operating_income`, `net_income`,
`total_assets`, `total_liabilities`, `equity`.  
Set `data_quality_flag = f"Currency normalized: BRL→USD (÷{ratio:.2f})"`.

---

## 8. IFRS vs GAAP Gaps

Most LatAm and Chinese public companies listed on US exchanges file as **foreign private
issuers** using IFRS (Form 20-F, not 10-K).

| EDGAR field | GAAP 10-K | IFRS 20-F |
|---|---|---|
| `revenue` | ✓ reliable | ✓ reliable |
| `gross_profit` | ✓ reliable | ✓ usually available |
| `operating_income` | ✓ reliable | ✗ returns null — **expected, not an error** |
| `net_income` | ✓ often available | ✗ returns null — **expected, not an error** |
| `total_assets` | ✓ reliable | ✓ reliable |
| `total_liabilities` | ✓ reliable | ✓ reliable |

When `operating_income` or `net_income` is null for a known 20-F filer: record N/A and
move on. Do not attempt to derive from other fields or flag as a data failure.

---

## 9. Data Quality Flags

One flag per company (most critical wins). Priority order: currency > EDGAR anomaly > EDGAR miss > FY offset.

| Flag value | Meaning |
|---|---|
| `""` / `null` | Clean — no issues |
| `"Currency normalized: BRL→USD (÷X.XX)"` | FX normalization applied, BRL |
| `"Currency normalized: CNY→USD (÷X.XX)"` | FX normalization applied, CNY |
| `"CLP reporter — verify FX"` | Chilean Peso detected, NOT normalized |
| `"EDGAR revenue anomaly — using source_revenue as denominator"` | XBRL mismatch; margins still valid |
| `"assets=liabilities anomaly — debt_ratio unreliable"` | IFRS XBRL bug; exclude debt_ratio |
| `"FY offset: FY2025=CY2024"` | Non-calendar fiscal year; data is correct |
| `"EDGAR miss — all fields N/A"` | Complete EDGAR failure; retry next session |
