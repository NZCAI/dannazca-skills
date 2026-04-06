---
name: data-querying
version: 1.0.0
status: minimal
description: Safely query internal analytics sources, producing reproducible notebooks, validated SQL, and documented insights.
allowed-tools:
  - Read
  - Write
  - Bash
related-skills:
  - ai-data-analyst
  - product-management
tags:
  - sql
  - analytics
  - data-warehousing
  - reproducibility
---

# Data Querying

## Use This Skill When
- Answering product, growth, or reliability questions that rely on internal warehouses/lakes.
- Producing dashboards, CSV extracts, or notebooks that must be auditable and reproducible.
- Triaging incidents or experiments where data accuracy and PII handling are critical.

## Required Inputs
1. Clear analytical question plus success metric or KPI definition.
2. Warehouse/project identifiers (BigQuery dataset, Snowflake DB, dbt model schema) and access scope.
3. Canonical metric definitions or dbt models to reference, including grain and filters.
4. Format expectations for the output (notebook, markdown summary, chart type, CSV, etc.).

## Workflow
1. Translate the question into hypotheses and decide the minimal dataset needed; prefer existing certified models over raw tables.
2. Draft SQL in a checked-in location (e.g., `analytics/queries/<ticket>.sql`) with parameters documented at the top.
3. Run queries in a controlled environment, limiting result size and ensuring filters exclude PII/regulated data unless explicitly approved.
4. Export results into a notebook/report with the exact query text, timestamp, and environment captured for reproducibility.
5. Analyze trends, segment by relevant dimensions, and call out anomalies or data quality concerns.
6. Summarize findings with decision-ready bullets plus follow-up recommendations.

## Verification
- Execute automated lint/type checks for analytics code (`dbt test`, `sqlfluff lint analytics/queries`, etc.).
- Re-run the query with a different seed or date range to ensure deterministic results.
- Share preview links or artifact paths (e.g., `.ipynb`, `.md`, `.csv`) and confirm peers can open them with read-only credentials.

## Deliverables
- Checked-in SQL/notebook files plus rendered artifacts attached to the ticket/PR.
- Summary section outlining methodology, key metrics, and confidence level.
- Documented next steps or decisions unblocked by the analysis.
