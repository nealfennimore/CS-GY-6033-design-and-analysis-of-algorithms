from copy import deepcopy as _deepcopy
from typing import List, Optional

from src.output import Output


class BaseNode:
    value: int
    left: Optional["BaseNode"]
    right: Optional["BaseNode"]

    def __init__(self, value: int):
        self.value = value
        self.left = None
        self.right = None

    def __str__(self) -> str:
        return f"{self.value}"


class Snapshot(List):
    def deepcopy(self):
        return _deepcopy(self)

    @property
    def root(self) -> Optional[BaseNode]:
        return self[0]


class BuildOrder(List):
    def to_snapshot(self) -> Snapshot:
        return Snapshot(self).deepcopy()


class BaseTree:
    root: Optional[BaseNode]
    snapshots: List[Snapshot]

    def __init__(self) -> None:
        self.snapshots = []

    def render(self, node: Optional[BaseNode], **kwargs) -> Output:
        return Output()

    def render_snapshots(self, **kwargs):
        return [self.render(snapshot.root, **kwargs) for snapshot in self.snapshots]

    def render_last_snapshot(self, **kwargs):
        return self.render(self.snapshots[-1].root, **kwargs)

    def take_snapshot(self, node: Optional[BaseNode]):
        _node = self.root if node is None and self.root is not None else node
        snapshot = self.to_build_order_pure(_node).to_snapshot()
        self.snapshots.append(snapshot)

    def to_build_order(self, node: Optional[BaseNode]) -> BuildOrder:
        if node is None:
            return BuildOrder([])

        levels = [[node]]
        level = [[node.left, node.right]]

        while not all(map(lambda path: all(node is None for node in path), level)):
            levels += level
            level = [
                [node.left, node.right] if node else [None, None]
                for branch in level
                for node in branch
            ]

        return BuildOrder(
            [node if node is not None else None for branch in levels for node in branch]
        )

    def to_build_order_pure(self, node: Optional[BaseNode]) -> BuildOrder:
        return BuildOrder(
            [node for node in self.to_build_order(node) if node is not None]
        )

    def to_build_order_values(self, node: Optional[BaseNode]) -> BuildOrder:
        return BuildOrder(
            [node.value for node in self.to_build_order(node) if node is not None]
        )

    def in_order_traversal(self, node: Optional[BaseNode]):
        if node is not None:
            yield from self.in_order_traversal(node.left)
            yield node.value
            yield from self.in_order_traversal(node.right)

    def preorder(self, node: Optional[BaseNode]):
        if node is not None:
            yield node.value
            yield from self.preorder(node.left)
            yield from self.preorder(node.right)

    def postorder(self, node: Optional[BaseNode]):
        if node is not None:
            yield from self.preorder(node.left)
            yield from self.preorder(node.right)
            yield node.value


if __name__ == "__main__":
    tree = BaseTree()

    tree.root = BaseNode(5)
    tree.root.left = BaseNode(3)
    tree.root.left.left = BaseNode(2)
    tree.root.left.right = BaseNode(4)
    tree.root.right = BaseNode(8)
    tree.root.right.left = BaseNode(7)
    tree.root.right.right = BaseNode(9)
    tree.root.right.right.right = BaseNode(10)

    assert [item for item in tree.preorder(tree.root)] == [5, 3, 2, 4, 8, 7, 9, 10]
    assert [item for item in tree.postorder(tree.root)] == [3, 2, 4, 8, 7, 9, 10, 5]
    assert [item for item in tree.in_order_traversal(tree.root)] == [
        2,
        3,
        4,
        5,
        7,
        8,
        9,
        10,
    ]
    assert [item for item in tree.to_build_order(tree.root)] == [
        5,
        3,
        8,
        2,
        4,
        7,
        9,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        10,
    ]
