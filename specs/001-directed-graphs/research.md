# Research & Design Decisions: Directed Graphs (Loading & Display)

**Feature**: Directed Graphs (Loading & Display)  
**Branch**: `001-directed-graphs`  
**Date**: 2026-11-02  
**Status**: Completed  

---

## 1. Graph Data Structure Representation

### Decision
Represent the directed unweighted graph in memory using an **adjacency list** implemented with Python native dictionaries and sets:
- Successors map: `dict[str, set[str]]` mapping each vertex to its set of outgoing neighbors.
- Predecessors map: `dict[str, set[str]]` mapping each vertex to its set of incoming neighbors (or an explicit in-degree counter).
- Every vertex in the graph exists as a key in the successors map, even if it has no outgoing edges (such as isolated vertices or sink vertices).

### Rationale
1. **Time and Space Efficiency**:
   - **Space Complexity**: $O(V + E)$ where $V$ is the number of vertices and $E$ is the number of unique directed edges. This is optimal for real-world sparse dependency graphs (e.g. curriculum prerequisites, package builds).
   - **Edge Insertion & Duplicate Detection**: Checking whether an edge $(u, v)$ already exists takes $O(1)$ average time via `v in self._adj[u]`. Adding an edge takes $O(1)$ average time.
   - **Edge Existence Lookup**: `has_edge(u, v)` is $O(1)$ average time.
   - **Degree & Neighbor Lookup**: `successors(u)` is $O(1)$ dictionary lookup returning the neighbor set. `in_degree(v)` is $O(1)$ using the predecessors map.
2. **Encapsulated Public API**:
   The internal dictionary and sets are private. The class `DirectedGraph` exposes high-level query methods:
   - `add_vertex(vertex: str) -> bool`: Adds vertex if absent; returns `True` if newly added, `False` if already present.
   - `add_edge(source: str, target: str) -> bool`: Ensures both vertices exist; adds edge to sets; returns `True` if edge was newly inserted, `False` if duplicate.
   - `vertices() -> set[str]`: Returns a set of all vertex names.
   - `edges() -> set[tuple[str, str]]`: Returns a set of all directed edge pairs `(source, target)`.
   - `successors(vertex: str) -> set[str]`: Returns direct outgoing neighbors.
   - `predecessors(vertex: str) -> set[str]`: Returns direct incoming neighbors.
   - `in_degree(vertex: str) -> int`: Returns the in-degree count.
   - `has_vertex(vertex: str) -> bool`: Checks vertex existence in $O(1)$.
   - `has_edge(source: str, target: str) -> bool`: Checks edge existence in $O(1)$.
   Sorting is deliberately separated from the graph model: all iteration or display sorting is performed by the presentation layer (CLI/formatter), keeping the graph model pure and efficient.
3. **Extensibility for Subsequent Features**:
   - **Feature 2 (Topological Sort)**: Kahn's algorithm requires tracking in-degrees and removing edges from vertices with in-degree 0. Having $O(1)$ `in_degree(v)` and $O(1)$ access to successors allows computing topological ordering in linear time $O(V + E)$.
   - **Feature 3 (Weighted Edges)**: The representation can evolve to `dict[str, dict[str, float]]` mapping `source -> {target: weight}` while retaining identical public methods (`add_vertex`, `vertices`, `has_edge`), preserving backwards compatibility for all existing callers.

### Alternatives Evaluated and Rejected

1. **Adjacency Matrix (`list[list[bool]]` or 2D array)**:
   - *Description*: A $V \times V$ matrix indexed by vertex identifiers.
   - *Why Rejected*: Requires $O(V^2)$ memory space regardless of edge density. In typical dependency graphs where $E \approx O(V)$ (sparse), an adjacency matrix wastes massive amounts of memory. For a graph with 10,000 vertices, an adjacency matrix allocates $10^8$ cells (~100 MB), whereas an adjacency list takes under 1 MB. Furthermore, iterating over all outgoing edges of a vertex takes $O(V)$ instead of $O(\text{out-degree})$.
