# Changelog

All notable changes to dannazca-skills are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning Policy

### Version Format
- **Semantic Versioning:** MAJOR.MINOR.PATCH (e.g., 1.0.0)
  - **MAJOR:** Backward-incompatible changes to skill behavior or API
  - **MINOR:** New features or enhancements (backward-compatible)
  - **PATCH:** Bug fixes and minor improvements

### Status Levels
- **foundational** — Core infrastructure skills used across all projects (e.g., solid, product-management)
- **mature** — Production-ready with extensive testing and documentation (e.g., humanizer, ai-data-analyst)
- **operational** — Active in production use with ongoing maintenance (e.g., trading-analysis-framework)
- **minimal** — Functional but limited scope, may have sparse documentation
- **prototype** — Experimental, may be unstable or undergoing major changes
- **deprecated** — No longer recommended; scheduled for removal (see Deprecation Policy)

### Deprecation Policy

Skills in **deprecated** status follow this timeline:

1. **Announcement Phase (4 weeks)**
   - Mark skill as deprecated in SKILL.md
   - Add CHANGELOG entry with migration guide
   - Notify all teams of deprecation date

2. **Sunset Phase (8 weeks)**
   - Skill remains functional but no new development
   - Support available for migration to replacement
   - Warnings added to documentation

3. **Removal (12 weeks from deprecation announcement)**
   - Skill directory removed from repository
   - Final commit tags removal with date
   - Archive maintained in git history

---

## [Unreleased]

### Added
- Pytest framework with 20+ validation tests
- GitHub Actions CI/CD: 4 automated workflows (Python tests, YAML validation, Markdown linting, naming conventions)
- CODEOWNERS file with skill ownership assignments
- Updated README.md with complete skill inventory matrix
- CHANGELOG.md with versioning and deprecation policy
- `governance/FastAPI_ECS_Deployment_Apr2026.md` — ECS Fargate deployment session handoff doc

### Changed
- All 13 SKILL.md files standardized with consistent metadata (version, status, allowed-tools, related-skills, tags)
- Updated .markdownlint.json configuration for consistent markdown style
- `governance/project-context.yaml` — advanced to Sprint 2, updated milestones, key decisions, and active blockers
- **Strategic pivot (Apr 10):** Roadmap resequenced — MCP accessibility before infrastructure completeness. Team primary interface is Claude; delivering usable tools in Claude now takes priority over dashboards, PostgreSQL, and production hardening.

### Fixed
- None in this release

---

## [1.1.0] — 2026-04-09

### Sprint 1 Complete + ECS Fargate Deployment ✅

#### Added

- **FastAPI Bridge — ECS Fargate deployment live:**
  - ECS cluster `nazca-cluster` + Fargate service `nazca-fastapi-service` (us-east-1)
  - Task definition `nazca-fastapi:1` — 512 CPU / 1024 MB, port 8000
  - Public URL live: `http://32.192.36.164:8000` (ephemeral — changes on task restart)
  - CloudWatch log group `/ecs/nazca-fastapi` streaming
  - Secrets Manager integration: `OPENAI_API_KEY`, `JWT_SECRET_KEY`, `EDGAR_IDENTITY` injected at runtime
  - IAM role `ecsTaskExecutionRole` with ECR pull + Secrets Manager access

- **FastAPI Bridge — Sprint 1 baseline (shipped Apr 9):**
  - 51/51 tests passing
  - LangGraph 12-agent trading graph wired end-to-end (mock outputs)
  - RBAC + JWT middleware live
  - In-memory JobStore with async pipeline runners (5A/5B)
  - EdgarTools HTTP client integrated

- **Infrastructure decisions documented:**
  - ECS image platform: `linux/amd64` required for Fargate (Apple Silicon builds are arm64)
  - Secrets Manager key naming: clean JSON keys required (trailing whitespace breaks ECS secret injection)

#### Changed

- `project-context.yaml` — Sprint 1 → Sprint 2, milestones updated, key decisions corrected
- ECR image rebuilt as `linux/amd64` (was arm64 from Apple Silicon build — incompatible with Fargate)

#### Fixed

