from typing import Optional

from src.mermaid import Mermaid
from src.tree.base import BaseNode, BaseTree


class Node(BaseNode):
    def __init__(self, value: int):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1


class AVLTree(BaseTree):
    root: Optional[Node] = None

    def __init__(self) -> None:
        super().__init__()

    def render(self, node: Optional[Node], **kwargs):
        _node = node or self.root
        assert _node is not None
        return Mermaid.render_avl_tree(_node, **kwargs)

    def insert(self, node: Optional[Node], value: int):
        _node = self._insert(node, value)
        self.take_snapshot(_node)
        return _node

    def _insert(self, node: Optional[Node], value: int):
        if not node:
            return Node(value)
        elif value < node.value:
            node.left = self.insert(node.left, value)
        else:
            node.right = self.insert(node.right, value)

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

        return self.rebalance(node) or node

    def delete(self, node: Optional[Node], value: int):
        _node = self._delete(node, value)
        self.take_snapshot(_node)
        return _node

    def _delete(self, node: Optional[Node], value: int):
        if not node:
            return node
        elif value < node.value:
            node.left = self.delete(node.left, value)
        elif value > node.value:
            node.right = self.delete(node.right, value)
        else:
            if node.left is None:
                temp = node.right
                node = None
                return temp
            elif node.right is None:
                temp = node.left
                node = None
                return temp
            temp = self.get_min_node_value(node.right)
            node.value = temp.value
            node.right = self.delete(node.right, temp.value)

        if node is None:
            return node

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

        return self.rebalance(node) or node

    def rebalance(self, node: Node):
        balance_factor = self.get_balance(node)

        if balance_factor > 1:
            if self.get_balance(node.left) >= 0:
                return self.right_rotate(node)
            else:
                node.left = self.left_rotate(node.left)
                return self.right_rotate(node)

        if balance_factor < -1:
            if self.get_balance(node.right) <= 0:
                return self.left_rotate(node)
            else:
                node.right = self.right_rotate(node.right)
                return self.left_rotate(node)

        return None

    def left_rotate(self, z: Node):
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    def right_rotate(self, z: Node):
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    def get_height(self, node: Node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node: Node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)

    def get_min_node_value(self, node: Node):
        if node is None or node.left is None:
            return node
        return self.get_min_node_value(node.left)
