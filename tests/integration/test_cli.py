"""Integration tests for the CLI via subprocess execution."""

import subprocess
import sys
from pathlib import Path


class TestCLIUserStory1:
    """Acceptance tests for User Story 1 (Valid Graph Display)."""

    def test_display_header_only_empty_graph(self, test_data_dir: Path) -> None:
        """Header-only CSV displays empty vertices and edges sections with count (0)."""
        csv_file = str(test_data_dir / "header_only.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )

        assert proc.returncode == 0
        expected_stdout = "Vertices (0):\nEdges (0):\n"
        assert proc.stdout == expected_stdout
        assert proc.stderr == ""

    def test_display_build_with_cycle(self, sample_data_dir: Path) -> None:
        """Cycles and self-loops display in alphabetical order with exit code 0."""
        csv_file = str(sample_data_dir / "build-with-cycle.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )

        assert proc.returncode == 0
        assert "Vertices (11):" in proc.stdout
        assert "Edges (13):" in proc.stdout
        assert "  metrics -> metrics" in proc.stdout

        lines = proc.stdout.splitlines()
        v_idx = lines.index("Vertices (11):")
        e_idx = lines.index("Edges (13):")

        vertices = lines[v_idx + 1 : e_idx]
        edges = lines[e_idx + 1 :]

        assert len(vertices) == 11
        assert len(edges) == 13

        # Assert 2-space indentation
        assert all(line.startswith("  ") and not line.startswith("   ") for line in vertices)
        assert all(line.startswith("  ") and not line.startswith("   ") for line in edges)

        # Assert lexicographical sorting
        v_names = [v.strip() for v in vertices]
        assert v_names == sorted(v_names)

        e_pairs = [e.strip() for e in edges]
        assert e_pairs == sorted(e_pairs)

    def test_display_subcommand_syntax(self, sample_data_dir: Path) -> None:
        """Explicit display subcommand works identical to default invocation."""
        csv_file = str(sample_data_dir / "build-with-cycle.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", "display", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0
        assert "Vertices (11):" in proc.stdout


class TestCLIUserStory2:
    """Acceptance tests for User Story 2 (Irregular Data and Transparent Reporting)."""

    def test_display_small_dag_with_isolated_vertex(self, sample_data_dir: Path) -> None:
        """Row 11 'watch,' creates isolated vertex, outputs notice on stderr, exits 0."""
        csv_file = str(sample_data_dir / "small-dag.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )

        assert proc.returncode == 0
        assert "Vertices (9):" in proc.stdout
        assert "  watch" in proc.stdout
        assert "Edges (9):" in proc.stdout
        assert "Line 11: added isolated vertex 'watch'" in proc.stderr

    def test_display_cs_curriculum_duplicate_edge(self, sample_data_dir: Path) -> None:
        """Duplicate edge on line 25 emits warning on stderr, deduplicates on stdout."""
        csv_file = str(sample_data_dir / "cs-curriculum.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )

        assert proc.returncode == 0
        assert "Vertices (19):" in proc.stdout
        assert "Edges (23):" in proc.stdout
        assert "Line 25: duplicate edge 'Data Structures -> Algorithms' ignored" in proc.stderr

    def test_display_padded_whitespace(self, test_data_dir: Path) -> None:
        """Surrounding whitespace is trimmed and reported on stderr."""
        csv_file = str(test_data_dir / "padded_whitespace.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )

        assert proc.returncode == 0
        assert "Vertices (4):" in proc.stdout
        assert "  undershorts" in proc.stdout
        assert "  pants" in proc.stdout
        assert "Line 2: normalized vertex '  undershorts  ' -> 'undershorts'" in proc.stderr


class TestCLIUserStory3:
    """Acceptance tests for User Story 3 (Actionable Error Feedback on Fatal Input Failures)."""

    def test_cli_missing_file_error(self, test_data_dir: Path) -> None:
        """Non-existent file exits 1 with error on stderr and empty stdout."""
        missing_file = str(test_data_dir / "non_existent.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", missing_file],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 1
        assert proc.stdout == ""
        assert "Error: cannot read file" in proc.stderr
        assert "Traceback" not in proc.stderr

    def test_cli_directory_path_error(self, test_data_dir: Path) -> None:
        """Passing a directory path exits 1 with error on stderr."""
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", str(test_data_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 1
        assert proc.stdout == ""
        assert "Error: path is a directory, not a file" in proc.stderr
        assert "Traceback" not in proc.stderr

    def test_cli_empty_file_error(self, test_data_dir: Path) -> None:
        """A 0-byte file exits 1 with error on stderr."""
        empty_file = str(test_data_dir / "empty_file.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", empty_file],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 1
        assert proc.stdout == ""
        assert "Error: file is empty" in proc.stderr
        assert "Traceback" not in proc.stderr

    def test_cli_invalid_header_error(self, test_data_dir: Path) -> None:
        """A file with an invalid header exits 1 with line 1 error on stderr."""
        invalid_header = str(test_data_dir / "invalid_header.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", invalid_header],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 1
        assert proc.stdout == ""
        assert "Error: invalid header on line 1: expected 'source,target'" in proc.stderr
        assert "Traceback" not in proc.stderr

    def test_cli_wrong_column_count_error(self, test_data_dir: Path) -> None:
        """A row with 3 columns exits 1 with line number error on stderr."""
        wrong_cols = str(test_data_dir / "wrong_columns.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", wrong_cols],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 1
        assert proc.stdout == ""
        assert "Error: line 2: expected 2 columns, got 3" in proc.stderr
        assert "Traceback" not in proc.stderr

    def test_cli_empty_source_error(self, test_data_dir: Path) -> None:
        """A row with an empty source vertex exits 1 with line number error on stderr."""
        empty_src = str(test_data_dir / "empty_source.csv")
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli", empty_src],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 1
        assert proc.stdout == ""
        assert "Error: line 2: source vertex name cannot be empty" in proc.stderr
        assert "Traceback" not in proc.stderr

    def test_cli_usage_error_no_arguments(self) -> None:
        """Running with no arguments exits 2 with usage instructions on stderr."""
        proc = subprocess.run(
            [sys.executable, "-m", "src.cli"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 2
        assert "usage:" in proc.stderr.lower() or "error:" in proc.stderr.lower()


class TestCLIUserStory4:
    """Acceptance tests for User Story 4 (Deterministic and Testable Output)."""

    def test_repeated_invocations_produce_identical_output(self, sample_data_dir: Path) -> None:
        """Running CLI twice on cs-curriculum.csv produces byte-for-byte identical streams."""
        csv_file = str(sample_data_dir / "cs-curriculum.csv")

        run1 = subprocess.run(
            [sys.executable, "-m", "src.cli", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )
        run2 = subprocess.run(
            [sys.executable, "-m", "src.cli", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )

        assert run1.returncode == 0
        assert run2.returncode == 0
        assert run1.stdout == run2.stdout
        assert run1.stderr == run2.stderr
        assert len(run1.stdout) > 0
        assert len(run1.stderr) > 0

    def test_repeated_invocations_with_cycles_identical(self, sample_data_dir: Path) -> None:
        """Running CLI twice on build-with-cycle.csv produces byte-for-byte identical output."""
        csv_file = str(sample_data_dir / "build-with-cycle.csv")

        run1 = subprocess.run(
            [sys.executable, "-m", "src.cli", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )
        run2 = subprocess.run(
            [sys.executable, "-m", "src.cli", csv_file],
            capture_output=True,
            text=True,
            check=False,
        )

        assert run1.returncode == 0
        assert run2.returncode == 0
        assert run1.stdout == run2.stdout
        assert run1.stderr == run2.stderr
