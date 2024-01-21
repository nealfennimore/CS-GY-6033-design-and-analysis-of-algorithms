from typing import Any, Callable, List, Optional

from binarytree import Node

from src.output import Output
from src.tree.base import BaseNode


def rb_formatter(node: BaseNode, prefix: str):
    if node.value == 0:
        return f"{prefix}[nil]:::nil"
    return f"{prefix}[{node.value}]:::{node.color.name.lower()}"


class Mermaid:
    @staticmethod
    def in_order_traversal(
        node: Optional[BaseNode | Node],
        formatter: Callable[[Any, str], str],
        paths: List[str],
        path: str = "",
        prefix="_ROOT",
        level=0,
    ):
        if node is not None:
            path = (
                f"{path} --> {formatter(node, prefix)}"
                if path != ""
                else formatter(node, prefix)
            )
            Mermaid.in_order_traversal(
                node.left, formatter, paths, path, f"{prefix}-L{level + 1}", level + 1
            )
            paths.append(path)
            Mermaid.in_order_traversal(
                node.right, formatter, paths, path, f"{prefix}-R{level + 1}", level + 1
            )

    @staticmethod
    def reduce_paths(paths: List[str]):
        container = [path.split(" --> ") for path in sorted(paths)]

        for idx in range(len(container) - 1):
            curr = container[idx]

            for j_idx in range(idx + 1, len(container)):
                nxt = container[j_idx]

                s = 0
                while s < len(curr) and s < len(nxt) and curr[s] == nxt[s]:
                    s += 1

                if s > 0:
                    container[j_idx] = nxt[s - 1 :]

        return [" --> ".join(path) for path in container]

    @staticmethod
    def render_binary_search_tree(
        node: Node,
        formatter=lambda node, prefix: f"{prefix}[{node.value}]",
        classDefs: str = "",
    ):
        assert node is not None

        paths = []
        Mermaid.in_order_traversal(node, formatter, paths)
        paths = Mermaid.reduce_paths(paths)
        paths = "\n".join(paths)

        return Output(
            f"""
flowchart TD
{classDefs}
{paths}
"""
        )

    @staticmethod
    def render_step_tree(
        node: BaseNode,
        formatter=lambda node,
        prefix: f'{prefix}["{node.label}"]:::{node.step.output_case.name.lower()}',
        classDefs: str = "classDef cached fill:#4a8bad,color:#fff",
    ):
        assert node is not None

        paths = []
        Mermaid.in_order_traversal(node, formatter, paths)
        paths = Mermaid.reduce_paths(paths)
        paths = "\n".join(paths)

        return Output(
            f"""
flowchart TD
{classDefs}
{paths}
"""
        )

    @staticmethod
    def render_red_black_tree(node: BaseNode, formatter=rb_formatter):
        assert node is not None

        paths = []
        Mermaid.in_order_traversal(node, formatter, paths)
        paths = Mermaid.reduce_paths(paths)
        paths = "\n".join(paths)

        return Output(
            f"""
flowchart TD
classDef black fill:#000,color:#fff
classDef red fill:#ff0000,color:#000
classDef nil fill:#000,stroke:#000,color:#00000000
{paths}
"""
        )

    @staticmethod
    def render_interval_tree(
        node: BaseNode,
        formatter=lambda node, prefix: f'{prefix}["({node})<br>{node.max_end}"]',
    ):
        assert node is not None

        paths = []
        Mermaid.in_order_traversal(node, formatter, paths)
        paths = Mermaid.reduce_paths(paths)
        paths = "\n".join(paths)

        return Output(
            f"""
flowchart TD
{paths}
"""
        )

    @staticmethod
    def render_avl_tree(
        node: BaseNode,
        formatter=lambda node, prefix: f"{prefix}[{node.value}<br>h: {node.height}]",
        classDefs: str = "",
    ):
        assert node is not None

        paths = []
        Mermaid.in_order_traversal(node, formatter, paths)
        paths = Mermaid.reduce_paths(paths)
        paths = "\n".join(paths)

        return Output(
            f"""
flowchart TD
{classDefs}
{paths}
"""
        )