2. **Plain Edge List (`list[tuple[str, str]]`)**:
   - *Description*: A flat list storing each edge pair `(source, target)`.
   - *Why Rejected*: Neighbor lookups, edge existence checks, and duplicate detection all require linear scans over all edges ($O(E)$). Constructing a graph of $E$ edges while checking for duplicates would scale as $O(E^2)$, severely violating the sub-second performance requirement for large graphs (SC-001).
3. **Adjacency List with Python Lists (`dict[str, list[str]]`)**:
   - *Description*: Mapping each vertex to a list of target vertex strings.
   - *Why Rejected*: Duplicate edge detection requires $v \in \text{list}$, which is $O(\text{degree})$. For vertices with high fan-out, insertions degrade to linear time per edge. Python `set` provides constant time $O(1)$ lookups and duplicate rejection.
4. **Edge Dataclass Objects (`Edge(source, target)`)**:
   - *Description*: Instantiating a dedicated object for every edge.
   - *Why Rejected*: For unweighted directed edges, separate Python class instances introduce significant memory overhead (Python object headers) and garbage collection overhead without adding any functional benefit. Plain string tuples or dictionary mappings are lighter and faster.

---

## 2. CSV Loader Design & Error Handling

### Decision
Implement the CSV loader in `src/loader.py` with:
- Standard library `csv.reader` reading a UTF-8 stream (using `utf-8-sig` encoding to handle optional UTF-8 BOM transparently).
- Physical line tracking via `reader.line_num` for all diagnostics.
- Separation of concerns: `load_graph_from_csv(path: str | Path) -> LoadResult`. The loader performs zero standard I/O (no `print`, no `sys.stderr.write`). It returns a container `LoadResult(graph: DirectedGraph, diagnostics: list[Diagnostic])`.
- Custom exception `GraphLoadError` raised exclusively on fatal validation failures.
- CLI in `src/cli.py` handles the presentation: it catches `GraphLoadError`, prints the formatted error message to `stderr`, and exits with status 1 without dumping a stack trace. On success, it prints all collected `diagnostics` to `stderr` in original input order, then prints the graph structure to `stdout`, and exits with status 0.

### Diagnostic Classification & Rule Resolution

| Irregularity | Level | Action Taken | Stderr Diagnostic Format |
|---|---|---|---|
| **Empty target (`watch,`)** | `NOTICE` | Add source as isolated vertex (in-degree 0, out-degree 0). | `Line {line}: added isolated vertex '{source}'` |
| **Duplicate edge** | `WARNING` | Record edge once; do not increment edge count. | `Line {line}: duplicate edge '{source} -> {target}' ignored` |
| **Padded whitespace** | `NOTICE` | Strip leading/trailing whitespace; use trimmed tokens. | `Line {line}: normalized vertex '{raw}' -> '{trimmed}'` |
| **Self-loops (`u -> u`)** | None | Allowed as valid directed edge in Feature 1. | None (accepted silently) |
| **Cycles (`u -> v -> u`)** | None | Allowed as valid directed edge in Feature 1. | None (accepted silently) |
| **Non-existent / unreadable path** | `ERROR` | Raise `GraphLoadError`; exit 1. | `Error: cannot read file '{path}': {reason}` |
| **Path is a directory** | `ERROR` | Raise `GraphLoadError`; exit 1. | `Error: path is a directory, not a file: '{path}'` |
| **Empty file (0 bytes)** | `ERROR` | Raise `GraphLoadError`; exit 1. | `Error: file is empty: '{path}'` |
| **Invalid header** | `ERROR` | Raise `GraphLoadError`; exit 1. | `Error: invalid header on line 1: expected 'source,target', got '{actual}'` |
| **Wrong column count (!= 2)** | `ERROR` | Raise `GraphLoadError`; exit 1. | `Error: line {line}: expected 2 columns, got {count}` |
| **Empty source value (`,target`)**| `ERROR` | Raise `GraphLoadError`; exit 1. | `Error: line {line}: source vertex name cannot be empty` |

