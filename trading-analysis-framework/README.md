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
