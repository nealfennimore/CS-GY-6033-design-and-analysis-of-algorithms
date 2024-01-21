from typing import Any, Optional

from src.graph.color import EdgeColor, NodeColor
from src.graph.dfs import (
    DFSVertexBase,
)
from src.graph.mst.prim import (
    EdgeBase,
    MSTGraphBase,
)
from src.graph.step import GraphStepTree
from src.tree.step import Stepper, ctx


class Vertex(DFSVertexBase):
    _blacklist = ["component", "next"]
    key: Any
    component: Optional["Vertex"]
    next: Optional["Vertex"]
    distance: float
    color: str

    def __init__(
        self,
        key: Any,
        distance: float = float("inf"),
        color=NodeColor.VISITED.value,
        *args,
        **kwargs,
    ):
        super().__init__(key, *args, **kwargs)
        self.key = key
        self.component = None
        self.next = None
        self.distance = distance
        self.color = color

    def __lt__(self, other):
        return self.distance < other.distance


class Edge(EdgeBase[Vertex]):
    def __init__(
        self,
        u: Vertex,
        v: Vertex,
        weight: int,
        color: str = EdgeColor.LINE_DEFAULT.value,
    ):
        self.u = u
        self.v = v
        self.weight = weight
        self.color = color


class KruskalsGraph(MSTGraphBase[Vertex, Edge]):
    vertex_cls = Vertex
    edge_cls = Edge


def _minimum_spanning_tree(Adj: KruskalsGraph):
    def merge(u: Vertex, v: Vertex):
        w = u.component

        assert w is not None
        while w.next:
            w = w.next

        w.next = v.component

        s = v.component
        while s:
            s.component = u.component
            s = s.next

    for v in Adj.vertices:
        v.component = v

    edges = sorted(Adj.edges, key=lambda e: e.weight)

    parent_id = edges[0].u.component.id

    for edge in edges:
        u, v = edge.u, edge.v
        if u.component != v.component:
            v_id = v.component.id
            merge(u, v)
            ctx.get().called_with(v_id, parent_id, merge, [u.key, v.key])
            edge.color = EdgeColor.LINE_VISITED.value
            parent_id = v_id
            Adj.take_snapshot()


def minimum_spanning_tree(Adj: KruskalsGraph):
    _, token = Stepper.run(_minimum_spanning_tree, Adj)
    tree = GraphStepTree.build(
        ctx.get().called_with_subcalls, include_output=False, include_fn=False
    )
    ctx.reset(token)
    return tree
