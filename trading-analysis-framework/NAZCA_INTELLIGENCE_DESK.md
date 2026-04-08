# Nazca Intelligence Desk

**Status:** Stage 1 — Team Ready  
**Last updated:** April 8, 2026  
**Engine:** TauricResearch TradingAgents library (LangGraph)  
**UI:** Streamlit + ngrok (Stage 1) → FastAPI + Claude MCP (Stage 3)

---

## What It Is

An on-demand, composable multi-agent investment research tool that produces investment-grade analysis for any public ticker, ETF, or sector. Built for Nazca's Data Science and Investment teams.

**Not a trading bot.** An analyst tool that augments and challenges human investment judgment.

---

## Primary Use Case

> Adolfo (leading partner) needs to evaluate semiconductor companies for a $2M position. He runs a comparative analysis on NVDA, TSMC, and AMD — the system produces analyst reports, a research debate, a trading plan, risk assessments, and a final BUY/HOLD/SELL per company. Adolfo exports the full report and presents to the investment committee.

---

## User Stories

| # | User | Story |
|---|------|-------|
| 1 | Investment Partner | Sector sweep: compare multiple tickers → allocate capital across best opportunities |
| 2 | Investment Analyst | Single ticker deep dive → export investment brief for internal review |
| 3 | Data Scientist | Invoke one or two specific agents for a targeted, fast answer |
| 4 | Investment Analyst | Submit a thesis → bear agent challenges it in Claude chat (Stage 3) |
| 5 | Investment Analyst | Analyze a portco using Aurora/RDS KPI data with the same agent pipeline (Stage 3) |

---

## Agent Pipeline

```
4 Analysts (parallel)          → run concurrently per ticker
  ├── Fundamentals Analyst
  ├── Market / Technical Analyst
  ├── News Analyst
  └── Social/Sentiment Analyst
       ↓
3 Researchers (sequential)     → bull vs bear debate
  ├── Bull Researcher
  ├── Bear Researcher
  └── Research Manager (judge)
       ↓
Trader Agent                   → position sizing and entry/exit plan
       ↓
3 Risk Managers (parallel)     → risk debate
  ├── Aggressive
  ├── Neutral
  └── Conservative
       ↓
Portfolio Manager              → final BUY / HOLD / SELL decision
```

---

## Product Stages

### Stage 1 — Team Ready (✅ Complete, April 8, 2026)

**What changed:**
- Multi-ticker input (comma-separated: `NVDA, TSMC, AMD`)
- Sequential execution with live progress bar per ticker
- Comparison summary view: BUY/HOLD/SELL card per ticker at a glance
- Per-ticker full results in tabs
- Download Report button — exports complete analysis as `.md` file

**How to run:**
```bash
cd /Users/dannazca/Factory/TradingAgents_Demo
streamlit run streamlit_app.py
# expose via ngrok: ngrok http 8501
```

**Branch:** `nazca-ui` in TradingAgents_Demo  
**Rollback:** `git checkout main -- streamlit_app.py`

---

### Stage 2 — Composable (Upcoming — next sprint)

- Route through FastAPI bridge (auth, RBAC, job tracking, history)
- Individual agent invocation via API
- ETF and sector sweep as named presets
- Results persisted — retrievable by job ID
- Proper stable URL (no ngrok dependency)

---

### Stage 3 — Claude + Aurora (Following sprint)

- Claude MCP tool: Adolfo asks in Claude chat → agents run → results return in conversation
- Thesis challenge: user pastes investment thesis → bear researcher debates it conversationally
- Slack command: `/analyze NVDA TSMC AMD`
- Aurora/RDS connection: load portco KPIs from Nazca's data warehouse into agent context

---

## Architecture

```
Stage 1 (now)              Stage 2                    Stage 3
──────────────────         ──────────────────────     ──────────────────────────
Streamlit (local)    →     FastAPI Bridge        →    Claude MCP Tool
ngrok (temporary)          Auth + RBAC                Conversational interface
TauricResearch lib         Job tracking + history     Slack /analyze command
                           Stable URL                 Aurora/RDS portco data
```

**Execution engine throughout all stages:** TauricResearch `TradingAgentsGraph` library.  
**FastAPI custom orchestrator** (`trading_orchestrator.py`) is maintained as a lightweight fallback — not used for Intelligence Desk.

---

## Fallback / Rollback

The `nazca-ui` branch contains all Nazca-specific changes to `streamlit_app.py`.

```bash
# To roll back to original MVP at any time:
git -C /Users/dannazca/Factory/TradingAgents_Demo checkout main -- streamlit_app.py

# To see what changed:
git -C /Users/dannazca/Factory/TradingAgents_Demo diff main nazca-ui -- streamlit_app.py
```

---

## Related Documents

- `FastAPI_Bridge_PRD.md` — FastAPI gateway architecture (Stage 2 integration)
- `TraddingAgentsDirectory.md` — Agent prompt directory
- `TradingAgents.md` — Framework overview
- `SKILL.md` — Claude skill definition for the macro-orchestrator
- `/Users/dannazca/Factory/dannazca-skills/governance/Nazca_Technical_Specification_v2.md` — System architecture
