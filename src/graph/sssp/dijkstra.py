from src.graph.mst.prim import EdgeColor, MinHeap, MSTGraph, Vertex
from src.graph.step import GraphStepTree
from src.tree.step import Stepper, ctx


def _single_source_shortest_path(start: Vertex, G: MSTGraph):
    start.distance = 0

    Q = MinHeap(G.vertices)
    e = G.edges_by_nodes

    ctx.get().called_with(start.id, None, _single_source_shortest_path, [start.key])

    while Q:
        u = Q.heappop()  # Extracts the vertex with min key value
        for v in G.neighbors_of(u):
            edge = e[u][v]
            if v.distance > u.distance + edge.weight:
                v.distance = u.distance + edge.weight
                if v.parent:
                    e[v.parent][v].color = EdgeColor.LINE_DEFAULT.value
                v.parent = u
                e[v.parent][v].color = EdgeColor.LINE_VISITED.value
                ctx.get().called_with(v.id, u.id, _single_source_shortest_path, [v.key])
                G.take_snapshot()


def single_source_shortest_path(start: Vertex, G: MSTGraph):
    _, token = Stepper.run(_single_source_shortest_path, start, G)
    tree = GraphStepTree.build(
        ctx.get().called_with_subcalls, include_output=False, include_fn=False
    )
    ctx.reset(token)
    return tree
