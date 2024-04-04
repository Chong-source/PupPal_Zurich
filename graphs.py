"""Abstract graph implementation code used in our Project 2 code.

Does not contain specific information pertaining to the ideas of our project, just
a general implementation of graphs similar to execersizes 3 and 4.
"""
from __future__ import annotations
from typing import Any


class _Vertex:
    """A vertex in a graph, used to represent any arbitrary element.

    Instance Attributes:
        - element: The data stored in this vertex

    Representation Invariants:
        - self not in self.neighbours
        - all(self in target.neighbours for target in self.neighbours)
    """
    element: Any
    neighbours: set[_Vertex]

    def __init__(self, element: Any) -> None:
        """Initialize a new vertex with the given element.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'user', 'book'}
        """
        self.element = element
        self.neighbours = set()

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)


class Graph:
    """A graph with connected vertices.
    """
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2

        >>> g = Graph()
        >>> g.add_vertex(1)
        >>> g.add_vertex(2)
        >>> g.add_edge(1, 2)
        >>> g._vertices[2] in g._vertices[1].neighbours and g._vertices[1] in g._vertices[2].neighbours
        True
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        >>> g = Graph()
        >>> g.add_vertex(1)
        >>> g.add_vertex(2)
        >>> g.add_edge(1, 2)
        >>> g.adjacent(1, 2)
        True
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.element == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        >>> g = Graph()
        >>> g.add_vertex(1)
        >>> g.add_vertex(2)
        >>> g.add_edge(1, 2)
        >>> neighbours = g.get_neighbours(1)
        >>> neighbours == {2}
        True
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.element for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_nodes(self) -> set:
        """Return a set of all the node values in this graph.
        """
        return set(self._vertices.keys())

    def contains(self, element: Any) -> bool:
        """Checks if this graph contains a vertex with the given key.
        """
        return element in self._vertices


class _WeightedVertex(_Vertex):
    """A vertex in a weighted graph.

    The only difference from normal vertices, is that it stores the weighted edge between each
    of its neighbours.

    Instance Attributes:
        - item: The data stored in this vertex
        - neighbours: The vertices that are adjacent to this vertex, and their corresponding
            edge weights.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    element: Any
    kind: str
    neighbours: dict[_WeightedVertex, int | float]

    def __init__(self, item: Any) -> None:
        """Initialize a new vertex with the given item.

        This vertex is initialized with no neighbours.
        """
        super().__init__(item)
        self.neighbours = {}


class WeightedGraph(Graph):
    """A weighted graph (has weights between the edges of different nodes).
    """
    _vertices: dict[Any, _WeightedVertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}
        Graph.__init__(self)

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item)

    def add_edge(self, item1: Any, item2: Any, weight: int | float = 1) -> None:
        """Add an edge between the two vertices with the given items in this graph,
        with the given weight.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight
        else:
            raise ValueError

    def get_weight(self, item1: Any, item2: Any) -> int | float:
        """Return the weight of the edge between the given items.

        Return 0 if item1 and item2 are not adjacent.

        Preconditions:
            - item1 and item2 are vertices in this graph

        >>> wg = WeightedGraph()
        >>> wg.add_vertex(1)
        >>> wg.add_vertex(2)
        >>> wg.add_edge(1, 2, 3)
        >>> wg.get_weight(1, 2)
        3
        """
        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        return v1.neighbours.get(v2, 0)

    def average_weight(self, item: Any) -> float:
        """Return the average weight of the edges adjacent to the vertex corresponding to item.

        Raise ValueError if item does not corresponding to a vertex in the graph.
        >>> wg = WeightedGraph()
        >>> wg.add_vertex(1)
        >>> wg.add_vertex(2)
        >>> wg.add_vertex(4)
        >>> wg.add_edge(1, 2, 3)
        >>> wg.add_edge(1, 4, 3)
        >>> wg.average_weight(1)
        3.0
        """
        if item in self._vertices:
            v = self._vertices[item]
            return sum(v.neighbours.values()) / len(v.neighbours)
        else:
            raise ValueError


if __name__ == '__main__':

    import doctest

    doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E1136', 'W0221'],
        'max-nested-blocks': 4
    })
