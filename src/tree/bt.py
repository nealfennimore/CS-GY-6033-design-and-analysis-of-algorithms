from typing import Optional

from binarytree import Node as _Node

from src.mermaid import Mermaid
from src.tree.base import BaseNode, BaseTree


class Node(_Node, BaseNode):
    pass


class Tree(BaseTree):
    def __init__(self):
        super().__init__()
        self.root = None

    def render(self, node: Optional[Node], **kwargs):
        return Mermaid.render_binary_search_tree(node, **kwargs)

    def insert(self, key: int):
        self._insert(key)
        self.take_snapshot(self.root)

    def _insert(self, key):
        if self.root is None:
            self.root = Node(key)
        else:
            self._insert_recursive(self.root, key)

    def _insert_recursive(self, current_node, key):
        if key < current_node.val:
            if current_node.left is None:
                current_node.left = Node(key)
            else:
                self._insert_recursive(current_node.left, key)
        elif key > current_node.val:
            if current_node.right is None:
                current_node.right = Node(key)
            else:
                self._insert_recursive(current_node.right, key)

    def delete(self, key):
        self.root = self._delete_recursive(self.root, key)
        self.take_snapshot(self.root)

    def _delete_recursive(self, current_node, key):
        if current_node is None:
            return current_node

        if key < current_node.val:
            current_node.left = self._delete_recursive(current_node.left, key)
        elif key > current_node.val:
            current_node.right = self._delete_recursive(current_node.right, key)
        else:
            if current_node.left is None:
                return current_node.right
            elif current_node.right is None:
                return current_node.left

            current_node.val = self._min_value_node(current_node.right).val
            current_node.right = self._delete_recursive(
                current_node.right, current_node.val
            )

        return current_node

    def search(self, key):
        return self._search_recursive(self.root, key)

    def _search_recursive(self, current_node, key) -> Optional[Node]:
        if current_node is None or current_node.val == key:
            return current_node

        if key < current_node.val:
            return self._search_recursive(current_node.left, key)
        else:
            return self._search_recursive(current_node.right, key)

    def _min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current
