# Nazca Skills Repository (Factory.ai)

This repository contains the centralized AI agent skills and tools utilized by the Nazca technical team. It serves as the single source of truth for prompts, behaviors, and specialized utilities designed to run within the Factory.ai ecosystem and external interfaces like Claude Code.

## 🎯 Purpose
The goal of this repository is to eliminate "prompt sprawl" and ensure that all team members (from senior engineers to trainees) use the same, version-controlled instructions when leveraging AI for code generation, data analysis, and system architecture.

## 🛠 Available Skills & Everyday Use Cases

Think of these skills as "lenses" you can put on your AI. Depending on the task you are doing, invoking a specific skill forces the AI to behave according to Nazca's exact standards for that specific job.

### Skill Inventory Matrix

| Skill | Version | Status | Owner | Use Case | Tags |
|-------|---------|--------|-------|----------|------|
| **solid** | 1.0.0 | Foundational | @admin | Code quality, architecture, TDD | code-quality, design-patterns, testing |
| **product-management** | 1.0.0 | Mature | @admin | Planning, scoping, PRD writing | product-strategy, requirements, roadmapping |
| **humanizer** | 2.2.0 | Mature | @ai-team | Writing, editing, communication | writing, tone-adjustment, documentation |
| **ai-data-analyst** | 1.0.0 | Mature | @data-scientist | Statistical modeling, EDA, reporting | statistics, data-science, analysis |
| **tracer-bullets** | 1.0.0 | Minimal | @admin | Feature development strategy, MVP planning | strategy, feature-development, mvp |
| **browser** | 1.0.0 | Minimal | @tooling-team | Chrome automation, web scraping, screenshots | automation, web-scraping, testing |
| **data-querying** | 1.0.0 | Minimal | @data-scientist | Safe analytics, SQL, database queries | sql, analytics, data-extraction |
| **frontend-ui-integration** | 1.0.0 | Minimal | @frontend-team | Typed UI flows, component integration | frontend, ui, react, typescript |
| **service-integration** | 1.0.0 | Minimal | @devops | Backend orchestration, service wiring | architecture, backend, integration |
| **internal-tools** | 1.0.0 | Minimal | @devops | Admin consoles, RBAC, operator dashboards | admin, tools, rbac, governance |
| **tidy-data-framework** | 1.0.0 | Prototype | @data-scientist | Data transformation, cleaning, validation | data-engineering, etl, transformation |
| **trading-analysis-framework** | 1.0.0 | Operational | @ai-team | Multi-agent trading analysis, LangGraph | ai-agents, finance, trading, orchestration |

### Detailed Skill Descriptions

#### 1. `solid` (Code Quality & Architecture) ⭐ Foundational
**What it does:** Forces the AI to write code like a Senior Software Engineer. It strictly enforces clean code, logical separation of concerns, and Test-Driven Development.
*   **When to use it:** When writing new Python functions, refactoring messy code, or building an API endpoint.
*   **Example Prompt:** *"I need a Python script to parse these CSVs. Please use the `solid` skill to ensure the architecture is clean and includes unit tests."*

#### 2. `tracer-bullets` (Feature Development Strategy)
**What it does:** Prevents you from building massive, complicated systems that fail when you try to connect them. It forces the AI to build the absolute smallest slice of a feature from front-to-back first (a "tracer bullet") before expanding it.
*   **When to use it:** When starting a brand new integration (like connecting n8n to a new database) or building a new product feature from scratch.
*   **Example Prompt:** *"We need to build a webhook receiver for n8n. Use the `tracer-bullets` skill to build just a 'hello world' version that hits the database and returns a 200 OK before we add the complex business logic."*

#### 3. `humanizer` (Documentation & Communication) ⭐ Mature
**What it does:** Edits text to remove the robotic, repetitive tone common in AI outputs (e.g., words like "delve", "crucial", or "pivotal", and repetitive bullet points).
*   **When to use it:** When writing PRDs, drafting emails to stakeholders, or preparing documentation for the investment team.
*   **Example Prompt:** *"Review my draft for the new architecture update. Apply the `humanizer` skill to make it sound like it was written by a human, removing any AI buzzwords."*

