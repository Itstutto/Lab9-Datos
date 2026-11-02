"""Unit tests for the CSV loader."""

from pathlib import Path

import pytest

from src.loader import Diagnostic, GraphLoadError, load_graph_from_csv


class TestLoaderValidGraph:
    """Test suite for valid graph loading and basic parsing (User Story 1)."""

    def test_load_header_only_file(self, test_data_dir: Path) -> None:
        """A CSV file containing only 'source,target' produces an empty graph."""
        csv_path = test_data_dir / "header_only.csv"
        result = load_graph_from_csv(csv_path)

        assert result.graph.order() == 0
        assert result.graph.size() == 0
        assert result.graph.vertices() == set()
        assert result.graph.edges() == set()
        assert result.diagnostics == []

    def test_load_build_with_cycle_file(self, sample_data_dir: Path) -> None:
        """Valid file with cycles and self-loops loads properly with zero diagnostics."""
        csv_path = sample_data_dir / "build-with-cycle.csv"
        result = load_graph_from_csv(csv_path)

        assert result.graph.order() == 11
        assert result.graph.size() == 13
        assert result.graph.has_edge("metrics", "metrics") is True  # self-loop
        assert result.graph.has_edge("auth", "session") is True  # cycle part
        assert result.graph.has_edge("session", "user-profile") is True
        assert result.graph.has_edge("user-profile", "auth") is True
        assert result.diagnostics == []


class TestLoaderIrregularities:
    """Test suite for handling irregular CSV data and diagnostics (User Story 2)."""

    def test_load_small_dag_with_isolated_vertex(self, sample_data_dir: Path) -> None:
        """Row with empty target (watch,) creates isolated vertex and emits a notice."""
        csv_path = sample_data_dir / "small-dag.csv"
        result = load_graph_from_csv(csv_path)

        assert result.graph.order() == 9
        assert result.graph.size() == 9
        assert result.graph.has_vertex("watch") is True
        assert result.graph.in_degree("watch") == 0
        assert result.graph.out_degree("watch") == 0

        assert len(result.diagnostics) == 1
        expected_diag = Diagnostic(
            line_num=11,
            level="NOTICE",
            message="Line 11: added isolated vertex 'watch'",
        )
        assert result.diagnostics[0] == expected_diag

    def test_load_cs_curriculum_duplicate_edge(self, sample_data_dir: Path) -> None:
        """Duplicate edge on line 25 generates a warning and is stored once."""
        csv_path = sample_data_dir / "cs-curriculum.csv"
        result = load_graph_from_csv(csv_path)

        assert result.graph.order() == 19
        assert result.graph.size() == 23
        assert len(result.diagnostics) == 1
        expected_diag = Diagnostic(
            line_num=25,
            level="WARNING",
            message="Line 25: duplicate edge 'Data Structures -> Algorithms' ignored",
        )
        assert result.diagnostics[0] == expected_diag

    def test_load_padded_whitespace(self, test_data_dir: Path) -> None:
        """Whitespace surrounding vertex names is trimmed and reported with notices."""
        csv_path = test_data_dir / "padded_whitespace.csv"
        result = load_graph_from_csv(csv_path)

        assert result.graph.has_vertex("undershorts") is True
        assert result.graph.has_vertex("pants") is True
        assert result.graph.has_vertex("shirt") is True
        assert result.graph.has_vertex("belt") is True

        # Notices for line 2 ('  undershorts  ', ' pants ') and line 3 (' belt')
        messages = [d.message for d in result.diagnostics]
        assert any("normalized vertex '  undershorts  ' -> 'undershorts'" in m for m in messages)
        assert any("normalized vertex ' pants ' -> 'pants'" in m for m in messages)
        assert any("normalized vertex ' belt' -> 'belt'" in m for m in messages)


class TestLoaderFatalErrors:
    """Test suite for fatal error detection and GraphLoadError exceptions (User Story 3)."""

    def test_missing_file_raises_error(self, test_data_dir: Path) -> None:
        """Non-existent path raises GraphLoadError with descriptive message."""
        missing_path = test_data_dir / "non_existent.csv"
        with pytest.raises(GraphLoadError) as exc_info:
            load_graph_from_csv(missing_path)
        assert "cannot read file" in exc_info.value.message
        assert "No such file or directory" in exc_info.value.message

    def test_directory_path_raises_error(self, test_data_dir: Path) -> None:
        """Providing a directory path instead of a file raises GraphLoadError."""
        with pytest.raises(GraphLoadError) as exc_info:
            load_graph_from_csv(test_data_dir)
        assert "path is a directory, not a file" in exc_info.value.message

    def test_empty_file_raises_error(self, test_data_dir: Path) -> None:
        """A 0-byte file raises GraphLoadError."""
        empty_path = test_data_dir / "empty_file.csv"
        with pytest.raises(GraphLoadError) as exc_info:
            load_graph_from_csv(empty_path)
        assert "file is empty" in exc_info.value.message

    def test_invalid_header_raises_error(self, test_data_dir: Path) -> None:
        """A CSV file with an incorrect header row raises GraphLoadError on line 1."""
        invalid_path = test_data_dir / "invalid_header.csv"
        with pytest.raises(GraphLoadError) as exc_info:
            load_graph_from_csv(invalid_path)
        assert "invalid header on line 1: expected 'source,target'" in exc_info.value.message
        assert exc_info.value.line_num == 1

    def test_wrong_column_count_raises_error(self, test_data_dir: Path) -> None:
        """A row with 3 or more columns raises GraphLoadError identifying the line number."""
        wrong_cols_path = test_data_dir / "wrong_columns.csv"
        with pytest.raises(GraphLoadError) as exc_info:
            load_graph_from_csv(wrong_cols_path)
        assert "line 2: expected 2 columns, got 3" in exc_info.value.message
        assert exc_info.value.line_num == 2

    def test_empty_source_raises_error(self, test_data_dir: Path) -> None:
        """A row with an empty source vertex raises GraphLoadError on that line."""
        empty_src_path = test_data_dir / "empty_source.csv"
        with pytest.raises(GraphLoadError) as exc_info:
            load_graph_from_csv(empty_src_path)
        assert "source vertex name cannot be empty" in exc_info.value.message
        assert exc_info.value.line_num == 2
