import heapq
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from src.graph.color import EdgeColor, NodeColor
from src.graph.dfs import DFS_KC, DFSGraphBase, DFSRenderer, DFSVertexBase
from src.graph.graph import (
    ED,
    BaseTemplate,
    EdgeArguments,
    EdgeBase,
    NodeArguments,
    NodePlaceholder,
)
from src.graph.step import GraphStepTree
from src.tree.step import Stepper, ctx


class Vertex(DFSVertexBase):
    key: Any
    parent: Optional["Vertex"]
    visited: bool
    distance: float
    color: str
    _blacklist = ["parent", "visited"]

    def __init__(
        self,
        key: Any,
        distance: float = float("inf"),
        color=NodeColor.VISITED.value,
        visited: bool = False,
        parent: Optional["Vertex"] = None,
        *args,
        **kwargs,
    ):
        super().__init__(key, *args, **kwargs)
        self.visited = False
        self.parent = None
        self.distance = distance
        self.color = color
        self.visited = visited
        self.parent = parent

    def __lt__(self, other):
        return self.distance < other.distance

    def __gt__(self, other):
        return self.distance > other.distance

    def __equal__(self, other):
        return self.distance == other.distance


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


EdgeWeight = int
MSTNodeTemplate = Tuple[NodePlaceholder, EdgeWeight]
MSTTemplate = Dict[NodePlaceholder, List[MSTNodeTemplate]]


class MSTGraphBase(DFSGraphBase[DFS_KC, ED]):
    @classmethod
    def from_template(cls, template: MSTTemplate | BaseTemplate):
        t: BaseTemplate = defaultdict(list)

        for node, edge_templates in template.items():
            for edge_template in edge_templates:
                assert isinstance(edge_template, tuple)
                node_args: NodeArguments = {}
                edge_args: EdgeArguments = {}
                if len(edge_template) == 2:
                    neighbor, weight = edge_template
                    edge_args = {"weight": weight}
                else:
                    neighbor, edge_args, node_args = edge_template
                t[node].append((neighbor, edge_args, node_args))

        return super().from_template(t)

    @property
    def render(self):
        return MSTRenderer(self)


class MSTGraph(MSTGraphBase[Vertex, Edge]):
    vertex_cls = Vertex
    edge_cls = Edge


class MSTRenderer(DFSRenderer):
    def draw(self, g, **kwargs):
        return super().draw(
            g,
            **kwargs,
            use_edge_color=True,
        )


class MinHeapObj(Vertex):
    def __init__(self, val: Vertex):
        self.val = val

    def __lt__(self, other):
        return self.val < other.val

    def __eq__(self, other):
        return self.val == other.val

    def __str__(self):
        return str(self.val.key)


class MaxHeapObj(MinHeapObj):
    def __lt__(self, other):
        return self.val.__gt__(other.val)


class MinHeap(List[Vertex]):
    def __init__(self, h: List[Vertex] = []):
        self.h = [MinHeapObj(n) for n in h]
        heapq.heapify(self.h)

    def heappush(self, x: Vertex):
        heapq.heappush(self.h, MinHeapObj(x))

    def heappop(self) -> Vertex:
        return heapq.heappop(self.h).val

    def decrease_key(self, v: Vertex):
        heapq.heapify(self.h)

    def __contains__(self, __key: Vertex) -> bool:
        for v in self.h:
            if v.val == __key:
                return True
        return False

    def __getitem__(self, i):
        return self.h[i]

    def __len__(self):
        return len(self.h)


class MaxHeap(MinHeap):
    def __init__(self, h: List[Vertex] = []):
        self.h = [MaxHeapObj(x) for x in h]
        heapq.heapify(self.h)

    def heappush(self, x: Vertex):
        heapq.heappush(self.h, MaxHeapObj(x))

    def heappop(self) -> Vertex:
        return heapq.heappop(self.h).val

    def increase_key(self, v: Vertex):
        heapq.heapify(self.h)


def _minimum_spanning_tree(start: Vertex, G: MSTGraph):
    start.distance = 0

    Q = MinHeap(G.vertices)
    e = G.edges_by_nodes

    ctx.get().called_with(start.id, None, _minimum_spanning_tree, [start.key])

    while Q:
        u = Q.heappop()  # Extracts the vertex with min key value
        for v in G.neighbors_of(u):
            edge = e[u][v]
            if v in Q and v.distance > edge.weight:
                v.distance = edge.weight
                if v.parent:
                    e[v.parent][v].color = EdgeColor.LINE_DEFAULT.value
                v.parent = u
                e[v.parent][v].color = EdgeColor.LINE_VISITED.value
                ctx.get().called_with(v.id, u.id, _minimum_spanning_tree, [v.key])
                Q.decrease_key(v)
                G.take_snapshot()


def minimum_spanning_tree(start: Vertex, G: MSTGraph):
    _, token = Stepper.run(_minimum_spanning_tree, start, G)
    tree = GraphStepTree.build(
        ctx.get().called_with_subcalls, include_output=False, include_fn=False
    )
    ctx.reset(token)
    return tree
