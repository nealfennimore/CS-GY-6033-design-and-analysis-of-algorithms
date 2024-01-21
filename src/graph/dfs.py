from contextvars import ContextVar, Token
from typing import List, Optional, Type, TypeVar

from src.graph.color import Color, NodeColor
from src.graph.graph import ED, EdgeBase, Graph, NodePlaceholder, Renderer, VertexBase
from src.graph.step import GraphStepTree
from src.mermaid import Output
from src.tree.step import Hash, Stepper, ctx

time_ctx = ContextVar("timer")


class DFSVertexBase(VertexBase):
    color: str
    start_time: Optional[int]
    end_time: Optional[int]
    distance: Optional[int]
    _blacklist = ["parent", "visited"]

    def __init__(
        self,
        key: NodePlaceholder,
        distance: Optional[int] = 0,
        color=NodeColor.DEFAULT.value,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.key = key
        self.visited = False
        self.parent = None
        self.distance = distance
        self.color = color
        self.start_time = start_time
        self.end_time = end_time


class Vertex(DFSVertexBase):
    parent: Optional["Vertex"]
    visited: bool
    _blacklist = ["parent", "visited"]

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.visited = False
        self.parent = None


DFS_KC = TypeVar("DFS_KC", bound=DFSVertexBase)


class DFSGraphBase(Graph[DFS_KC, ED]):
    vertex_cls: Type[DFS_KC]
    edge_cls: Type[ED]

    @property
    def topological_sort(self) -> List[DFS_KC]:
        for node in self.nodes:
            assert (
                node.start_time is not None and node.end_time is not None
            ), f"{node.key} has no start/end time"
        return list(sorted(self.nodes, key=lambda x: x.end_time, reverse=True))

    def strongly_connected_components(self):
        G = self.clone()
        dfs_visit_whole_graph_no_start(G)

        H = self.transpose()

        trees = []
        colors = [c.value for c in Color]

        for sorted_node in G.topological_sort:
            node = H.node_by_key(sorted_node.key)
            assert node is not None
            if node.visited:
                continue

            node.color = colors.pop()
            node.visited = True
            trees.append(dfs_visit(node, H, skip_time=True, color=node.color))

        for colored_node in H.vertices:
            node = G.node_by_key(colored_node.key)
            assert node is not None
            node.color = colored_node.color

        return G, H, trees

    @property
    def topological_sortings(self):
        if len(self.vertices) == 0:
            yield []
            return

        for v in self.vertices:
            g = self.remove_node(v)
            for ts in g.topological_sortings:
                yield [v.key] + ts

        return

    @property
    def count_topological_sortings(self):
        return len([sorting for sorting in self.topological_sortings])

    @property
    def render(self):
        return DFSRenderer(self)


class DFSGraph(DFSGraphBase):
    vertex_cls: Type[DFSVertexBase] = DFSVertexBase
    edge_cls: Type[EdgeBase] = EdgeBase


class DFSRenderer(Renderer):
    def __init__(self, adj: DFSGraphBase) -> None:
        self.adj = adj

    @property
    def topological_sort(self) -> Output:
        nodes = self.adj.topological_sort

        m = """graph LR
        classDef default fill:#87ceeb\n
"""

        node_defs = set()
        paths = set()

        for idx in range(len(nodes) - 1, -1, -1):
            node = nodes[idx]
            node_defs.add(f"{node.id}(({node.key}: {idx}))")

        for idx in range(len(nodes) - 1, -1, -1):
            node = nodes[idx]
            neighbors = self.adj.neighbors_of(node)

            for neighbor in neighbors:
                paths.add(f"{node.id} --> {neighbor.id}")

        items = [*paths]
        items.reverse()

        m += "\n".join(list(node_defs) + items)

        return Output(m)


class Timer:
    time: int
    token: Token | None

    def __init__(self, time=0) -> None:
        self.token = time_ctx.set(self)
        self.time = time

    def increment(self):
        assert self.token is not None
        self.time += 1
        return self.time

    def done(self):
        assert self.token is not None
        time_ctx.reset(self.token)
        self.token = None


def _dfs_visit(
    u: Vertex,
    Adj: DFSGraphBase,
    parent_id: Optional[Hash] = None,
    color: str = NodeColor.VISITED.value,
    skip_time: bool = False,
):
    ctx.get().called_with(u.id, parent_id, _dfs_visit, [u.key])

    u.visited = True

    if not skip_time:
        u.start_time = time_ctx.get().increment()

    for v in Adj.neighbors_of(u):
        if not v.visited:
            v.color = color
            assert u.distance is not None
            v.distance = u.distance + 1
            v.parent = u
            Adj.take_snapshot()
            _dfs_visit(v, Adj, u.id, color, skip_time)

    if not skip_time:
        u.end_time = time_ctx.get().increment()


def dfs_visit(u: DFSVertexBase, Adj: DFSGraphBase, *args, **kwargs):
    _, token = Stepper.run(_dfs_visit, u, Adj, *args, **kwargs)
    tree = GraphStepTree.build(
        ctx.get().called_with_subcalls, include_output=False, include_fn=False
    )
    ctx.reset(token)
    return tree


def dfs_visit_whole_graph(u: Vertex, Adj: DFSGraphBase, *args, **kwargs):
    u.distance = 0
    u.color = NodeColor.START_FROM.value

    trees = []

    _timer = Timer(0)

    trees.append(dfs_visit(u, Adj, *args, **kwargs))

    for v in Adj.vertices:
        if v.visited:
            continue

        v.distance = 0
        v.color = NodeColor.START_FROM.value

        trees.append(dfs_visit(v, Adj, *args, **kwargs))

    _timer.done()

    return trees


def dfs_visit_whole_graph_no_start(Adj: DFSGraphBase, *args, **kwargs):
    trees = []

    _timer = Timer(0)

    for v in Adj.vertices:
        if v.visited:
            continue

        v.distance = 0
        v.color = NodeColor.START_FROM.value

        trees.append(dfs_visit(v, Adj, *args, **kwargs))

    _timer.done()

    return trees


def initialize(s: Vertex, Adj: DFSGraphBase) -> None:
    for vertex in Adj.vertices:
        vertex.visited = False
        vertex.parent = None

    s.distance = 0
    s.color = NodeColor.START_FROM.value


def _depth_first_search(start: Vertex, Adj: DFSGraphBase) -> None:
    initialize(start, Adj)
    _dfs_visit(start, Adj)


def depth_first_search(
    start: Vertex,
    Adj: Graph,
    timer: Optional[Timer] = None,
) -> GraphStepTree:
    _timer = timer or Timer(0)
    _, token = Stepper.run(_depth_first_search, start, Adj)
    tree = GraphStepTree.build(
        ctx.get().called_with_subcalls, include_output=False, include_fn=False
    )
    ctx.reset(token)
    if timer is None:
        assert _timer is not None
        _timer.done()
    return tree
