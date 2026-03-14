# Nazca Skills Repository (Factory.ai)

This repository contains the centralized AI agent skills and tools utilized by the Nazca technical team. It serves as the single source of truth for prompts, behaviors, and specialized utilities designed to run within the Factory.ai ecosystem and external interfaces like Claude Code.

## 🎯 Purpose
The goal of this repository is to eliminate "prompt sprawl" and ensure that all team members (from senior engineers to trainees) use the same, version-controlled instructions when leveraging AI for code generation, data analysis, and system architecture.

## 🛠 Available Skills

*   **`solid`**: Enforces SOLID principles, Test-Driven Development (TDD), and clean architecture standards on generated code.
*   **`tracer-bullets`**: Guides the agent to implement features via tiny, end-to-end vertical slices to prevent overbuilding.
*   **`humanizer`**: A specialized editing skill that removes common LLM linguistic patterns and robotic tones from written documentation.
*   **`universal-tester`**: A Factory Custom Droid engine used to evaluate the memory coherence and human tone of internal n8n agents via FastAPI endpoints.
*   *Other domains include Data Querying, Internal Tools, Frontend UI Integration, and Product Management.*

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