#### 4. `data-querying` (Safe Analytics)
**What it does:** Ensures the AI approaches database queries methodically. It forces the AI to understand schemas first, write safe (read-only) SQL, and present the data clearly.
*   **When to use it:** When you need to extract metrics from Aurora or RDS to answer questions from the investment team.
*   **Example Prompt:** *"Using the `data-querying` skill, write a script to find all companies in the DB with revenue over $1M in Q3."*

#### 5. `product-management` (Planning & Scoping) ⭐ Mature
**What it does:** Turns the AI into a structured product manager. It helps break vague requests into actionable requirements, defines success metrics, and outlines edge cases.
*   **When to use it:** Before you write any code! Use this when you get a new request from the business side and need to map out *what* actually needs to be built.
*   **Example Prompt:** *"The investment team wants a new dashboard for traction metrics. Use the `product-management` skill to help me draft the requirements and scope the effort."*

#### 6. `ai-data-analyst` (Statistical Modeling & Analysis) ⭐ Mature
**What it does:** Comprehensive data science workflow tool for EDA, statistical analysis, model building, and reporting.
*   **When to use it:** For quantitative analysis, hypothesis testing, feature engineering, and data-driven decision making.
*   **Example Prompt:** *"Using the `ai-data-analyst` skill, analyze this dataset for correlations with fund performance and generate a statistical report."*

#### 7. `trading-analysis-framework` (Multi-Agent Trading) ⭐ Operational
**What it does:** Orchestrates 12+ specialized agents (analysts, researchers, traders, risk managers) for comprehensive trading analysis using LangGraph.
*   **When to use it:** For complex trading decisions, multi-perspective analysis, risk assessment, and portfolio management.
*   **Where it is:** `trading-analysis-framework/`
*   **Example Prompt:** *"Use the `trading-analysis-framework` to analyze NVDA with fundamental, technical, and sentiment analysis from multiple agent perspectives."*

#### 8. `tidy-data-framework` (Data Transformation) - Prototype
**What it does:** Standardized data cleaning, transformation, and validation workflows for ETL pipelines.
*   **When to use it:** When building data pipelines or cleaning messy datasets for analysis.
*   **Status:** Early-stage, improving

## 🔌 Available MCP Tools & Integrations

| MCP Tool | Version | Status | Owner | Purpose | Docs |
|----------|---------|--------|-------|---------|------|
| **edgartools-mcp** | 1.0.0 | Operational | @edgar-team | SEC EDGAR filing intelligence, comparables, trends | [Installation](tools/edgartools-mcp/installation-guide.md) |

### 1. `edgartools-mcp` (SEC EDGAR Intelligence)
**What it does:** Adds SEC filing intelligence as MCP tools for investment workflows (10-K/10-Q/8-K analysis, insider transactions, comparables, trends, and monitoring).
*   **Where it is:** `tools/edgartools-mcp/`
*   **Install guide:** `tools/edgartools-mcp/installation-guide.md`
*   **One-prompt setup:** `tools/edgartools-mcp/one-prompt-installation-guide.md`
*   **PRD fit + roadmap:** `tools/edgartools-mcp/tool-description.md`
*   **MCP config template:** `tools/edgartools-mcp/mcp-config.template.json`
*   **Skill routing:** `tools/edgartools-mcp/skill-routing.md`
*   **PDR integration handoff:** `tools/edgartools-mcp/pdr-integration-handoff.md`
*   **HTTP pilot (WIP):** `tools/edgartools-mcp/http-wip/` — Planned container deployment with streamable-http transport

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

## 📚 Integration & Reference Documents

### Governance & Architecture
- **[Nazca Governance Blueprint (PDR v1)](../Factory/dannazca-skills/governance/PDR_v1.md)** — RBAC, observability, audit logging, delivery timeline
- **[Nazca Technical Specification (PRD v2)](../Factory/PRD_Nazca_Agentic_System_V2.md)** — System architecture, workflows, technical requirements
- **[Nomenclature Standards](../Downloads/Nazca_Nomenclature_Standards.xlsx)** — Definitions of Tool, Product, Workflow, System Requirement, Engine

