"""Oracle tests using NetworkX to cross-check custom DirectedGraph model.

NetworkX is used strictly as a verification oracle in test suites per Constitution Principle III.
Application code in src/ NEVER imports networkx.
"""

import csv
from pathlib import Path

import networkx as nx

from src.loader import load_graph_from_csv


class TestNetworkXOracle:
    """Compare custom DirectedGraph loaded vertices and edges against NetworkX DiGraph."""

    def test_oracle_small_dag(self, sample_data_dir: Path) -> None:
        """Cross-check small-dag.csv vertices and edges against NetworkX."""
        csv_path = sample_data_dir / "small-dag.csv"
        result = load_graph_from_csv(csv_path)
        our_graph = result.graph

        nx_graph = nx.DiGraph()
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if len(row) == 2:
                    s, t = row[0].strip(), row[1].strip()
                    if s and not t:
                        nx_graph.add_node(s)
                    elif s and t:
                        nx_graph.add_edge(s, t)

        assert our_graph.vertices() == set(nx_graph.nodes())
        assert our_graph.edges() == set(nx_graph.edges())
        assert our_graph.order() == nx_graph.number_of_nodes()
        assert our_graph.size() == nx_graph.number_of_edges()

    def test_oracle_cs_curriculum(self, sample_data_dir: Path) -> None:
        """Cross-check cs-curriculum.csv vertices and deduplicated edges against NetworkX."""
        csv_path = sample_data_dir / "cs-curriculum.csv"
        result = load_graph_from_csv(csv_path)
        our_graph = result.graph

        nx_graph = nx.DiGraph()
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) == 2:
                    s, t = row[0].strip(), row[1].strip()
                    if s and t:
                        nx_graph.add_edge(s, t)

        assert our_graph.vertices() == set(nx_graph.nodes())
        assert our_graph.edges() == set(nx_graph.edges())
        assert our_graph.order() == nx_graph.number_of_nodes()
        assert our_graph.size() == nx_graph.number_of_edges()

    def test_oracle_build_with_cycle(self, sample_data_dir: Path) -> None:
        """Cross-check build-with-cycle.csv (with cycle and self-loop) against NetworkX."""
        csv_path = sample_data_dir / "build-with-cycle.csv"
        result = load_graph_from_csv(csv_path)
        our_graph = result.graph

        nx_graph = nx.DiGraph()
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) == 2:
                    s, t = row[0].strip(), row[1].strip()
                    if s and t:
                        nx_graph.add_edge(s, t)

        assert our_graph.vertices() == set(nx_graph.nodes())
        assert our_graph.edges() == set(nx_graph.edges())
        assert our_graph.order() == nx_graph.number_of_nodes()
        assert our_graph.size() == nx_graph.number_of_edges()
