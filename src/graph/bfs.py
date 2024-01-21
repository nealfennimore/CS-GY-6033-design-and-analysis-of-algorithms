from queue import Queue
from typing import Any, List, Optional, Type

from src.graph.color import NodeColor
from src.graph.graph import EdgeBase, Graph, VertexBase
from src.graph.step import GraphStepTree
from src.tree.step import Stepper, ctx


class Vertex(VertexBase):
    key: Any
    children: Optional[List["Vertex"]]
    parent: Optional["Vertex"]
    visited: bool
    distance: Optional[int]
    color: str

    def __init__(self, key: Any):
        self.key = key
        self.visited = False
        self.children = None
        self.parent = None
        self.distance = None
        self.color = NodeColor.DEFAULT.value


class BFSGraph(Graph[Vertex, EdgeBase]):
    vertex_cls: Type[Vertex] = Vertex
    edge_cls: Type[EdgeBase] = EdgeBase


def _breadth_first_search(start: Vertex, Adj: BFSGraph) -> None:
    Q = Queue()

    initialize(start, Adj, Q)

    ctx.get().called_with(start.id, None, _breadth_first_search, [start.key])

    while not Q.empty():
        u = Q.get()

        for v in Adj.neighbors_of(u):
            if not v.visited:
                v.visited = True
                v.color = NodeColor.VISITED.value
                v.distance = u.distance + 1
                v.parent = u
                u.children.append(v)
                ctx.get().called_with(v.id, u.id, _breadth_first_search, [v.key])
                Q.put(v)


def initialize(start: Vertex, Adj: BFSGraph, Q: Queue) -> None:
    for vertex in Adj.vertices:
        vertex.visited = False
        vertex.children = []
        vertex.parent = None

    start.visited = True
    start.color = NodeColor.START_FROM.value
    start.distance = 0

    Q.put(start)


def breadth_first_search(start: Vertex, Adj: BFSGraph) -> GraphStepTree:
    _, token = Stepper.run(_breadth_first_search, start, Adj)
    tree = GraphStepTree.build(
        ctx.get().called_with_subcalls, include_output=False, include_fn=False
    )
    ctx.reset(token)
    return tree
