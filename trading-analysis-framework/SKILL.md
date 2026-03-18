# Skill: Trading Analysis Framework

## Purpose
This skill orchestrates a multi-agent financial trading analysis framework. It utilizes specialized LLM agents (Analysts, Researchers, Traders, Risk Managers) to collaboratively evaluate market conditions, debate strategies, and inform trading decisions.

## When to use this skill
- When a comprehensive analysis of a specific stock ticker is required.
- To trigger the LangGraph trading analysis backend via the universal FastAPI bridge.
- When generating financial intelligence that requires fact-checking and risk assessment before trading.

## How it works (The Macro-to-Micro Bridge)
From the Factory/CLI side, this skill acts as a **Macro-Orchestrator**. It gathers the user's intent (Ticker, Date, Depth) and forwards it to the **Micro-Orchestrator** (LangGraph running in the FastAPI bridge). The prompts that govern the LangGraph agents are stored here and pulled dynamically.
