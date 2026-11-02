# CLI Interface Contract: Directed Graphs (Loading & Display)

**Feature**: Directed Graphs (Loading & Display)  
**Contract Version**: `1.0.0`  
**Date**: 2026-11-02  

---

## 1. Invocation Syntax

The command-line interface is invoked using Python 3.11+:

```bash
# Default invocation with positional file argument:
python3 -m src.cli <file.csv>

# Explicit display subcommand:
python3 -m src.cli display <file.csv>

# Help options:
python3 -m src.cli --help
python3 -m src.cli display --help
```

### Arguments
- `file`: Positional argument indicating the filesystem path to the CSV graph file to load.
- `--help` / `-h`: Displays standard usage information and exits.

---

## 2. Exit Codes

| Exit Code | Meaning | Triggers |
|---|---|---|
| `0` | Success | Graph was successfully loaded and displayed. Non-fatal warnings or notices may have been output to `stderr`. |
| `1` | Fatal Application / Domain Error | Input file was missing, empty, unreadable, had an invalid header, or contained a fatal row syntax error. A descriptive error message was written to `stderr`. |
| `2` | CLI Usage / Argument Error | Triggered automatically by `argparse` when arguments are missing, extra unrecognized arguments are provided, or invalid CLI flags are passed. Usage information was written to `stderr`. |

---

## 3. Standard Output (`stdout`) Contract

All successful graph presentation data is written exclusively to `stdout`.

### Format Structure

```text
Vertices (<V>):
  <vertex_1>
  <vertex_2>
  ...
Edges (<E>):
  <source_1> -> <target_1>
  <source_2> -> <target_2>
  ...
```

### Formatting Rules
1. **Section Headers**:
   - `Vertices (<V>):` where `<V>` is the integer count of unique vertices in the graph.
   - `Edges (<E>):` where `<E>` is the integer count of unique directed edges in the graph.
2. **Item Indentation**:
   - Every vertex and edge item is indented by exactly two spaces (`  `).
3. **Deterministic Ordering (Principle VI)**:
   - Vertices are sorted in ascending lexicographical order (`sorted(vertices)`).
   - Edges are formatted as `<source> -> <target>` and sorted lexicographically in ascending order, first by `source`, and then by `target` for edges with identical sources.
4. **Empty Graphs**:
   - When $|V| = 0$ and $|E| = 0$, the output is:
     ```text
     Vertices (0):
     Edges (0):
     ```
   - No blank lines or child lines are printed under the headers.

---

## 4. Standard Error (`stderr`) Contract

All diagnostics, notices, warnings, and error messages are written exclusively to `stderr`.

### 4.1 Non-Fatal Diagnostics
Diagnostics are output in the exact order in which they are encountered in the input file.

- **Isolated Vertex Declaration**:
  ```text
  Line {line_num}: added isolated vertex '{vertex}'
  ```
- **Duplicate Directed Edge**:
  ```text
  Line {line_num}: duplicate edge '{source} -> {target}' ignored
  ```
- **Whitespace Normalization**:
  ```text
  Line {line_num}: normalized vertex '{raw}' -> '{trimmed}'
  ```
- **Skipped Blank Line**:
  ```text
  Line {line_num}: skipped empty line
  ```

### 4.2 Fatal Error Messages
When a fatal error occurs, execution terminates immediately, no graph output is printed to `stdout`, and a single line is written to `stderr`:

- **Missing / Unreadable File**:
  ```text
  Error: cannot read file '{path}': [reason]
  ```
- **Path is a Directory**:
  ```text
  Error: path is a directory, not a file: '{path}'
  ```
- **Empty File (0 bytes)**:
  ```text
  Error: file is empty: '{path}'
  ```
- **Invalid Header**:
  ```text
  Error: invalid header on line 1: expected 'source,target', got '{actual_header}'
  ```
- **Wrong Column Count**:
  ```text
  Error: line {line_num}: expected 2 columns, got {count}
  ```
- **Empty Source Field**:
  ```text
  Error: line {line_num}: source vertex name cannot be empty
  ```
