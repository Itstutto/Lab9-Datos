# Feature Specification: Directed Graphs (Loading & Display)

**Feature Branch**: `Feature1`

**Created**: 2026-10-30

**Status**: Ready for Planning

**Input**: User description: "Feature: Directed graphs. Users can load a directed, unweighted graph from a CSV file and display it: its vertices and its edges."

## Clarifications

### Session 2026-10-30

- Q: How should the application process a CSV row that has a source identifier but an empty target field, such as "watch," in small-dag.csv? → A: Add as an isolated vertex with no incident edges, and emit an informational notice to stderr.
- Q: How should the application handle repeated identical directed edges in an input CSV file, such as "Data Structures,Algorithms" in cs-curriculum.csv? → A: Warn to stderr with line number and deduplicate (store the edge once in the graph).
- Q: What should be the exact command-line invocation syntax and stdout display layout for showing vertices and edges? → A: Sectioned lists with counts and indented items (`Vertices (N):` and `Edges (M):` with `source -> target`), sorted alphabetically, invoked via `python3 -m src.cli <file.csv>` (or `python3 -m src.cli display <file.csv>`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load and Display Valid Directed Graph (Priority: P1)

A user provides a valid CSV file containing directed dependencies (such as course prerequisites, build orders, or task sequences) to the command-line application. The application reads the file, parses the vertices and directed edges, and prints the graph structure clearly to stdout, exiting successfully.

**Why this priority**: Loading and displaying a valid graph is the foundational capability of the application upon which all further graph operations and analysis depend.

**Independent Test**: Can be fully tested by providing `data/small-dag.csv` or any valid CSV and asserting that all vertices and edges appear in stdout in deterministic order with exit code 0.

**Acceptance Scenarios**:

1. **Given** a valid CSV file containing directed edges with header `source,target` (such as `data/small-dag.csv`), **When** the user runs `python3 -m src.cli <file.csv>`, **Then** the application outputs to stdout:
   ```text
   Vertices (<count>):
     <vertex_1>
     <vertex_2>
   Edges (<count>):
     <source_1> -> <target_1>
     <source_2> -> <target_2>
   ```
   with all vertices and edges sorted in lexicographical order, exiting with status code 0.
2. **Given** a CSV file containing only the header `source,target` and zero data rows, **When** the user runs the graph display command, **Then** the application outputs `Vertices (0):` and `Edges (0):` with no listed items to stdout and exits with status code 0.
3. **Given** a graph containing cycles and self-loops (such as `data/build-with-cycle.csv`), **When** the user runs the graph display command, **Then** the application successfully loads and displays all vertices and directed edges (including cyclic dependencies and self-loops like `metrics -> metrics`) in the sectioned output without error, exiting with status code 0.

---

### User Story 2 - Irregular Data Handling with Transparent Reporting (Priority: P2)

A user provides a CSV file containing irregularities or non-standard formatting (such as duplicate edges, whitespace padding around identifiers, or trailing commas). The application processes the valid data while transparently reporting each normalization or skipped irregularity to stderr, ensuring no data is silently changed or discarded.

**Why this priority**: Real-world data is messy and untrusted (Constitution Principle V). Users must be alerted to anomalies in their dependency data so they can understand and audit how the data was interpreted.

**Independent Test**: Can be tested by running the application with `data/cs-curriculum.csv` (containing duplicate edge `Data Structures,Algorithms`) and inputs with padded whitespace, asserting that warnings appear on stderr while valid graph results are output to stdout.

**Acceptance Scenarios**:

1. **Given** a CSV file containing duplicate edges (such as rows 11 and 25 in `data/cs-curriculum.csv`), **When** the user runs the graph display command, **Then** the application emits a descriptive warning to stderr indicating the line number and duplicated edge, stores the edge once in the graph model, and outputs the deduplicated graph to stdout with exit status 0.
2. **Given** a CSV file where vertex names contain leading or trailing whitespace (e.g. `" pants ", " shoes "`), **When** the user runs the graph display command, **Then** the application strips the extraneous whitespace, emits a diagnostic message to stderr noting the normalized vertex names, and uses the trimmed names in the graph.
3. **Given** a CSV file with an empty target field (such as `watch,` in `data/small-dag.csv`), **When** the user runs the graph display command, **Then** the application adds the source name as an isolated vertex in the graph with degree 0, creates no edge, emits an informational notice to stderr noting the isolated vertex addition, and displays the graph with exit status 0.

---

### User Story 3 - Actionable Error Feedback on Fatal Input Failures (Priority: P3)

A user provides an input file that cannot be parsed into a graph (for example, the file does not exist, is unreadable, is completely empty, has an invalid header, or has malformed rows with missing columns). The application immediately terminates with a clear, actionable error message on stderr and a non-zero exit status, without printing garbled output or unhandled exceptions.

**Why this priority**: Users need rapid, precise diagnostics when input cannot be processed, preventing corrupt data propagation and facilitating automated script error handling.

**Independent Test**: Can be tested by providing non-existent paths, 0-byte files, and invalid headers, asserting that exit status is non-zero and stderr contains a specific descriptive error message.

**Acceptance Scenarios**:

1. **Given** a file path that does not exist or cannot be accessed, **When** the user runs the graph display command, **Then** the application writes a descriptive error message to stderr indicating the file cannot be found or read, prints no graph output to stdout, and exits with a non-zero exit status.
2. **Given** a completely empty file (0 bytes), **When** the user runs the graph display command, **Then** the application writes an error message to stderr indicating the file is empty and missing the required header, and exits with a non-zero exit status.
3. **Given** a CSV file with an incorrect or missing header (e.g. `from,to` instead of `source,target`), **When** the user runs the graph display command, **Then** the application writes an error to stderr detailing that the header must be `source,target`, and exits with a non-zero exit status.
4. **Given** a row containing an invalid column count (e.g. more than 2 comma-separated fields) or an empty source field (e.g. `,target`), **When** the user runs the graph display command, **Then** the application reports a specific error detailing the line number and syntax problem to stderr and exits with a non-zero exit status.

---

### User Story 4 - Deterministic and Testable Output (Priority: P4)

A user or automated testing harness executes the application repeatedly with the same arguments and input data. The application guarantees byte-for-byte identical output on stdout and stderr across runs.

**Why this priority**: Determinism is required by Constitution Principle VI to make output reproducible and verifiable by automated tests.

**Independent Test**: Can be tested by executing the command twice on `data/cs-curriculum.csv` or `data/build-with-cycle.csv` and asserting that stdout and stderr outputs are byte-for-byte identical.

**Acceptance Scenarios**:

1. **Given** any valid or irregular graph file, **When** the command is executed multiple times with identical arguments, **Then** stdout outputs are identical in every run, with vertices and edges consistently sorted in predetermined lexicographical order.
2. **Given** an input file that triggers warnings or errors, **When** executed multiple times, **Then** the sequence, content, and formatting of stderr messages are strictly identical across runs.

---

### Edge Cases

- **Row with empty target (`watch,` in `data/small-dag.csv`)**: Source is present but target is empty string. Treated as an isolated vertex declaration: vertex is added with in-degree 0 and out-degree 0, zero edges are created, and an informational notice is emitted to stderr. Loading succeeds.
- **Duplicate directed edge (`Data Structures,Algorithms` in `data/cs-curriculum.csv`)**: Appears on line 11 and line 25. Reported with a warning to stderr detailing line number; the edge is stored once in the graph model.
- **Self-loops (`metrics,metrics` in `data/build-with-cycle.csv`)**: Source equals target. In Feature 1, this is represented as a valid directed edge `metrics -> metrics` and displayed under edges.
- **Directed cycles (`auth -> session -> user-profile -> auth` in `data/build-with-cycle.csv`)**: In Feature 1, cycles are valid directed graph topologies and are loaded and displayed without error.
- **Missing or unreadable file**: File path does not exist, points to a directory, or lacks read permissions. Must report error to stderr and exit with non-zero status.
- **Empty file (0 bytes)**: Completely empty. Reported as missing header/empty file on stderr, exit non-zero.
- **Header-only file**: Exactly 1 line `source,target`. Valid empty graph with 0 vertices and 0 edges.
- **Missing or invalid header**: Header line does not match `source,target` (e.g. `Source,Target`, `origin,destination`, or missing entirely). Reported to stderr, exit non-zero.
- **Malformed row (column count != 2)**: Row with 1 column or 3+ columns (e.g. `a,b,c`). Reported to stderr with line number; execution terminates with non-zero status.
- **Empty source value (`,target` or `  ,target`)**: Cannot establish edge source. Reported to stderr with line number, exit non-zero.
- **Whitespace-only values (`"   ",target` or `source,"   "`):** Treated as empty value; reported to stderr.
- **Padded whitespace (`"  math  "," cs "`):** Trimmed with diagnostic message to stderr; normalized tokens become graph vertices.
- **Case sensitivity:** Vertex names with differing casing (e.g., `Core` vs `core`) are treated as distinct vertices.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST accept a path to a CSV file as a command-line argument (supporting invocation as `python3 -m src.cli <file.csv>` as well as optional subcommand format `python3 -m src.cli display <file.csv>`).
- **FR-002**: The application MUST validate that the first line of the input CSV file is a header row containing exactly `source,target`. If the header is missing or does not match, the application MUST write a descriptive error to stderr and exit with status 1.
- **FR-003**: The application MUST parse each valid two-column data row as a directed edge from `source` to `target`.
- **FR-004**: The application MUST treat a data row containing a non-empty source and an empty target field (e.g. `watch,`) as an isolated vertex declaration: the source vertex MUST be added to the graph with no incident edges, an informational notice MUST be emitted to stderr (specifying line number and vertex name), and execution MUST continue successfully with status 0.
- **FR-005**: The application MUST detect duplicate directed edges in the input file. When a duplicate edge is encountered, the application MUST store the edge once in the graph model, emit a warning to stderr detailing the line number and the duplicated edge (`source -> target`), and continue execution without error.
- **FR-006**: The application MUST trim leading and trailing whitespace from vertex names. If any vertex name was padded with whitespace, the application MUST emit a diagnostic notice to stderr describing the normalization performed.
- **FR-007**: The application MUST allow directed self-loops (edges where source equals target) and directed cycles as valid edges in the directed graph structure.
- **FR-008**: The application MUST display the loaded graph on stdout structured in two distinct sections with element counts:
  1. A `Vertices (<count>):` section listing each unique vertex sorted in ascending lexicographical order, indented by 2 spaces.
  2. An `Edges (<count>):` section listing each directed edge formatted as `<source> -> <target>` sorted lexicographically by source then target, indented by 2 spaces.
  If the graph has 0 vertices or 0 edges, the count MUST show `(0)` and no indented items under that section.
- **FR-009**: The application MUST ensure all vertex listings and edge listings in stdout are strictly deterministic (lexicographically sorted).
- **FR-010**: The application MUST direct all successful graph output and summaries to stdout, and all diagnostic notices, warnings, and error messages to stderr.
- **FR-011**: The application MUST exit with status code 0 when the graph is loaded and displayed successfully, and exit with status code 1 when encountering fatal errors (missing file, invalid header, or fatal row syntax errors).

### Key Entities *(include if feature involves data)*

- **Vertex**: A unique, named entity representing a node in the dependency graph (e.g., a course, software package, or garment). Uniquely identified by its trimmed, case-sensitive string label.
- **Directed Edge**: An ordered pair `(source, target)` representing a directed dependency from the `source` vertex to the `target` vertex.
- **Directed Graph**: A discrete mathematical structure composed of a set of unique vertices and a set of directed edges connecting them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid CSV input graphs (including standard sample datasets `small-dag.csv`, `cs-curriculum.csv`, and `build-with-cycle.csv`) load and display within 1 second for graphs containing up to 10,000 edges.
- **SC-002**: For identical input files and arguments, repeated executions produce 100% byte-for-byte identical output on both stdout and stderr.
- **SC-003**: 100% of input data irregularities (whitespace padding, duplicate edges, malformed rows) trigger an informative, human-readable message on stderr—zero silent modifications or silent drops.
- **SC-004**: 100% of unrecoverable errors (missing file, empty file, incorrect header, malformed row) terminate with a non-zero exit code and a clear error message on stderr without an unhandled stack trace.
- **SC-005**: All acceptance scenarios can be asserted by automated tests examining stdout, stderr, and process exit codes without access to application internals.

## Assumptions

- **Encoding**: Input CSV files are encoded in UTF-8 or ASCII.
- **File Access**: The application executes with standard filesystem read permissions for the provided file path.
- **Scope Limitations**: Graph visualization (rendering graphics or diagrams) is out of scope; output is text-based CLI. Edge weights and computing topological orders are out of scope for Feature 1.
- **Memory**: The entire graph dataset fits within available system memory.
