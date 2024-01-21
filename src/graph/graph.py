from collections import defaultdict
from random import getrandbits
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
)

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from src.display import Display
from src.graph.color import Color, EdgeColor, NodeColor

T = TypeVar("T")
U = TypeVar("U")


NodePlaceholder: TypeAlias = str | int
NodeArguments: TypeAlias = Dict[str, Any]
EdgeArguments: TypeAlias = Dict[str, Any]
EdgeCoordinate: TypeAlias = Tuple[NodePlaceholder, NodePlaceholder]
SingleEdgeTemplate: TypeAlias = NodePlaceholder
EdgeTemplate: TypeAlias = Tuple[NodePlaceholder, EdgeArguments, NodeArguments]
EdgeTemplates: TypeAlias = EdgeTemplate | SingleEdgeTemplate


class NodeTemplate(Tuple[NodePlaceholder, NodeArguments]):
    def __new__(cls, t: Tuple[NodePlaceholder, NodeArguments]):
        assert len(t) == 2
        instance = tuple.__new__(NodeTemplate, t)
        return instance

    def __hash__(self):
        return hash(f"{self[0]}")


BaseTemplate: TypeAlias = Dict[NodePlaceholder | NodeTemplate, List[EdgeTemplates]]


class VertexBase:
    key: NodePlaceholder
    color: str
    _id: Optional[str] = None
    _default_blacklist: List[str] = ["key", "_id", "_blacklist", "_default_blacklist"]
    _blacklist: List[str] = []

    def __init__(self, **kwargs) -> None:
        self.color = NodeColor.DEFAULT.value
        self.__dict__.update(kwargs)

    @property
    def id(self) -> str:
        if not self._id:
            self._id = hex(getrandbits(24))[2:]
        return self._id

    @property
    def values(self):
        d = self.__dict__
        return {
            k: v
            for k, v in d.items()
            if k not in self._blacklist and k not in self._default_blacklist
        }

    @property
    def to_template(self) -> NodeTemplate:
        return NodeTemplate((self.key, self.values))


KC = TypeVar("KC", bound=VertexBase)


class EdgeBase(Generic[KC]):
    color: str
    _default_blacklist: List[str] = ["u", "v", "_blacklist", "_default_blacklist"]
    _blacklist: List[str] = []

    def __init__(self, u: KC, v: KC, **kwargs):
        self.color = EdgeColor.LINE_DEFAULT.value
        self.__dict__.update(kwargs)
        self.u = u
        self.v = v

    def __hash__(self):
        return hash("-".join(sorted([str(self.u.key), str(self.v.key)])))

    @property
    def values(self):
        d = self.__dict__
        return {
            k: v
            for k, v in d.items()
            if k not in self._blacklist and k not in self._default_blacklist
        }

    @property
    def to_template(self) -> Tuple[EdgeTemplate, EdgeTemplate]:
        u_key, u_values = self.u.to_template
        v_key, v_values = self.v.to_template
        return (
            (u_key, self.values, u_values),
            (v_key, self.values, v_values),
        )


ED = TypeVar("ED", bound=EdgeBase)


def build_attrs(x: Dict, *args: str) -> Dict[str, Any]:
    return {arg: x[arg] for arg in args if arg in x and x[arg] is not None}


NodeMapping: TypeAlias = Dict[NodePlaceholder, KC]
NodeToNeighborsMapping: TypeAlias = Dict[KC, List[KC]]
EdgeFromNodesMapping: TypeAlias = Dict[KC, Dict[KC, ED]]
EdgeFromCoordinatesMapping: TypeAlias = Dict[EdgeCoordinate, ED]
EdgeFromNodeCoordinatesMapping: TypeAlias = Dict[Tuple[KC, KC], ED]


def from_edge_template(template: EdgeTemplates) -> EdgeTemplate:
    if isinstance(template, tuple) and len(template) == 3:
        return template
    return (template, {}, {})