### Open / Undefined Corner Cases Addressed
1. **Completely Blank Lines in CSV**:
   - *Decision*: If a row is completely blank (e.g. empty line or trailing newline), skip it with a diagnostic notice: `Line {line}: skipped empty line`.
2. **Whitespace-Only Target Field (`source,"   "`)**:
   - *Decision*: When trimmed, the target is empty string `""`. Handled identical to `source,`: treated as an isolated vertex declaration with a notice.
3. **Repeated Isolated Vertex Declarations (`watch,` twice)**:
   - *Decision*: First occurrence adds vertex and emits notice; subsequent occurrences emit a warning: `Line {line}: duplicate isolated vertex '{source}' ignored`.
4. **BOM / Non-UTF-8 Encoding**:
   - *Decision*: Files are opened with `encoding="utf-8-sig"`. If the file contains invalid byte sequences not decodable as UTF-8, catch `UnicodeDecodeError` and raise `GraphLoadError(f"File '{path}' is not valid UTF-8: {e}")`.

---

## 3. CLI Design & Formatter Contract

### Decision
- Standard library `argparse` entry point in `src/cli.py`.
- Invocation formats supported:
  - Default positional: `python3 -m src.cli <file.csv>`
  - Explicit subcommand: `python3 -m src.cli display <file.csv>`
- Output Formatting Rules:
  - Standard output (`stdout`):
    ```text
    Vertices (<V>):
      <vertex_1>
      <vertex_2>
    Edges (<E>):
      <source_1> -> <target_1>
      <source_2> -> <target_2>
    ```
    - Section header lines: `Vertices (<V>):` and `Edges (<E>):`.
    - Indentation: exactly 2 spaces (`  `).
    - Sorting: Vertices sorted lexicographically (`sorted(vertices)`). Edges sorted lexicographically by source, then target (`sorted(edges, key=lambda e: (e[0], e[1]))`).
    - Empty graph (0 vertices, 0 edges): prints `Vertices (0):` and `Edges (0):` with no child lines.
  - Standard error (`stderr`):
    - All diagnostic notices and warnings printed in order of physical line appearance.
    - Errors prefixed with `Error: `.
- Exit Codes:
  - `0`: Success (valid graph loaded and displayed).
  - `1`: Application/Domain error (file missing, corrupt header, malformed row).
  - `2`: Command-line usage error (missing required arguments, unrecognized options triggered by `argparse`).

---

## 4. Test Strategy & Oracle Verification

### Decision
- **Test-First Discipline (Constitution Principle II)**:
  - All tests written in `tests/` and verified failing prior to implementing corresponding modules.
- **Test Structure**:
  - `tests/unit/test_graph.py`: Direct unit tests on `DirectedGraph` methods (addition, idempotency, neighbor queries, in-degrees, cycle tolerance).
  - `tests/unit/test_loader.py`: Unit tests on `load_graph_from_csv` testing normal parsing, whitespace trimming, isolated vertices, duplicate edges, and specific `GraphLoadError` triggers.
  - `tests/integration/test_cli.py`: Subprocess invocation tests (`subprocess.run([sys.executable, "-m", "src.cli", ...])`) validating exact stdout formatting, stderr messages, and exit codes for all 3 sample files and edge case fixtures.
  - `tests/oracle/test_networkx_oracle.py`: Uses `networkx.DiGraph` to load the same CSV data and verify that `set(graph.vertices()) == set(nx_graph.nodes())` and `set(graph.edges()) == set(nx_graph.edges())`.
- **Performance Benchmarking (SC-001)**:
  - `tests/integration/test_performance.py`: Programmatically generates a synthetic CSV graph with 10,000 edges and verifies loading and display completes in under 1.0 second.
- **Deterministic Output Test (SC-002)**:
  - Runs CLI twice on `cs-curriculum.csv` and `build-with-cycle.csv`, asserting `res1.stdout == res2.stdout` and `res1.stderr == res2.stderr`.
