# Nazca Skills Repository (Factory.ai)

This repository contains the centralized AI agent skills and tools utilized by the Nazca technical team. It serves as the single source of truth for prompts, behaviors, and specialized utilities designed to run within the Factory.ai ecosystem and external interfaces like Claude Code.

## 🎯 Purpose
The goal of this repository is to eliminate "prompt sprawl" and ensure that all team members (from senior engineers to trainees) use the same, version-controlled instructions when leveraging AI for code generation, data analysis, and system architecture.

## 🛠 Available Skills & Everyday Use Cases

Think of these skills as "lenses" you can put on your AI. Depending on the task you are doing, invoking a specific skill forces the AI to behave according to Nazca's exact standards for that specific job.

### 1. `solid` (Code Quality & Architecture)
**What it does:** Forces the AI to write code like a Senior Software Engineer. It strictly enforces clean code, logical separation of concerns, and Test-Driven Development.
*   **When to use it:** When writing new Python functions, refactoring messy code, or building an API endpoint.
*   **Example Prompt:** *"I need a Python script to parse these CSVs. Please use the `solid` skill to ensure the architecture is clean and includes unit tests."*

### 2. `tracer-bullets` (Feature Development Strategy)
**What it does:** Prevents you from building massive, complicated systems that fail when you try to connect them. It forces the AI to build the absolute smallest slice of a feature from front-to-back first (a "tracer bullet") before expanding it.
*   **When to use it:** When starting a brand new integration (like connecting n8n to a new database) or building a new product feature from scratch.
*   **Example Prompt:** *"We need to build a webhook receiver for n8n. Use the `tracer-bullets` skill to build just a 'hello world' version that hits the database and returns a 200 OK before we add the complex business logic."*

### 3. `humanizer` (Documentation & Communication)
**What it does:** Edits text to remove the robotic, repetitive tone common in AI outputs (e.g., words like "delve", "crucial", or "pivotal", and repetitive bullet points).
*   **When to use it:** When writing PRDs, drafting emails to stakeholders, or preparing documentation for the investment team.
*   **Example Prompt:** *"Review my draft for the new architecture update. Apply the `humanizer` skill to make it sound like it was written by a human, removing any AI buzzwords."*

### 4. `data-querying` (Safe Analytics)
**What it does:** Ensures the AI approaches database queries methodically. It forces the AI to understand schemas first, write safe (read-only) SQL, and present the data clearly.
*   **When to use it:** When you need to extract metrics from Aurora or RDS to answer questions from the investment team.
*   **Example Prompt:** *"Using the `data-querying` skill, write a script to find all companies in the DB with revenue over $1M in Q3."*

### 5. `product-management` (Planning & Scoping)
**What it does:** Turns the AI into a structured product manager. It helps break vague requests into actionable requirements, defines success metrics, and outlines edge cases.
*   **When to use it:** Before you write any code! Use this when you get a new request from the business side and need to map out *what* actually needs to be built.
*   **Example Prompt:** *"The investment team wants a new dashboard for traction metrics. Use the `product-management` skill to help me draft the requirements and scope the effort."*

### 6. `universal-tester` (Custom Droid for QA)
**What it does:** A specialized evaluation engine that stress-tests our n8n Langchain agents to ensure they don't hallucinate or get stuck in infinite loops.
*   **When to use it:** Right before you deploy a new agent workflow to production.
*   **Example Prompt:** *"Run the `universal-tester` against my local FastAPI webhook at http://localhost:8000/api/v1/chat."*

## 🔌 Available MCP Tools

### 1. `edgartools-mcp` (SEC EDGAR Intelligence)
**What it does:** Adds SEC filing intelligence as MCP tools for investment workflows (10-K/10-Q/8-K analysis, insider transactions, comparisons, trends, and monitoring).
*   **Where it is:** `tools/edgartools-mcp/`
*   **Install guide:** `tools/edgartools-mcp/installation-guide.md`
*   **One-prompt setup:** `tools/edgartools-mcp/one-prompt-installation-guide.md`
*   **PRD fit + roadmap:** `tools/edgartools-mcp/tool-description.md`
*   **MCP config template:** `tools/edgartools-mcp/mcp-config.template.json`
*   **Skill routing:** `tools/edgartools-mcp/skill-routing.md`
*   **PDR integration handoff:** `tools/edgartools-mcp/pdr-integration-handoff.md`
*   **HTTP pilot (WIP):** `tools/edgartools-mcp/http-wip/`

## 🚀 How to Use (Factory CLI)

To utilize these skills locally, they must be placed in your Factory configuration directory.

```bash
# Clone this repository into your personal Factory skills directory
git clone https://github.com/NZCD5L/dannazca-skills.git ~/.factory/skills
```

Once installed, you can trigger these skills dynamically in your Factory terminal:
```bash
droid task "Refactor this python script using the solid skill"
```

## ⚠️ Architecture Constraints
As part of our internal architecture guidelines, **no core business logic should be baked directly into CLI configurations**. If a tool requires complex loops or logic, it must be engineered as a portable Python script or MCP (Model Context Protocol) Server, ensuring it can be consumed by both Factory Droids and Claude Code seamlessly.