class Graph(Generic[KC, ED]):
    template: BaseTemplate
    vertex_cls: Type[KC]
    edge_cls: Type[ED]
    snapshots: List["Graph[KC,ED]"]

    _node_mapping: NodeMapping[KC]
    _node_to_neighbors: NodeToNeighborsMapping[KC]
    _edge_from_nodes: EdgeFromNodesMapping[KC, ED]
    _edge_from_coords: EdgeFromCoordinatesMapping[ED]
    _edge_from_node_coords: EdgeFromNodeCoordinatesMapping[KC, ED]

    def __init__(
        self,
        template: BaseTemplate,
        node_mapping: NodeMapping = {},
        node_to_neighbors: NodeToNeighborsMapping = {},
        edge_from_nodes: EdgeFromNodesMapping = {},
        edge_from_coords: EdgeFromCoordinatesMapping = {},
        edge_from_node_coords: EdgeFromNodeCoordinatesMapping = {},
    ):
        self.template = template
        self._node_mapping = node_mapping
        self._node_to_neighbors = node_to_neighbors
        self._edge_from_nodes = edge_from_nodes
        self._edge_from_coords = edge_from_coords
        self._edge_from_node_coords = edge_from_node_coords
        self.snapshots = []

    @classmethod
    def from_template(cls, template: BaseTemplate):
        node_arguments: Dict[NodePlaceholder, NodeArguments] = {}
        edge_arguments: Dict[EdgeCoordinate, EdgeArguments] = defaultdict(dict)

        for node, edge_templates in template.items():
            if isinstance(node, tuple):
                node, node_args = node
                node_arguments[node] = node_args
            else:
                node_arguments[node] = {}

            for edge_template in edge_templates:
                neighbor, edge_args, node_args = from_edge_template(edge_template)
                node_arguments[neighbor] = node_args
                edge_arguments[(node, neighbor)] = edge_args

        def to_vertex(n: NodePlaceholder):
            return cls.vertex_cls(**{"key": n, **node_arguments[n]})

        node_mapping: NodeMapping[KC] = {
            v.key: v
            for v in map(
                to_vertex,
                set(node_arguments.keys()),
            )
        }

        node_to_neighbors: NodeToNeighborsMapping[KC] = defaultdict(list)
        for node, edge_templates in template.items():
            if isinstance(node, tuple):
                node, _ = node
            for edge_template in edge_templates:
                neighbor, _, __ = from_edge_template(edge_template)
                node_to_neighbors[node_mapping[node]].append(node_mapping[neighbor])

        edge_from_nodes: EdgeFromNodesMapping[KC, ED] = defaultdict(dict)
        edge_from_node_coords: EdgeFromNodeCoordinatesMapping[KC, ED] = {}
        edge_from_coords: EdgeFromCoordinatesMapping[ED] = defaultdict(dict)

        for coords, edge_args in edge_arguments.items():
            node_u_key, node_v_key = coords
            node_u, node_v = node_mapping[node_u_key], node_mapping[node_v_key]

            if node_v in edge_from_nodes and node_u in edge_from_nodes[node_v]:
                edge = edge_from_nodes[node_v][node_u]
            else:
                edge = cls.edge_cls(node_u, node_v, **edge_args)

            edge_from_nodes[node_u][node_v] = edge
            edge_from_coords[coords] = edge
            edge_from_node_coords[(node_u, node_v)] = edge

        return cls(
            template,
            node_mapping,
            node_to_neighbors,
            edge_from_nodes,
            edge_from_coords,
            edge_from_node_coords,
        )

    def to_template(self):
        t: BaseTemplate = defaultdict(list)

        for node in self.nodes:
            node_temp = NodeTemplate((node.key, node.values))
            t[node_temp] = []
            for neighbor in self.neighbors_of(node):
                edge = self.edges_by_node_coords(node, neighbor)
                edge_values = {}
                if edge:
                    edge_values = edge.values
                t[node_temp].append(
                    (
                        neighbor.key,
                        edge_values,
                        neighbor.values,
                    )
                )

        return t

    def clone(self):
        return self.from_template(self.to_template())

    def node_by_key(self, key: NodePlaceholder) -> KC:
        assert key in self._node_mapping, f"Node '{key}' not found"
        return self._node_mapping[key]

    def edges_with_attrs(
        self,
        *args: str,
    ) -> List[Tuple[NodePlaceholder, NodePlaceholder, Optional[Dict]]]:
        return [
            (*coords, {k: v for k, v in edge.values.items() if k in args})
            for coords, edge in self._edge_from_coords.items()
        ]

    def nodes_with_attrs(self, *args: str) -> List[Tuple[Any, Optional[Any]]]:
        return [(node.key, build_attrs(node.__dict__, *args)) for node in self.vertices]

    @property
    def vertices(self) -> List[KC]:
        return list(self._node_mapping.values())

    @property
    def nodes(self) -> List[KC]:
        return self.vertices

    def neighbors_of(self, node: KC) -> List[KC]:
        return self._node_to_neighbors[node]

    @property
    def edges_by_nodes(self) -> EdgeFromNodesMapping[KC, ED]:
        return self._edge_from_nodes

    def edges_by_node_coords(self, u: KC, v: KC) -> ED:
        return self._edge_from_node_coords[(u, v)]

    @property
    def edges(self) -> List[ED]:
        return list(set(self._edge_from_coords.values()))

    def transpose(self):
        t: BaseTemplate = defaultdict(list)

        current = self.to_template()

        node_arguments: Dict[NodePlaceholder, NodeArguments] = {}
        edge_arguments: Dict[EdgeCoordinate, EdgeArguments] = {}

        for node, edge_templates in current.items():
            node_args = {}
            if isinstance(node, tuple):
                node, node_args = node

            node_arguments[node] = node_args
            for edge_template in edge_templates:
                neighbor, edge_args, node_args = from_edge_template(edge_template)
                node_arguments[neighbor] = node_args
                edge_arguments[(neighbor, node)] = edge_args

        potential_lone_nodes = set()

        for node, edge_template in current.items():
            if isinstance(node, tuple):
                node, node_args = node
            else:
                node_args = node_arguments[node]

            if len(edge_template) == 0:
                potential_lone_nodes.add(NodeTemplate((node, node_args)))

            for edge in edge_template:
                neighbor, _, __ = from_edge_template(edge)
                neighbor_node_args = node_arguments[neighbor]
                t[NodeTemplate((neighbor, neighbor_node_args))].append(
                    (node, edge_arguments[(neighbor, node)], node_args)
                )

        for node, node_args in potential_lone_nodes:
            template = NodeTemplate((node, node_args))
            if template not in t:
                t[template] = []

        return self.from_template(t)

    @property
    def render(self):
        return Renderer(self)

    def remove_node(self, v: KC):
        t = self.to_template()
        u: BaseTemplate = defaultdict(list)

        for node, edge_templates in t.items():
            node_args = {}
            if isinstance(node, tuple):
                node, node_args = node

            if node == v.key:
                continue

            for edge in edge_templates:
                neighbor, edge_args, neighbor_node_args = from_edge_template(edge)

                if neighbor == v.key:
                    continue

                u[NodeTemplate((node, node_args))].append(
                    (node, edge_args, neighbor_node_args)
                )

        return self.from_template(u)

    def take_snapshot(self):
        snapshot = self.clone()
        self.snapshots.append(snapshot)
        return snapshot

    @property
    def to_matrix(self):
        return AdjacencyMatrix(self)

    def is_cyclic(self, directed=True) -> bool:
        visited = set()  # Set to keep track of visited vertices
        rec_stack = set()  # Set to keep track of the recursion stack

        cycle_check = lambda x, y: x != y
        if directed:
            cycle_check = lambda x, _: x in rec_stack

        # Helper function for DFS
        def is_cyclic_util(v: KC, parent: Optional[KC]):
            visited.add(v)
            if directed:
                rec_stack.add(v)

            # Check all the neighbors of vertex v
            for neighbor in self.neighbors_of(v):
                if neighbor not in visited:
                    if is_cyclic_util(neighbor, v):
                        return True
                elif cycle_check(neighbor, parent):
                    # Directed: Found a back edge, graph is cyclic
                    # Undirected: If the neighbor is visited and is not the parent of the current vertex, a cycle is found
                    return True
            if directed:
                rec_stack.remove(v)
            return False

        # Check each vertex in the graph
        for vertex in self.vertices:
            if vertex not in visited:
                if is_cyclic_util(vertex, None):
                    return True

        return False

    def is_acyclic(self, directed=True) -> bool:
        return not self.is_cyclic(directed)

    @property
    def is_valid_undirected(self):
        for node in self.nodes:
            for neighbor in self.neighbors_of(node):
                if not (
                    neighbor in self.edges_by_nodes
                    and node in self.edges_by_nodes[neighbor]
                ):
                    print(f"Add node '{node.key}' to '{neighbor.key}'")
                    return False
        return True