- `EDGAR_IDENTITY` key in Secrets Manager had a trailing tab character — caused `ResourceInitializationError` during ECS task launch; fixed by rewriting secret via Python

#### Status

✅ Sprint 1: Foundation — COMPLETE (shipped Apr 9)
🔄 Sprint 2: Observability — IN PROGRESS (target Apr 22)

---

## [1.0.0] — 2026-04-06

### Phase 1: Repository Standardization Complete ✅

#### Added
- **Core Skills Versioned:**
  - solid v1.0.0 (foundational)
  - product-management v1.0.0 (mature)
  - humanizer v2.2.0 (mature)
  - ai-data-analyst v1.0.0 (mature)
  - trading-analysis-framework v1.0.0 (operational)
  - And 8 additional skills with full metadata

- **MCP Tools:**
  - edgartools-mcp v1.0.0 (operational) with stdio and HTTP pilot modes
  - Skill routing and integration guides

- **Documentation:**
  - Expanded README.md with skill discovery matrix
  - Phase 2 trading agents assessment (PHASE_2_AUDIT_REPORT.md)
  - Fast-track trading integration roadmap (FAST_TRACK_TRADING_INTEGRATION.md)

- **Infrastructure:**
  - GitHub Actions CI/CD pipeline (.github/workflows/)
  - Pytest test suite (tests/)
  - CODEOWNERS file with responsibility assignments
  - CHANGELOG.md (this file)

#### Changed
- Transitioned from unversioned skills to semantic versioning across all 13 skills
- Standardized SKILL.md frontmatter format (name, version, status, description, allowed-tools, related-skills, tags)
- Consolidated skill documentation under unified README.md
- Renamed PDR_v1.md → Nazca_Governance_Blueprint_v1.md
- Renamed PRD_Nazca_Agentic_System_V2.md → Nazca_Technical_Specification_v2.md

#### Fixed
- Removed duplicate skill definitions
- Corrected bidirectional references in related-skills fields
- Resolved terminology inconsistencies across documentation

#### Status
✅ Phase 1: GitHub Repository Standardization — COMPLETE

---

## Upcoming Releases

### Phase 2 (Planned)
- FactoryTest repository assessment
- Trading agents integration testing
- Reference implementation alignment

### Phase 3 (Planned)
- Data science workflow standardization (Pipelines 5A, 5B, Market Analysis)
- Terminology audit and cross-reference validation
- Agent prompt alignment with governance constraints

### Phase 4 (Planned)
- FastAPI Bridge implementation
- MCP integration (edgartools-mcp HTTP mode)
- RBAC enforcement and observability middleware
- E2E workflow testing

### Phase 5 (Planned)
- Development server launch.json configuration
- Local testing setup guides
- Deployment documentation

---

## Git Commit History

Recent commits leading to v1.0.0:

- `f425aaa` — Add fast-track trading integration roadmap (FAST_TRACK_TRADING_INTEGRATION.md)
- `d17f818` — Phase 2: Complete Trading Agents & Reference Implementation Assessment
- `0c27cec` — Standardize all 13 SKILL.md files with version, status, metadata
- `9ef6519` — Create standardized tools/SKILL.md for MCP tools directory
- `bb63d35` — Add standardized frontmatter to trading-analysis-framework SKILL.md
- `28c523b` — Add standardized frontmatter to tidy-data-framework SKILL.md

---

## Contributing

When adding changes to dannazca-skills:

1. **Update SKILL.md** with new version number (MAJOR.MINOR.PATCH)
2. **Update CHANGELOG.md** with a summary of changes
3. **Create git commit** with message: `chore: update {skill-name} to X.Y.Z`
4. **Ensure tests pass** (GitHub Actions will validate automatically)
5. **Create PR** for team review before merging to main

### Release Process

1. Update version in all affected SKILL.md files
2. Update CHANGELOG.md with release notes
3. Create git tag: `git tag -a v{version} -m "Release {version}"`
4. Push tag: `git push origin v{version}`
5. Create GitHub Release from tag

---

## License

See LICENSE file in repository.

---

**Last Updated:** April 6, 2026
**Maintainers:** @admin, @devops, @data-scientist, @ai-team
