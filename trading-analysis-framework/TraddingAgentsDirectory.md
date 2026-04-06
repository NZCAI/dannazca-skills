# Trading Analysis Framework

This directory contains the central prompt repository and orchestration logic for Nazca's multi-agent financial trading analysis framework. 

## Overview
This framework uses a collection of specialized LLM agents (Analysts, Researchers, Traders, Risk Managers) to collaboratively evaluate market conditions, debate strategies, and inform trading decisions. 

## Repository Structure

* `SKILL.md`: Factory-level documentation defining when and how this framework is invoked by the macro-orchestrator.
* `TradingAgents.md`: The master orchestration guide that outlines the team structure and how the agents interact with each other.
* `prompts/`: A directory containing the individual system prompts for each sub-agent in the LangGraph backend. By keeping these prompts as markdown files, the technical team can version-control agent behavior without modifying the underlying Python API code.

## Integration
This framework is designed to be executed by the **Nazca FastAPI Bridge**. When a request (e.g., via n8n webhook) hits the `/analyze-ticker` endpoint, the FastAPI bridge will pull the prompts from this repository, inject them into the LangGraph micro-orchestrator, and execute the analysis.

## Recent Milestones (Streamlit Web UI & Ngrok Integration)
- **Configuration Hotfixes:** Resolved default dictionary and API key patching to support OpenAI "o"-series reasoning configurations gracefully.
- **Streamlit Web UI:** Developed a dynamic frontend interface allowing researchers to interact with the multi-agent system in a browser instead of the CLI.
- **Agent Selection Feature:** Introduced a multi-select component in the UI enabling users to pick specific analyst agents (Market, Social, News, Fundamentals) with descriptive markdown references.
- **Ngrok Tunneling:** Standardized a deployment process using Ngrok to expose the local Streamlit port securely to a public URL for broader stakeholder testing.
- **Documentation:** Updated the main repository `README.md` to reflect the new Streamlit capabilities and tunneling instructions.
