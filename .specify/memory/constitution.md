<!--
# Sync Impact Report
- Version change: Unversioned template → 1.0.0
- Principles defined:
  - I. The Spec Is the Source of Truth
  - II. Test-First (NON-NEGOTIABLE)
  - III. Own Implementations of Graphs and Algorithms
  - IV. Standard Library Only at Runtime
  - V. Explicit Handling of Input Data
  - VI. Deterministic, Testable Output
  - VII. Simple, Typed, Extensible Code
- Added sections:
  - Technical Constraints
  - Development Workflow
  - Governance
- Removed sections: None
- Follow-up TODOs: None (all placeholders resolved)
-->

# Directed Dependency Graph CLI Constitution

## Core Principles

### I. The Spec Is the Source of Truth
Every behavior MUST be described in a feature spec before it is implemented. Spec and code MUST always agree. When a defect is found, the team MUST determine whether the spec or the code is wrong; if the spec is defective, update the spec first, then modify the code. Spec and code MUST never be left in disagreement.

### II. Test-First (NON-NEGOTIABLE)
Every acceptance scenario, including edge cases and error cases, MUST have at least one automated pytest test written and observed failing before the code that makes it pass is implemented. A feature is complete ONLY when all its automated tests pass.

### III. Own Implementations of Graphs and Algorithms
The graph data structure and all graph algorithms MUST be implemented by the project. Application code MUST NOT import third-party or external graph libraries (such as NetworkX, igraph, graph-tool, graphlib, scipy.sparse.csgraph, or similar). Those libraries MAY be used solely in automated tests as an oracle to verify correctness. The graph representation MUST be justified in `plan.md` and `research.md`, explicitly documenting rejected alternatives and trade-offs.

### IV. Standard Library Only at Runtime
The application MUST have zero third-party runtime dependencies. The command-line interface MUST use standard-library `argparse` and file parsing MUST use the standard-library `csv` module. Third-party packages are permitted exclusively as development dependencies (for testing, linting, formatting, and test oracles).

### V. Explicit Handling of Input Data
Input files are untrusted real-world data. Every irregularity the application can encounter (including malformed rows, blank or whitespace-padded values, duplicate edges or vertices, self-loops, cycles, missing or incorrect headers, empty files, or missing files) MUST have its behavior explicitly defined in a feature specification. The application MUST never silently discard or alter input data; anything skipped or normalized MUST be reported. All errors MUST be clear, actionable, written to `stderr`, and cause the process to exit with a non-zero status.

### VI. Deterministic, Testable Output
The same input and command-line arguments MUST always produce byte-for-byte identical output across executions. Normal execution results MUST be written to `stdout`, and diagnostics/error messages MUST be written to `stderr`. Any ordering in the output (such as vertices, edges, or topological orders) MUST be strictly and deterministically defined by the specification so automated tests can reliably assert exact matches.

### VII. Simple, Typed, Extensible Code
Application code MUST be as simple as current features require, maintaining clear separation of concerns: the graph model, file loading, algorithms, and CLI MUST reside in separate modules. All functions, methods, and module interfaces MUST provide complete type hints, and all code MUST pass `ruff check` and `ruff format --check`. Architectural and design choices MUST NOT prevent later features (such as weighted edges or additional traversals) from being added without rewriting existing code.

## Technical Constraints

- **Language & Runtime**: Python 3.11+ strictly using the Python standard library at runtime.
- **Interface**: Command-line interface (CLI) only; interactive prompts or GUI components are prohibited.
- **Runtime Dependencies**: Zero third-party runtime packages; parsing MUST use `csv` and CLI argument handling MUST use `argparse`.
- **Development Dependencies**: `pytest` (test execution), `ruff` (linting and formatting), and external graph libraries allowed solely as test oracles.
- **Repository Structure**:
  - Application source code in `src/`.
  - Test suites and test fixtures in `tests/`.
  - Sample datasets and input files in `data/`.
- **Security & Secrets**: No API keys, credentials, tokens, or private secrets may be committed to the repository.

## Development Workflow

- **Branch Isolation**: Each feature MUST be developed on its own dedicated branch.
- **Spec Kit Lifecycle**: Features MUST strictly proceed through the phases in sequential order: `specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`.
- **Clarification Tracking**: Every feature specification MUST include a `Clarifications` section recording every question raised and decision made.
- **Quality Gates**: `/speckit.analyze` MUST run before implementation begins. All CRITICAL and HIGH findings MUST be resolved and documented before invoking `/speckit.implement`.
- **Commit Cadence**: At least one commit per phase MUST be recorded for each feature.
- **Merge Requirements**: A feature branch MAY be merged into the main branch ONLY when all automated tests pass and `ruff` reports no issues.
- **Feature Dependencies**: Any feature that builds upon another MUST start only after the prerequisite feature has been merged.

## Governance

The constitution is the supreme architectural and development authority for the project and supersedes any conflicting practices, informal conventions, or agent suggestions.

- **Constitution Check**: Every implementation plan MUST include an explicit Constitution Check verifying compliance with all principles and technical constraints. Any planned violation or deviation MUST be explicitly justified in the plan's complexity tracking section or eliminated.
- **Amendment Procedure**: Amendments to the constitution MUST be executed in a dedicated commit, updating the Sync Impact Report comment and bumping the version in accordance with semantic versioning.
- **Versioning Policy**:
  - **MAJOR**: Incompatible governance shifts, removing a principle, or fundamentally redefining a core principle.
  - **MINOR**: Adding a new principle, technical constraint, or structural section, or materially expanding existing rules.
  - **PATCH**: Wording improvements, clarifications, typo fixes, and non-semantic adjustments.

**Version**: 1.0.0 | **Ratified**: 2026-10-30 | **Last Amended**: 2026-10-30
