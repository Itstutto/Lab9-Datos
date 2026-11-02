"""CSV loader, data validation, and diagnostic tracking for DirectedGraph."""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from src.graph import DirectedGraph

DiagnosticLevel = Literal["NOTICE", "WARNING"]


@dataclass(frozen=True)
class Diagnostic:
    """Represents a non-fatal observation made during CSV loading."""

    line_num: int
    level: DiagnosticLevel
    message: str


@dataclass
class LoadResult:
    """Container returned by the loader with the graph and collected diagnostics."""

    graph: DirectedGraph
    diagnostics: list[Diagnostic] = field(default_factory=list)


class GraphLoadError(Exception):
    """Raised when encountering an unrecoverable failure during graph loading."""

    def __init__(self, message: str, line_num: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.line_num = line_num


def load_graph_from_csv(path: str | Path) -> LoadResult:
    """Load and validate a directed unweighted graph from a CSV file.

    Zero direct printing to stdout or stderr.
    All non-fatal diagnostics are collected and returned in encounter order.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise GraphLoadError(f"cannot read file '{file_path}': No such file or directory")
    if file_path.is_dir():
        raise GraphLoadError(f"path is a directory, not a file: '{file_path}'")

    try:
        content = file_path.read_bytes()
    except PermissionError as e:
        raise GraphLoadError(f"cannot read file '{file_path}': Permission denied") from e
    except OSError as e:
        raise GraphLoadError(f"cannot read file '{file_path}': {e}") from e

    if len(content) == 0:
        raise GraphLoadError(f"file is empty: '{file_path}'")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise GraphLoadError(f"cannot read file '{file_path}': invalid UTF-8 encoding ({e})") from e

    lines = text.splitlines()
    if not lines:
        raise GraphLoadError(f"file is empty: '{file_path}'")

    reader = csv.reader(lines)
    graph = DirectedGraph()
    diagnostics: list[Diagnostic] = []

    try:
        header = next(reader)
    except StopIteration:
        raise GraphLoadError(f"file is empty: '{file_path}'") from None

    # Validate header row
    if header != ["source", "target"]:
        actual_header = ",".join(header)
        raise GraphLoadError(
            f"invalid header on line 1: expected 'source,target', got '{actual_header}'",
            line_num=1,
        )

    for row_idx, row in enumerate(reader, start=2):
        if len(row) == 0:
            diagnostics.append(
                Diagnostic(
                    line_num=row_idx,
                    level="NOTICE",
                    message=f"Line {row_idx}: skipped empty line",
                )
            )
            continue

        if len(row) != 2:
            raise GraphLoadError(
                f"line {row_idx}: expected 2 columns, got {len(row)}",
                line_num=row_idx,
            )

        raw_source, raw_target = row[0], row[1]
        source = raw_source.strip()
        target = raw_target.strip()

        # Check for whitespace normalization
        if raw_source != source:
            diagnostics.append(
                Diagnostic(
                    line_num=row_idx,
                    level="NOTICE",
                    message=f"Line {row_idx}: normalized vertex '{raw_source}' -> '{source}'",
                )
            )
        if raw_target != target and raw_target != "":
            diagnostics.append(
                Diagnostic(
                    line_num=row_idx,
                    level="NOTICE",
                    message=f"Line {row_idx}: normalized vertex '{raw_target}' -> '{target}'",
                )
            )

        if not source:
            raise GraphLoadError(
                f"line {row_idx}: source vertex name cannot be empty",
                line_num=row_idx,
            )

        # Empty target denotes an isolated vertex
        if not target:
            is_new = graph.add_vertex(source)
            if is_new:
                diagnostics.append(
                    Diagnostic(
                        line_num=row_idx,
                        level="NOTICE",
                        message=f"Line {row_idx}: added isolated vertex '{source}'",
                    )
                )
            else:
                diagnostics.append(
                    Diagnostic(
                        line_num=row_idx,
                        level="WARNING",
                        message=f"Line {row_idx}: duplicate isolated vertex '{source}' ignored",
                    )
                )
            continue

        # Standard directed edge
        is_new_edge = graph.add_edge(source, target)
        if not is_new_edge:
            diagnostics.append(
                Diagnostic(
                    line_num=row_idx,
                    level="WARNING",
                    message=f"Line {row_idx}: duplicate edge '{source} -> {target}' ignored",
                )
            )

    return LoadResult(graph=graph, diagnostics=diagnostics)
