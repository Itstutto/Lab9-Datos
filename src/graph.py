"""Pure in-memory DirectedGraph data structure.

Zero I/O, zero printing, zero external dependencies.
"""

from collections.abc import Set


class DirectedGraph:
    """An unweighted directed graph represented via adjacency lists.

    Invariants:
      - Every vertex exists in both _adj and _pred dictionaries.
      - _adj[u] stores the set of outgoing successors {v | (u, v) in E}.
      - _pred[v] stores the set of incoming predecessors {u | (u, v) in E}.
      - Edge existence and duplicate detection are O(1) average time.
      - Total space complexity is O(V + E).
    """

    def __init__(self) -> None:
        self._adj: dict[str, set[str]] = {}
        self._pred: dict[str, set[str]] = {}

    def add_vertex(self, vertex: str) -> bool:
        """Add a vertex to the graph if not already present.

        Returns True if the vertex was newly added, False if it already existed.
        """
        if vertex in self._adj:
            return False
        self._adj[vertex] = set()
        self._pred[vertex] = set()
        return True

    def add_edge(self, source: str, target: str) -> bool:
        """Add a directed edge from source to target.

        Implicitly registers source and target as vertices if not already present.
        Returns True if the edge was newly added, False if it was already present.
        """
        self.add_vertex(source)
        self.add_vertex(target)

        if target in self._adj[source]:
            return False

        self._adj[source].add(target)
        self._pred[target].add(source)
        return True

    def has_vertex(self, vertex: str) -> bool:
        """Return True if vertex exists in the graph, False otherwise."""
        return vertex in self._adj

    def has_edge(self, source: str, target: str) -> bool:
        """Return True if directed edge (source, target) exists in the graph."""
        return source in self._adj and target in self._adj[source]

    def vertices(self) -> set[str]:
        """Return a copy of the set of all vertex names in the graph."""
        return set(self._adj.keys())

    def edges(self) -> set[tuple[str, str]]:
        """Return a set of all directed edge pairs (source, target) in the graph."""
        result: set[tuple[str, str]] = set()
        for source, targets in self._adj.items():
            for target in targets:
                result.add((source, target))
        return result

    def successors(self, vertex: str) -> Set[str]:
        """Return the set of direct outgoing successor vertices for vertex.

        Raises KeyError if vertex is not in the graph.
        """
        if vertex not in self._adj:
            raise KeyError(f"Vertex '{vertex}' does not exist in graph")
        return set(self._adj[vertex])

    def predecessors(self, vertex: str) -> Set[str]:
        """Return the set of direct incoming predecessor vertices for vertex.

        Raises KeyError if vertex is not in the graph.
        """
        if vertex not in self._pred:
            raise KeyError(f"Vertex '{vertex}' does not exist in graph")
        return set(self._pred[vertex])

    def in_degree(self, vertex: str) -> int:
        """Return the in-degree of vertex (number of incoming directed edges).

        Raises KeyError if vertex is not in the graph.
        """
        if vertex not in self._pred:
            raise KeyError(f"Vertex '{vertex}' does not exist in graph")
        return len(self._pred[vertex])

    def out_degree(self, vertex: str) -> int:
        """Return the out-degree of vertex (number of outgoing directed edges).

        Raises KeyError if vertex is not in the graph.
        """
        if vertex not in self._adj:
            raise KeyError(f"Vertex '{vertex}' does not exist in graph")
        return len(self._adj[vertex])

    def order(self) -> int:
        """Return the total number of vertices |V| in the graph."""
        return len(self._adj)

    def size(self) -> int:
        """Return the total number of unique directed edges |E| in the graph."""
        return sum(len(targets) for targets in self._adj.values())
