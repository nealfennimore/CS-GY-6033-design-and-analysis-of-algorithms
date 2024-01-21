from typing import Optional

from src.tree.step import Node, Tree


class GraphStepTree(Tree):
    def render(self, node: Optional[Node], **kwargs):
        formatter = (
            lambda node,
            prefix: f'{prefix}(("{node.label}")):::{node.step.output_case.name.lower()}'
        )
        # classDefs: str = f"classDef subcall fill:{str(NodeColor.VISITED
        # .value)}"
        classDefs: str = "classDef subcall fill:#87ceeb"
        return super().render(node, formatter=formatter, classDefs=classDefs, **kwargs)
