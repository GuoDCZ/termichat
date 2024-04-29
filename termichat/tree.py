"""
Define N-ary tree structure for storing chat messages.

The tree structure is used to store chat messages in a hierarchical way. It
also defines the current node and the current path in the tree. The tree also
supports moving up and down the tree, adding new messages, and getting the
current path.
"""

from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum
import pickle


@dataclass
class Node:
    """Node in the N-ary tree."""

    data: dict = field(default_factory=dict)
    parent: Optional["Node"] = None
    children: List["Node"] = field(default_factory=list)
    index: Optional[int] = None

    @property
    def child(self) -> Optional["Node"]:
        """Return the current child node."""
        if self.index is not None:
            return self.children[self.index]
        return None


class Render(Enum):
    """Enum for rendering instructions."""

    POP = "POP"
    PUSH = "PUSH"
    REPEAT = "REPEAT"
    RELOAD = "RELOAD"


@dataclass
class Tree:
    """N-ary tree structure for storing chat messages."""

    root: Node = field(default_factory=Node)
    curr: Node = root
    renders: List[Render] = field(default_factory=list)

    def save(self, path: str = "tree") -> None:
        """Save the tree to a file."""
        with open(f"{path}.pkl", "wb") as f:
            pickle.dump(self.root, f)

    @classmethod
    def load(cls, path: str = "tree") -> "Tree":
        """Load the tree from a file."""
        try:
            with open(f"{path}.pkl", "rb") as f:
                root = pickle.load(f)
        except FileNotFoundError:
            root = Node()
        tree = cls()
        tree.root = root
        tree.curr = root
        tree.move_bottom()
        return tree

    def get_path(self) -> List:
        """Return the path from the root to the current node."""
        path = []
        node = self.curr
        while node is not None:
            path.append(node)
            node = node.parent
        return path[::-1]

    def insert(self, data) -> None:
        """Insert a new node as a child of the current node."""
        node = Node(data=data, parent=self.curr)
        if self.curr.index is None:
            self.curr.index = 0
        else:
            self.curr.index += 1
        self.curr.children.insert(self.curr.index, node)

    def remove(self) -> None:
        """Remove the current child node of the current node."""
        if self.curr.index is not None:
            self.curr.children.pop(self.curr.index)
            if self.curr.index >= len(self.curr.children):
                self.curr.index = len(self.curr.children) - 1

    def insert_move(self, data) -> None:
        """Insert a new node and move to it."""
        self.insert(data)
        self.move_down()

    def remove_move(self) -> None:
        """Move up and remove all children of the current node."""
        self.move_up()
        self.curr.children = []

    def move_up(self) -> None:
        """Move up the tree to the parent node."""
        if self.curr.parent is not None:
            self.curr = self.curr.parent
            self.renders.append(Render.POP)

    def move_down(self) -> None:
        """Move down the tree to the current child node."""
        if self.curr.child is not None:
            self.curr = self.curr.child
            self.renders.append(Render.PUSH)

    def move_left(self) -> None:
        """Move left in the current node's children."""
        if self.curr.index is not None:
            if self.curr.index > 0:
                self.curr.index -= 1
                self.renders.append(Render.REPEAT)

    def move_right(self) -> None:
        """Move right in the current node's children."""
        if self.curr.index is not None:
            if self.curr.index < len(self.curr.children) - 1:
                self.curr.index += 1
                self.renders.append(Render.REPEAT)

    def move_top(self) -> None:
        """Move to the top of the tree."""
        self.curr = self.root
        self.renders.append(Render.RELOAD)

    def move_bottom(self) -> None:
        """Move to the bottom of the tree."""
        while self.curr.child is not None:
            self.curr = self.curr.child
        self.renders.append(Render.RELOAD)

    def move_first(self) -> None:
        """Move to the first child of the current node."""
        if self.curr.child is not None:
            self.curr.index = 0
            self.renders.append(Render.REPEAT)

    def move_last(self) -> None:
        """Move to the last child of the current node."""
        if self.curr.child is not None:
            self.curr.index = len(self.curr.children) - 1
            self.renders.append(Render.REPEAT)
