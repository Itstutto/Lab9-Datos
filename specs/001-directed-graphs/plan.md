# Implementation Plan: Directed Graphs (Loading & Display)

**Branch**: `001-directed-graphs` | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-directed-graphs/spec.md`

---

## Summary

This feature provides the foundational capability to load directed, unweighted dependency graphs from CSV files and display them deterministically via a command-line interface.

The application is built in Python 3.11+ using strictly the Python standard library (`argparse`, `csv`, `pathlib`, `sys`). The internal graph model is implemented from scratch as an encapsulated adjacency list (`dict[str, set[str]]` for successors and predecessors), offering $O(1)$ edge insertion, $O(1)$ duplicate detection, and $O(V + E)$ space complexity, cleanly decoupled from file I/O and display formatting. The CSV loader performs rigorous input validation and normalization, returning a structured `LoadResult` container of graph data and physical line diagnostics. The CLI formats output to `stdout` with lexicographical sorting, directs diagnostics and errors to `stderr`, and exits with standardized status codes.

---

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: None (Standard Library only at runtime: `argparse`, `csv`, `pathlib`, `sys`, `dataclasses`, `typing`)  
**Storage**: In-memory adjacency list data structure  
**Testing**: `pytest` (automated testing), `ruff` (linting and formatting), `networkx` (test oracle only in `tests/oracle/`, never imported in `src/`)  
**Target Platform**: Cross-platform CLI (macOS, Linux, Windows) executed via `python3 -m src.cli [display] <file.csv>`  
**Project Type**: Standalone command-line application  
**Performance Goals**: Load, validate, and display graphs of up to 10,000 edges in under 1.0 second (SC-001)  
**Constraints**: Zero runtime third-party dependencies (Constitution Principle IV); byte-for-byte deterministic output (Principle VI); no silent alterations or drops (Principle V); modular separation across `graph.py`, `loader.py`, and `cli.py` (Principle VII)  
**Scale/Scope**: Arbitrary directed graphs that fit into memory (thousands of vertices and edges)  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Constraint | Status | Compliance Verification |
|---|---|---|
| **I. The Spec Is the Source of Truth** | **PASS** | `spec.md` is fully defined and validated with 0 remaining clarification markers. Implementation strictly implements the behavior defined in the spec. |
| **II. Test-First (NON-NEGOTIABLE)** | **PASS** | Full test suite (`tests/unit/`, `tests/integration/`, `tests/oracle/`) planned to be written and observed failing before implementing `src/` modules. |
| **III. Own Implementations of Graphs and Algorithms** | **PASS** | `DirectedGraph` is designed from scratch in `src/graph.py`. `networkx` is used exclusively in `tests/oracle/` as a verification oracle. Graph representation and rejected alternatives are justified in `research.md`. |
| **IV. Standard Library Only at Runtime** | **PASS** | Runtime code uses only Python stdlib (`argparse`, `csv`, `sys`, `pathlib`). No external packages in `pyproject.toml` runtime dependencies. |
| **V. Explicit Handling of Input Data** | **PASS** | All input anomalies (missing files, invalid headers, malformed rows, duplicate edges, isolated vertices, whitespace padding) are defined with specific actions and line-numbered diagnostics on `stderr`. |
| **VI. Deterministic, Testable Output** | **PASS** | Strict lexicographical sorting for vertices and edges; `stdout` for results; `stderr` for diagnostics; byte-for-byte identical output across repeated runs. |
| **VII. Simple, Typed, Extensible Code** | **PASS** | Modular architecture (`src/graph.py`, `src/loader.py`, `src/cli.py`); full type hinting; strict `ruff` validation; extensible for Feature 2 (topological sort) and Feature 3 (weighted edges). |
| **Technical Constraint: Python 3.11+** | **PASS** | Python 3.11+ type syntax and features utilized. |
| **Technical Constraint: CLI Only** | **PASS** | Standard CLI interface with standard exit codes (0, 1, 2). |
| **Technical Constraint: Directory Layout** | **PASS** | `src/` for application code, `tests/` for tests, `data/` for sample datasets. |
| **Technical Constraint: Secret Hygiene** | **PASS** | No credentials, tokens, or private assets. |

---

## Project Structure

### Documentation (`specs/001-directed-graphs/`)

```text
specs/001-directed-graphs/
├── spec.md              # Feature specification (completed & clarified)
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & rejected alternatives (Phase 0)
├── data-model.md        # Entities, invariants & data types (Phase 1)
├── quickstart.md        # Runnable verification guide (Phase 1)
├── contracts/           # Interface contracts (Phase 1)
│   └── cli.md           # CLI syntax, stdout/stderr format, exit codes
└── checklists/
    └── requirements.md  # Spec quality checklist (16/16 passing)
```

### Source Code (`src/`) and Tests (`tests/`)

```text
src/
├── __init__.py          # Package marker
├── graph.py             # DirectedGraph data model (pure model, zero I/O)
├── loader.py            # CSV file parsing, normalization, and validation
└── cli.py               # argparse entry point, output formatting, exit codes

tests/
├── __init__.py          # Package marker
├── conftest.py          # Pytest fixtures and test paths
├── unit/
│   ├── __init__.py
│   ├── test_graph.py    # Unit tests for DirectedGraph methods
│   └── test_loader.py   # Unit tests for CSV parser, edge cases, exceptions
├── integration/
│   ├── __init__.py
│   ├── test_cli.py      # Subprocess CLI tests on data/*.csv & fixtures
│   └── test_performance.py # Benchmark verifying SC-001 (10,000 edges < 1.0s)
├── oracle/
│   ├── __init__.py
│   └── test_networkx_oracle.py # Cross-check graph models against NetworkX
└── data/                # Purpose-built edge case CSV test fixtures
    ├── empty_file.csv
    ├── header_only.csv
    ├── invalid_header.csv
    ├── wrong_columns.csv
    ├── empty_source.csv
    ├── padded_whitespace.csv
    └── duplicate_edges.csv

data/                    # Project sample datasets
├── small-dag.csv
├── cs-curriculum.csv
└── build-with-cycle.csv
```

**Structure Decision**: Single project layout cleanly separating pure data structure logic (`src/graph.py`), ingestion/validation logic (`src/loader.py`), and CLI presentation (`src/cli.py`). This guarantees no I/O leaks into the graph model, satisfies Constitution Principle VII, and allows Feature 2 (`src/algorithms.py`) to build directly upon `DirectedGraph` without modifying existing modules.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| *None* | *All principles and constraints fully satisfied without deviations.* | *N/A* |
