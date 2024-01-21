from enum import Enum
from typing import Callable, Optional

from src.mermaid import Mermaid
from src.tree.base import BaseNode, BaseTree


class Color(Enum):
    RED = 1
    BLACK = 2


class Node(BaseNode):
    left: Optional["Node"]
    right: Optional["Node"]
    parent: Optional["Node"]
    color: Color
    _value: int
    value_finder: Callable[["Node"], int] = lambda x: x._value

    def __init__(self, value: int, color: Color):
        self._value = value
        self.color = color
        self.left = None
        self.right = None
        self.parent = None

    @property
    def value(self):
        return self._value

    def __str__(self):
        return f"{self.value}"


class RBTree(BaseTree):
    def __init__(self):
        super().__init__()
        self.NULL: Node = Node(0, Color.BLACK)
        self.NULL.left = None
        self.NULL.right = None
        self.root: Node = self.NULL

    def render(self, node: Optional[Node], **kwargs):
        return Mermaid.render_red_black_tree(node, **kwargs)

    def insert_node(self, node: Node):
        self._insert_node(node)
        self.take_snapshot(self.root)

    # Insert New Node
    def _insert_node(self, node: Node):
        node.color = Color.RED  # Set colour as Red
        node.left = self.NULL  # Set left child as NULL
        node.right = self.NULL  # Set right child as NULL

        y = None
        x: Node = self.root

        while x != self.NULL:  # Find position for new node
            y = x
            if node.value < x.value:
                x = x.left
            else:
                x = x.right

        node.parent = y  # Set parent of Node as y
        if y == None:  # If parent i.e, is none then it is root node
            self.root = node
        elif (
            node.value < y.value
        ):  # Check if it is right Node or Left Node by checking the value
            y.left = node
        else:
            y.right = node

        if node.parent == None:  # Root node is always Black
            node.color = Color.BLACK
            return

        if node.parent.parent == None:  # If parent of node is Root Node
            return

        self.fix_insert(node)  # Else call for Fix Up

    def minimum(self, node):
        while node.left != self.NULL:
            node = node.left
        return node

    # Code for left rotate
    def LR(self, x: Node):
        y = x.right  # Y = Right child of x
        x.right = y.left  # Change right child of x to left child of y
        if y.left != self.NULL:
            y.left.parent = x

        y.parent = x.parent  # Change parent of y as parent of x
        if x.parent == None:  # If parent of x == None ie. root node
            self.root = y  # Set y as root
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    # Code for right rotate
    def RR(self, x: Node):
        y = x.left  # Y = Left child of x
        x.left = y.right  # Change left child of x to right child of y
        if y.right != self.NULL:
            y.right.parent = x

        y.parent = x.parent  # Change parent of y as parent of x
        if x.parent == None:  # If x is root node
            self.root = y  # Set y as root
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    # Fix Up Insertion
    def fix_insert(self, k: Node):
        while k.parent.color == Color.RED:  # While parent is red
            if (
                k.parent == k.parent.parent.right
            ):  # if parent is right child of its parent
                u = k.parent.parent.left  # Left child of grandparent
                if (
                    u.color == Color.RED
                ):  # if color of left child of grandparent i.e, uncle node is red
                    u.color = (
                        Color.BLACK
                    )  # Set both children of grandparent node as black
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED  # Set grandparent node as Red
                    k = (
                        k.parent.parent
                    )  # Repeat the algo with Parent node to check conflicts
                else:
                    if k == k.parent.left:  # If k is left child of it's parent
                        k = k.parent
                        self.RR(k)  # Call for right rotation
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    self.LR(k.parent.parent)
            else:  # if parent is left child of its parent
                u = k.parent.parent.right  # Right child of grandparent
                if (
                    u.color == Color.RED
                ):  # if color of right child of grandparent i.e, uncle node is red
                    u.color = Color.BLACK  # Set color of childs as black
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED  # set color of grandparent as Red
                    k = (
                        k.parent.parent
                    )  # Repeat algo on grandparent to remove conflicts
                else:
                    if k == k.parent.right:  # if k is right child of its parent
                        k = k.parent
                        self.LR(k)  # Call left rotate on parent of k
                    k.parent.color = Color.BLACK
                    k.parent.parent.color = Color.RED
                    self.RR(k.parent.parent)  # Call right rotate on grandparent
            if k == self.root:  # If k reaches root then break
                break
        self.root.color = Color.BLACK  # Set color of root as black

    # Function to fix issues after deletion
    def fix_delete(self, x: Node):
        while (
            x != self.root and x.color == Color.BLACK
        ):  # Repeat until x reaches nodes and color of x is black
            if x == x.parent.left:  # If x is left child of its parent
                s = x.parent.right  # Sibling of x
                if s.color == Color.RED:  # if sibling is red
                    s.color = Color.BLACK  # Set its color to black
                    x.parent.color = Color.RED  # Make its parent red
                    self.LR(x.parent)  # Call for left rotate on parent of x
                    s = x.parent.right
                # If both the child are black
                if s.left.color == Color.BLACK and s.right.color == Color.BLACK:
                    s.color = Color.RED  # Set color of s as red
                    x = x.parent
                else:
                    if s.right.color == Color.BLACK:  # If right child of s is black
                        s.left.color = Color.BLACK  # set left child of s as black
                        s.color = Color.RED  # set color of s as red
                        self.RR(s)  # call right rotation on x
                        s = x.parent.right

                    s.color = x.parent.color
                    x.parent.color = Color.BLACK  # Set parent of x as black
                    s.right.color = Color.BLACK
                    self.LR(x.parent)  # call left rotation on parent of x
                    x = self.root
            else:  # If x is right child of its parent
                s = x.parent.left  # Sibling of x
                if s.color == Color.RED:  # if sibling is red
                    s.color = Color.BLACK  # Set its color to black
                    x.parent.color = Color.RED  # Make its parent red
                    self.RR(x.parent)  # Call for right rotate on parent of x
                    s = x.parent.left

                if s.right.color == Color.BLACK and s.right.color == Color.BLACK:
                    s.color = Color.RED
                    x = x.parent
                else:
                    if s.left.color == Color.BLACK:  # If left child of s is black
                        s.right.color = Color.BLACK  # set right child of s as black
                        s.color = Color.RED
                        self.LR(s)  # call left rotation on x
                        s = x.parent.left

                    s.color = x.parent.color
                    x.parent.color = Color.BLACK
                    s.left.color = Color.BLACK
                    self.RR(x.parent)
                    x = self.root
        x.color = Color.BLACK

    # Function to transplant nodes
    def __rb_transplant(self, u, v):
        if u.parent == None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    # Function to handle deletion
    def delete_node_helper(self, node: Node, key: int):
        z = self.NULL
        while (
            node != self.NULL
        ):  # Search for the node having that value/ key and store it in 'z'
            if node.value == key:
                z = node

            if node.value <= key:
                node = node.right
            else:
                node = node.left

        if z == self.NULL:  # If Kwy is not present then deletion not possible so return
            print("Value not present in Tree !!")
            return

        y = z
        y_original_color = y.color  # Store the color of z- node
        if z.left == self.NULL:  # If left child of z is NULL
            x = z.right  # Assign right child of z to x
            self.__rb_transplant(z, z.right)  # Transplant Node to be deleted with x
        elif z.right == self.NULL:  # If right child of z is NULL
            x = z.left  # Assign left child of z to x
            self.__rb_transplant(z, z.left)  # Transplant Node to be deleted with x
        else:  # If z has both the child nodes
            y = self.minimum(z.right)  # Find minimum of the right sub tree
            y_original_color = y.color  # Store color of y
            x = y.right
            if y.parent == z:  # If y is child of z
                x.parent = y  # Set parent of x as y
            else:
                self.__rb_transplant(y, y.right)
                y.right = z.right
                y.right.parent = y

            self.__rb_transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        if y_original_color == Color.BLACK:  # If color is black then fixing is needed
            self.fix_delete(x)

    # Deletion of node
    def delete_node(self, val):
        self.delete_node_helper(self.root, val)  # Call for deletion
        self.take_snapshot(self.root)