### Fast-Track Implementation
- **[Phase 2 Audit Report](PHASE_2_AUDIT_REPORT.md)** — Trading agents assessment, reusability, integration roadmap
- **[Fast-Track Trading Integration](FAST_TRACK_TRADING_INTEGRATION.md)** — 4-phase implementation plan for /analyze-ticker endpoint (Phases A-D)

### Skill Details
- **[trading-analysis-framework](trading-analysis-framework/)** — 12 agent prompts, LangGraph orchestration, TauricResearch reference implementation
- **[edgartools-mcp](tools/edgartools-mcp/)** — SEC EDGAR MCP with stdio default, HTTP pilot, installation guides

## 🚀 Integration Patterns

### How Skills + MCPs Work Together

```
FastAPI Bridge (port 8000)
  ├─ RBAC Middleware (verify token, role)
  ├─ Trace Middleware (correlation_id)
  └─ Routes:
      ├─ /api/v1/workflows/{5a|5b|market-analysis}
      │   └─ Pulls: data-querying, ai-data-analyst, tidy-data-framework
      │
      ├─ /api/v1/edgar/* (EDGAR financial data)
      │   └─ Routes to: edgartools-mcp (stdio or HTTP)
      │
      ├─ /analyze-ticker (trading analysis)
      │   └─ Pulls: trading-analysis-framework prompts
      │   └─ Routes to: LangGraph agents + edgartools-mcp for data
      │
      └─ /governance/log, /observability/metrics
          └─ Unified audit trail + observability
```

### Local Development Setup

1. **Install Factory CLI** (if not already):
   ```bash
   git clone https://github.com/NZCD5L/dannazca-skills.git ~/.factory/skills
   ```

2. **Run tests locally:**
   ```bash
   cd /tmp/dannazca-skills
   pytest tests/ -v
   ```

3. **Trigger skill in Factory:**
   ```bash
   droid task "Refactor using solid skill"
   ```

4. **Access MCPs in Claude Code:**
   - EdgarTools MCP: Configure in Claude Desktop / settings.json
   - See: [edgartools-mcp/installation-guide.md](tools/edgartools-mcp/installation-guide.md)

## ⚙️ Ownership & Governance

### Code Ownership
See [CODEOWNERS](CODEOWNERS) for skill ownership assignments.

### Versioning Policy
- **Semver Format:** MAJOR.MINOR.PATCH (e.g., 1.0.0)
- **Status Levels:** foundational, mature, minimal, prototype, operational, deprecated
- **Release Log:** See [CHANGELOG.md](CHANGELOG.md)

### Contributing
1. Update relevant SKILL.md with new version
2. Add git commit with skill name: `chore: update {skill-name} to X.Y.Z`
3. Update CHANGELOG.md
4. Create PR for team review
5. Ensure tests pass (GitHub Actions CI/CD)

## ⚠️ Architecture Constraints
As part of our internal architecture guidelines, **no core business logic should be baked directly into CLI configurations**. If a tool requires complex loops or logic, it must be engineered as a portable Python script or MCP (Model Context Protocol) Server, ensuring it can be consumed by both Factory Droids and Claude Code seamlessly.

## 📊 CI/CD & Testing

This repository uses GitHub Actions for automated quality checks:
- **YAML Validation:** Ensures all SKILL.md frontmatter is valid
- **Markdown Linting:** Checks README, CHANGELOG, skill docs for consistency
- **Python Tests:** pytest framework validates code quality and functionality
- **Naming Conventions:** Ensures kebab-case directory names, semver versioning

See [.github/workflows/](.github/workflows/) for detailed workflow configurations.

## 📞 Support & Questions

For issues, questions, or contributions:
1. Check the [Skill Inventory Matrix](#skill-inventory-matrix) above
2. Review relevant SKILL.md in each directory
3. Check [PHASE_2_AUDIT_REPORT.md](PHASE_2_AUDIT_REPORT.md) for architecture decisions
4. Contact skill owner from [CODEOWNERS](CODEOWNERS)
