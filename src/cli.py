"""Command-line interface entry point for DirectedGraph application."""

import argparse
import sys
from collections.abc import Sequence

from src.loader import GraphLoadError, load_graph_from_csv


def parse_arguments(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments supporting default positional file and display subcommand."""
    raw_args = list(sys.argv[1:] if args is None else args)

    # Normalize: if first positional argument is not a known flag or subcommand, default to display
    if raw_args and not raw_args[0].startswith("-") and raw_args[0] != "display":
        raw_args = ["display"] + raw_args

    parser = argparse.ArgumentParser(
        prog="graph-cli",
        description="Load and display directed dependency graphs from CSV files.",
    )

    subparsers = parser.add_subparsers(dest="command")

    display_parser = subparsers.add_parser(
        "display",
        help="Load and display vertices and edges of a directed graph.",
    )
    display_parser.add_argument(
        "file",
        help="Path to the CSV dependency graph file",
    )

    return parser.parse_args(raw_args)


def main(args: Sequence[str] | None = None) -> int:
    """Main CLI execution routine."""
    try:
        parsed = parse_arguments(args)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    if not parsed.command or not getattr(parsed, "file", None):
        sys.stderr.write("Error: missing required graph file argument\n")
        return 2

    try:
        result = load_graph_from_csv(parsed.file)
    except GraphLoadError as exc:
        sys.stderr.write(f"Error: {exc.message}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1

    # Output diagnostics to stderr in original encounter order
    for diag in result.diagnostics:
        sys.stderr.write(f"{diag.message}\n")

    # Output graph structure to stdout with deterministic lexicographical ordering
    graph = result.graph
    vertices = sorted(graph.vertices())
    edges = sorted(graph.edges(), key=lambda e: (e[0], e[1]))

    sys.stdout.write(f"Vertices ({len(vertices)}):\n")
    for vertex in vertices:
        sys.stdout.write(f"  {vertex}\n")

    sys.stdout.write(f"Edges ({len(edges)}):\n")
    for source, target in edges:
        sys.stdout.write(f"  {source} -> {target}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
