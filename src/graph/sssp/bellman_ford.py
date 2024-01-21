from src.graph.mst.prim import EdgeColor, MSTGraph, Vertex
from src.graph.step import GraphStepTree
from src.tree.step import Stepper, ctx


def _single_source_shortest_path(start: Vertex, Adj: MSTGraph):
    start.distance = 0

    V = Adj.vertices
    E = Adj._edge_from_node_coords
    e = Adj.edges_by_nodes

    ctx.get().called_with(start.id, None, _single_source_shortest_path, [start.key])

    for _ in range(len(V) - 1):
        for coords, edge in E.items():
            u, v = coords
            if v.distance > u.distance + edge.weight:
                v.distance = u.distance + edge.weight
                if v.parent:
                    e[v.parent][v].color = EdgeColor.LINE_DEFAULT.value
                v.parent = u
                e[v.parent][v].color = EdgeColor.LINE_VISITED.value
                ctx.get().called_with(v.id, u.id, _single_source_shortest_path, [v.key])
                Adj.take_snapshot()


def single_source_shortest_path(start: Vertex, Adj: MSTGraph):
    _, token = Stepper.run(_single_source_shortest_path, start, Adj)
    tree = GraphStepTree.build(
        ctx.get().called_with_subcalls, include_output=False, include_fn=False
    )
    ctx.reset(token)
    return tree
