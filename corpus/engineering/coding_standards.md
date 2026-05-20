# Engineering Coding Standards

This document defines the coding standards enforced across Acme Robotics engineering repositories. These standards are enforced via pre-commit hooks and CI checks.

## Languages and Style

Each language has a single canonical formatter and linter:

- **Go**: gofmt + golangci-lint with the `.golangci.yml` config in the monorepo root
- **Python**: ruff for both linting and formatting, configured for Python 3.11+
- **Rust**: rustfmt + clippy with deny-warnings in CI
- **TypeScript**: prettier + eslint with the `@acme/eslint-config` shared config
- **C++**: clang-format using the LLVM style with 100-char line length

## Naming Conventions

- Service names use kebab-case: `fleet-api`, `dispatch-service`
- Database tables use snake_case: `robot_telemetry_events`, `facility_assignments`
- Kafka topics use dot.case: `robot.telemetry.raw`, `dispatch.commands.issued`
- Environment variables use UPPER_SNAKE_CASE with an `ACME_` prefix: `ACME_DB_HOST`, `ACME_LOG_LEVEL`

## Pull Request Requirements

Every PR must include:

1. A linked issue or JIRA ticket
2. Test coverage for new code (minimum 70% line coverage for changed files)
3. At least one approval from a CODEOWNER for the modified path
4. A passing CI run with all required checks green

PRs that modify production-critical paths (dispatch-service, command-control, telemetry-ingest) additionally require approval from a senior engineer on the owning team.

## Code Review SLA

Reviewers are expected to respond within 24 hours during business days. If you cannot review within that window, reassign explicitly rather than letting the PR sit.
