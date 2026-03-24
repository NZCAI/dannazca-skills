# Nazca Use Cases (Prompt Pack)

## 1) PE/VC Diligence Snapshot
“Using EdgarTools MCP, build a diligence snapshot for `{{TICKER}}` from latest 10-K/10-Q: business model, top risks, growth profile, margin trend, balance-sheet posture, and key open questions.”

## 2) Risk-Factor Delta
“Using EdgarTools MCP, compare risk factors across the latest two 10-K filings for `{{TICKER}}`; return added, removed, and materially changed items with short impact notes.”

## 3) Insider Activity Signal
“Using EdgarTools MCP, analyze Form 4 insider transactions for `{{TICKER}}` over the last 180 days; classify as bullish/bearish/neutral and highlight unusual clusters.”

## 4) Public Comps Grid
“Using EdgarTools MCP, compare `{{TICKER_A}}`, `{{TICKER_B}}`, and `{{TICKER_C}}` on revenue, net income, operating income, EPS, assets, liabilities, equity over last 12 quarters.”

## 5) Event Monitoring (8-K)
“Using EdgarTools MCP, monitor latest 8-K filings in `{{SECTOR}}`; classify each into M&A, leadership change, litigation/regulatory, financing, cybersecurity, and summarize implications.”

## 6) Follow-on Time-Series Extraction
“Using EdgarTools MCP + ai-data-analyst skill, extract the last 12 quarters for `{{TICKERS}}` with revenue/net_income/gross_profit/operating_income/eps/assets/liabilities/equity and output CSV+XLS.”

## 7) PM-Driven Diligence Plan
“Use product-management skill to define the diligence scope for `{{COMPANY}}`, then run EdgarTools MCP queries and produce a decision-ready memo with data provenance.”
