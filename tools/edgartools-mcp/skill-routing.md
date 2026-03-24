# Skill Routing — EdgarTools MCP + Nazca Skills

## When to use EdgarTools MCP directly
Use EdgarTools MCP when the task is SEC-native:
- 10-K/10-Q/8-K extraction
- insider/ownership checks
- multi-company comparisons
- quarterly/annual trend pulls

## When to pair with `product-management`
Use `product-management` first when the request is ambiguous or strategic:
- define diligence scope
- prioritize metrics/questions
- produce structured memo requirements and acceptance criteria

Then execute data collection with EdgarTools MCP.

## When to pair with `ai-data-analyst`
Use `ai-data-analyst` after MCP extraction:
- clean and normalize time-series
- fill missing periods as null
- generate CSV/XLS outputs
- run consistency and completeness checks

## When to pair with `data-querying`
Use `data-querying` only if you need to merge SEC outputs with internal Nazca datasets (CRM/portfolio/KPI warehouse).

## When to pair with `solid`
Use `solid` for productionizing scripts/services around this MCP flow:
- reusable extraction scripts
- validation pipelines
- tests and refactors

## Default workflow
1. `product-management` (scope and required outputs)
2. EdgarTools MCP (data pull)
3. `ai-data-analyst` (transform/export)
4. `solid` (production hardening, if needed)
