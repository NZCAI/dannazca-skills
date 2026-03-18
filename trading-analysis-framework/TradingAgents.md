# TradingAgents Orchestration

This document outlines the macro-level architecture and flow for the Trading Analysis Framework.

## 1. The Teams
The LangGraph backend orchestrates the following specialized agents. Their individual system prompts are stored in the `prompts/` directory.

### I. Analyst Team
- **Fundamentals Analyst**: Reviews financial statements and health.
- **Social Analyst**: Gauges public sentiment.
- **News Analyst**: Tracks macro and global events.
- **Technical/Market Analyst**: Examines momentum and charts.

### II. Research Team
- **Bull Researcher**: Argues the upside potential.
- **Bear Researcher**: Argues the downside risk.
- **Research Manager**: Synthesizes the debate into a single investment plan.

### III. Trading Team
- **Trader**: Consumes the investment plan and proposes specific entry/exit and position sizing.

### IV. Risk Management Team
- **Risk Analysts (Aggressive, Neutral, Conservative)**: Stress-test the Trader's proposal.
- **Portfolio Manager**: Makes the final definitive execution decision.
