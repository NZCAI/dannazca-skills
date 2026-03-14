---
name: frontend-ui-integration
description: Implement typed frontend flows backed by existing APIs while following the design system, routing rules, and test coverage requirements.
---

# Frontend UI Integration

## Use This Skill When
- Building or updating UI surfaces that talk to an already-existing backend endpoint.
- Refining client-side state, validation, or orchestration logic without changing server contracts.
- Enforcing the product design system, accessibility, and analytics conventions on new features.

## Required Inputs
1. Source issue, spec, or acceptance criteria describing the user flow.
2. API references (OpenAPI file, TypeScript client, or GraphQL schema) for the backend the UI consumes.
3. Design tokens or component-library references (Figma link, Storybook entry, etc.).
4. Target app/package path plus routing context (URL, nested layout, feature flag, etc.).

## Workflow
1. Confirm backend coverage: inspect shared types or generate a typed client; add or update Zod/TypeScript models as needed.
2. Sketch the UI hierarchy using existing atomic components, ensuring responsive breakpoints and ARIA attributes stay aligned with design rules.
3. Implement the feature with strict type checking enabled (`tsc --noEmit`) and colocate state management with the component where possible.
4. Wire analytics/telemetry hooks (tracking IDs, tracing spans) and guard feature rollout behind the provided flag.
5. Add or extend unit tests (React Testing Library, Vitest/Jest) plus E2E/regression cases where the flow spans multiple pages.
6. Update docs visible to QA/PM (changelog snippet, release notes entry, screenshots) if the feature is user-facing.

## Verification
- `npm run lint` (or the repo’s lint command) passes without warnings.
- `npm run test -- --runInBand` (or equivalent) covers new logic and snapshots are updated when intentional.
- Manual smoke test in the dev server shows the new flow behaving as spec, including empty/error states.

## Deliverables
- Updated UI components, hooks, and typed clients scoped to the requested app.
- Tests proving the critical path plus edge cases (loading, error, disabled states).
- Brief summary in the PR description that calls out feature flags, analytics, and verification commands executed.