G = TypeVar("G", bound=Graph)


class GraphBase(Graph[VertexBase, EdgeBase]):
    vertex_cls: Type[VertexBase] = VertexBase
    edge_cls: Type[EdgeBase] = EdgeBase


class AdjacencyMatrix(Generic[KC, ED]):
    adj: Graph[KC, ED]
    matrix: Dict[NodePlaceholder, List[NodePlaceholder]]
    rows: List[NodePlaceholder]
    columns: List[NodePlaceholder]

    def __init__(self, adj: Graph[KC, ED]):
        self.adj = adj

        keys = self.adj.template.keys()
        keys = [key[0] if isinstance(key, tuple) else key for key in keys]

        self.rows = self.columns = list(sorted(keys))

        matrix = defaultdict(list)

        for row in self.rows:
            for column in self.columns:
                t_row = self.adj.template[row]
                if len(t_row) == 0:
                    matrix[row].append(0)
                    continue

                if isinstance(t_row[0], tuple):
                    t_row = [t[0] for t in t_row]

                if isinstance(column, tuple):
                    column = column[0]

                if column in t_row:
                    matrix[row].append(1)
                else:
                    matrix[row].append(0)

        self.matrix = matrix

    def __str__(self) -> str:
        return self.to_grid()

    @property
    def to_df(self):
        return pd.DataFrame.from_dict(
            self.matrix,
        ).rename(index={idx: f"{row}" for idx, row in enumerate(self.rows)})

    def to_markdown(self, **kwargs):
        return self.to_df.to_markdown(**({"tablefmt": "github", **kwargs}))

    def to_grid(self):
        return (
            "$$"
            + (
                self.to_df.to_markdown(tablefmt="latex")
                .replace("tabular", "array")
                .replace("\n", " ")
            )
            + "$$"
        )

    def render_markdown(self, **kwargs):
        return Display.md(self.to_markdown(**kwargs))

    def render_katex(self):
        return Display.md(self.to_grid())


