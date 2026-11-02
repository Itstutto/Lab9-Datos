"""Unit tests for the DirectedGraph data structure."""

import pytest

from src.graph import DirectedGraph


class TestDirectedGraph:
    """Test suite for DirectedGraph core operations, invariants, and edge cases."""

    def test_empty_graph_initialization(self) -> None:
        """A new graph has order 0 and size 0, with empty vertices and edges sets."""
        graph = DirectedGraph()
        assert graph.order() == 0
        assert graph.size() == 0
        assert graph.vertices() == set()
        assert graph.edges() == set()

    def test_add_vertex(self) -> None:
        """Adding a vertex adds it to vertices and returns True; repeat returns False."""
        graph = DirectedGraph()
        assert graph.add_vertex("A") is True
        assert graph.order() == 1
        assert graph.has_vertex("A") is True
        assert graph.vertices() == {"A"}

        # Repeat addition is idempotent
        assert graph.add_vertex("A") is False
        assert graph.order() == 1

    def test_add_edge_and_implicit_vertex_creation(self) -> None:
        """Adding an edge implicitly creates source and target vertices."""
        graph = DirectedGraph()
        assert graph.add_edge("A", "B") is True
        assert graph.order() == 2
        assert graph.size() == 1
        assert graph.has_vertex("A") is True
        assert graph.has_vertex("B") is True
        assert graph.has_edge("A", "B") is True
        assert graph.has_edge("B", "A") is False
        assert graph.edges() == {("A", "B")}

        # Duplicate edge addition returns False and does not increase size
        assert graph.add_edge("A", "B") is False
        assert graph.size() == 1

    def test_successors_and_predecessors(self) -> None:
        """Successors and predecessors correctly reflect directed adjacency."""
        graph = DirectedGraph()
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        graph.add_edge("B", "C")

        assert graph.successors("A") == {"B", "C"}
        assert graph.successors("B") == {"C"}
        assert graph.successors("C") == set()

        assert graph.predecessors("A") == set()
        assert graph.predecessors("B") == {"A"}
        assert graph.predecessors("C") == {"A", "B"}

    def test_in_degree_and_out_degree(self) -> None:
        """Degrees match number of incident incoming and outgoing directed edges."""
        graph = DirectedGraph()
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        graph.add_edge("B", "C")

        assert graph.out_degree("A") == 2
        assert graph.in_degree("A") == 0

        assert graph.out_degree("B") == 1
        assert graph.in_degree("B") == 1

        assert graph.out_degree("C") == 0
        assert graph.in_degree("C") == 2

    def test_isolated_vertex_degrees(self) -> None:
        """An isolated vertex has in-degree 0 and out-degree 0."""
        graph = DirectedGraph()
        graph.add_vertex("isolated")
        assert graph.in_degree("isolated") == 0
        assert graph.out_degree("isolated") == 0
        assert graph.successors("isolated") == set()
        assert graph.predecessors("isolated") == set()

    def test_self_loops(self) -> None:
        """Self-loops (u -> u) are valid edges in an unweighted directed graph."""
        graph = DirectedGraph()
        assert graph.add_edge("A", "A") is True
        assert graph.order() == 1
        assert graph.size() == 1
        assert graph.has_edge("A", "A") is True
        assert graph.successors("A") == {"A"}
        assert graph.predecessors("A") == {"A"}
        assert graph.in_degree("A") == 1
        assert graph.out_degree("A") == 1

    def test_cycles(self) -> None:
        """Directed cycles (A -> B -> A) are valid and preserved in the model."""
        graph = DirectedGraph()
        assert graph.add_edge("A", "B") is True
        assert graph.add_edge("B", "A") is True
        assert graph.order() == 2
        assert graph.size() == 2
        assert graph.has_edge("A", "B") is True
        assert graph.has_edge("B", "A") is True
        assert graph.successors("A") == {"B"}
        assert graph.successors("B") == {"A"}

    def test_key_error_on_unknown_vertex_queries(self) -> None:
        """Querying neighbors or degrees of a non-existent vertex raises KeyError."""
        graph = DirectedGraph()
        with pytest.raises(KeyError):
            graph.successors("unknown")
        with pytest.raises(KeyError):
            graph.predecessors("unknown")
        with pytest.raises(KeyError):
            graph.in_degree("unknown")
        with pytest.raises(KeyError):
            graph.out_degree("unknown")
