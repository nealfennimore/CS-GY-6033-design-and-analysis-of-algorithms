from typing import List, Optional, Tuple

from src.mermaid import Mermaid
from src.tree.base import BaseNode, BaseTree


class Interval(Tuple[int, int]):
    def overlaps(self, other: "Interval"):
        return self[0] <= other[1] and self[1] >= other[0]


class Node(BaseNode):
    interval: Interval
    _max_end: Optional[int] = None
    left: Optional["Node"] = None
    right: Optional["Node"] = None

    def __init__(self, interval: Interval):
        self.interval = Interval(interval)

    @property
    def start(self):
        return self.interval[0]

    @property
    def end(self):
        return self.interval[1]

    @property
    def max_end(self):
        if self._max_end is not None:
            return self._max_end
        return self.end

    @max_end.setter
    def max_end(self, value: int):
        self._max_end = value

    def __str__(self):
        return f"{self.start},{self.end}"


class IntervalTree(BaseTree):
    root: Optional[Node] = None

    def __init__(self) -> None:
        super().__init__()

    def render(self, node: Optional[Node], **kwargs):
        return Mermaid.render_interval_tree(node, **kwargs)

    def insert(self, interval: Interval):
        if self.root is None:
            self.root = Node(interval)
        else:
            self._insert_helper(self.root, interval)

        self.take_snapshot(self.root)

    def _insert_helper(self, node: Node, interval: Interval):
        start, end = interval
        node.max_end = max(node.max_end, end)

        if start < node.start:
            if node.left is None:
                node.left = Node(interval)
            else:
                self._insert_helper(node.left, interval)
        else:
            if node.right is None:
                node.right = Node(interval)
            else:
                self._insert_helper(node.right, interval)

    def search(self, interval: Interval):
        overlaps: List[Interval] = []
        for overlap in self._search_helper(self.root, interval):
            overlaps.append(overlap)
        return overlaps

    def _search_helper(self, node: Optional[Node], interval: Interval):
        if node is None:
            return None

        start, _ = interval

        if node.interval.overlaps(interval):
            yield node.interval

        if node.left is not None and node.left.max_end >= start:
            # print(node.interval, '->', node.left.interval)
            yield from self._search_helper(node.left, interval)

        # if node.right is not None:
        #     print(node.interval, '->', node.right.interval)
        yield from self._search_helper(node.right, interval)