class Renderer:
    def __init__(self, adj: Graph) -> None:
        self.adj = adj

    def graph(self, **kwargs):
        g = nx.Graph()
        self.draw(g, **kwargs)

    def digraph(self, **kwargs):
        g = nx.DiGraph()
        self.draw(g, arrows=True, **kwargs)

    def multigraph(self, **kwargs):
        g = nx.MultiGraph()
        self.draw(g, **kwargs)

    def multidigraph(self, **kwargs):
        g = nx.MultiDiGraph()
        self.draw(g, arrows=True, **kwargs)

    def draw(
        self,
        g: nx.DiGraph | nx.Graph | nx.MultiGraph | nx.MultiDiGraph,
        edge_font_color: str = "k",
        edge_labels: List[str] = [],
        edge_label_prefixes: List[str] = [],
        node_labels: List[str] = [],
        node_label_prefixes: List[str] = [],
        node_font_color: str = "k",
        node_label_font_color: str = "k",
        node_label_offset: float = 0.0,
        use_node_color: bool = True,
        use_edge_color: bool = False,
        node_attributes: List[str] = [],
        edge_attributes: List[str] = [],
        line_width: float = 0.1,
        seed: int = 1111,
        arrows: bool = False,
    ):
        node_attrs = set(*node_attributes)
        for node_label in node_labels:
            node_attrs.add(node_label)

        if use_node_color:
            node_attrs.add("color")

        edge_attrs = set(*edge_attributes)
        for edge_label in edge_labels:
            edge_attrs.add(edge_label)

        if use_edge_color:
            edge_attrs.add("color")

        g.add_nodes_from(self.adj.nodes_with_attrs(*node_attrs))
        g.add_edges_from(self.adj.edges_with_attrs(*edge_attrs))

        pos = nx.spring_layout(g, seed=seed)

        if len(node_labels) > 0:
            assert len(node_label_prefixes) == 0 or len(node_labels) == len(
                node_label_prefixes
            )

            offset = min(len(node_labels), 1) * 0.05 + node_label_offset
            state_pos = {n: (x + offset, y + offset) for n, (x, y) in pos.items()}

            _node_labels: Dict[str, str] = {}
            for idx, node_label in enumerate(node_labels):
                attrs = nx.get_node_attributes(g, node_label)
                for node, label in attrs.items():
                    _prefix = (
                        f"{node_label_prefixes[idx]}:"
                        if idx < len(node_label_prefixes)
                        else ""
                    )
                    _label = f"{_prefix}{label}"
                    if node in _node_labels:
                        _node_labels[node] += f"\n{_label}"
                    else:
                        _node_labels[node] = f"{_label}"

            nx.draw_networkx_labels(
                g,
                state_pos,
                labels=_node_labels,
                font_color=node_label_font_color,
                font_size=8,
                bbox=dict(
                    boxstyle="circle",
                    alpha=1,
                    facecolor="sandybrown",
                    # edgecolor="black",
                    # pad=0.5,
                    linewidth=0,
                ),
            )

        if len(edge_labels) > 0:
            assert len(edge_label_prefixes) == 0 or len(edge_labels) == len(
                edge_label_prefixes
            )

            _edge_labels: Dict[str, str] = {}
            for idx, edge_label in enumerate(edge_labels):
                attrs = nx.get_edge_attributes(g, edge_label)
                for edge, label in attrs.items():
                    _prefix = (
                        f"{edge_label_prefixes[idx]}:"
                        if idx < len(edge_label_prefixes)
                        else ""
                    )
                    _label = f"{_prefix}{label}"
                    if edge in _edge_labels:
                        _edge_labels[edge] += f"\n{_label}"
                    else:
                        _edge_labels[edge] = f"{_label}"

            nx.draw_networkx_edge_labels(
                g,
                pos,
                edge_labels=_edge_labels,
                font_color=edge_font_color,
                verticalalignment="top",
                # bbox=dict(alpha=1, facecolor="purple", edgecolor="none"),
            )

        node_color = None
        if use_node_color:
            node_color = nx.get_node_attributes(g, "color").values()

        edge_color = Color.BLACK.value
        if use_edge_color:
            edge_color = nx.get_edge_attributes(g, "color").values()

        nx.draw_networkx(
            g,
            pos,
            node_color=node_color,
            edge_color=edge_color,
            font_color=node_font_color,
            arrows=arrows,
            width=line_width,
        )
        plt.axis("off")
        plt.show()
