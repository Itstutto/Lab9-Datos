# Quickstart Validation Guide: Directed Graphs (Loading & Display)

**Feature**: Directed Graphs (Loading & Display)  
**Branch**: `001-directed-graphs`  
**Date**: 2026-11-02  

This guide provides step-by-step instructions for running, testing, and validating Feature 1 end-to-end.

---

## 1. Prerequisites & Environment Setup

- **Python**: Version 3.11 or newer.
- **Virtual Environment** (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest ruff networkx
```

Verify that code passes static analysis:

```bash
ruff check .
ruff format --check .
```

---

## 2. Running Automated Tests

Run the full pytest suite (including unit tests, integration subprocess tests, deterministic reproduction tests, and NetworkX oracle validation):

```bash
pytest -v
```

---

## 3. End-to-End CLI Verification Scenarios

### Scenario 1: Loading `data/small-dag.csv` (Isolated Vertex Handling)

```bash
python3 -m src.cli data/small-dag.csv
```

**Expected Exit Code**: `0`

**Expected `stderr`**:
```text
Line 11: added isolated vertex 'watch'
```

**Expected `stdout`**:
```text
Vertices (9):
  belt
  jacket
  pants
  shirt
  shoes
  socks
  tie
  undershorts
  watch
Edges (9):
  belt -> jacket
  pants -> belt
  pants -> shoes
  shirt -> belt
  shirt -> tie
  socks -> shoes
  tie -> jacket
  undershorts -> pants
  undershorts -> shoes
```

---

### Scenario 2: Loading `data/cs-curriculum.csv` (Duplicate Edge Deduplication)

```bash
python3 -m src.cli data/cs-curriculum.csv
```

**Expected Exit Code**: `0`

**Expected `stderr`**:
```text
Line 25: duplicate edge 'Data Structures -> Algorithms' ignored
```

**Expected `stdout`**:
```text
Vertices (16):
  Algorithms
  Calculus I
  Calculus II
  Capstone Project
  Compilers
  Computer Architecture
  Computer Networks
  Data Structures
  Databases
  Discrete Mathematics
  Distributed Systems
  Linear Algebra
  Machine Learning
  Object-Oriented Programming
  Operating Systems
  Probability and Statistics
  Programming Fundamentals
  Software Engineering
  Theory of Computation
Edges (23):
  Algorithms -> Compilers
  Algorithms -> Machine Learning
  Calculus I -> Calculus II
  Calculus I -> Linear Algebra
  Calculus II -> Probability and Statistics
  Computer Architecture -> Operating Systems
  Computer Networks -> Distributed Systems
  Data Structures -> Algorithms
  Data Structures -> Databases
  Data Structures -> Operating Systems
  Databases -> Software Engineering
  Discrete Mathematics -> Data Structures
  Discrete Mathematics -> Theory of Computation
  Distributed Systems -> Capstone Project
  Linear Algebra -> Machine Learning
  Object-Oriented Programming -> Data Structures
  Object-Oriented Programming -> Software Engineering
  Operating Systems -> Distributed Systems
  Probability and Statistics -> Machine Learning
  Programming Fundamentals -> Computer Architecture
  Programming Fundamentals -> Object-Oriented Programming
  Software Engineering -> Capstone Project
  Theory of Computation -> Compilers
```

---

### Scenario 3: Loading `data/build-with-cycle.csv` (Cycles & Self-Loops)

```bash
python3 -m src.cli data/build-with-cycle.csv
```

**Expected Exit Code**: `0`

**Expected `stderr`**: *(empty)*

**Expected `stdout`**:
```text
Vertices (9):
  api
  auth
  config
  core
  logging
  metrics
  session
  storage
  user-profile
  utils
  web
Edges (13):
  api -> web
  auth -> api
  auth -> session
  config -> core
  core -> auth
  core -> storage
  logging -> core
  metrics -> metrics
  session -> user-profile
  storage -> api
  user-profile -> auth
  utils -> config
  utils -> logging
```

---

### Scenario 4: Error Handling on Invalid Input

#### 4a. Non-Existent File
```bash
python3 -m src.cli non_existent_file.csv
```
- **Exit Code**: `1`
- **`stderr`**: `Error: cannot read file 'non_existent_file.csv': No such file or directory`

#### 4b. Missing or Invalid Header
```bash
python3 -m src.cli tests/data/invalid_header.csv
```
- **Exit Code**: `1`
- **`stderr`**: `Error: invalid header on line 1: expected 'source,target', got ...`
