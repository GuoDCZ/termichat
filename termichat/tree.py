"""
Define N-ary tree structure for storing chat messages.

The tree structure is used to store chat messages in a hierarchical way. It
also defines the current node and the current path in the tree. The tree also
supports moving up and down the tree, adding new messages, and getting the
current path.
"""

from typing import List, Optional
from dataclasses import dataclass, field
from functools import cached_property
import pickle


@dataclass
class Node:
    """N-ary node structure for storing children nodes."""

    datas: List[dict] = field(default_factory=list)
    children: List["Node"] = field(default_factory=list)
    index: Optional[int] = None
    parent: Optional["Node"] = None

    @cached_property
    def role(self) -> str:
        """Return the default role."""
        if self.parent is None:
            return "system"
        if self.parent.role == "user":
            return "assistant"
        return "user"

    @property
    def data(self) -> dict:
        """Return the current data."""
        if self.index is not None:
            return self.datas[self.index]
        return self.make_data("")
    
    @property
    def child(self) -> Optional["Node"]:
        """Return the current child."""
        if self.index is not None:
            return self.children[self.index]
        return None
    
    def make_data(self, content: str) -> dict:
        """Make a new data."""
        return {"role": self.role, "content": content}
    
    def path(self) -> List["Node"]:
        """Return the path starting from the current node."""
        path = []
        node = self
        while node is not None:
            path.append(node)
            node = node.child
        return path
    
    def get_messages(self) -> List[dict]:
        """
        Return the messages from the root to the current node.
        
        This can be directly used by API.
        """
        path = []
        node = self
        while node is not None:
            path.append(node.data)
            node = node.parent
        return path[::-1]

    def add(self, content: str) -> None:
        """
        Add a new data.
        
        NOTE: The new data is added to the end of self.children.
        This can be modified to add the new data at a specific index.
        """
        data = self.make_data(content)
        self.datas.append(data)
        self.children.append(Node(parent=self))
        self.index = len(self.datas) - 1

    def remove(self) -> None:
        """
        Remove the current data.
        
        NOTE: User may expect to move to the previous data after removing the
        very last data. This should be handled elsewhere.
        """
        if self.index is not None:
            self.datas.pop(self.index)
            self.children.pop(self.index)
            if self.index == 0:
                self.index = None
            elif self.index >= len(self.datas):
                self.index = len(self.datas) - 1


@dataclass
class Tree:
    """N-ary tree structure for storing chat messages."""

    root: Node = field(default_factory=Node)

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
        return tree

    # def get_path_before(self, node: Node) -> List[Node]:
    #     """Return the path before the current node."""
    #     path = []
    #     while node.parent is not None:
    #         path.append(node)
    #         node = node.parent
    #     return path[::-1]
    
    # def get_path_after(self, node: Node) -> List[Node]:
    #     """Return the path after the current node."""
    #     path = []
    #     while node.child is not None:
    #         path.append(node)
    #         node = node.child
    #     return path
    
    # def get_path(self, node: Optional[Node] = None) -> List[Node]:
    #     """Return the path from the root to the current node."""
    #     if node is None:
    #         node = self.root
    #     return self.get_path_before(node) + [node] + self.get_path_after(node)

    # def get_dialog(self, node: Optional[Node] = None) -> List[dict]:
    #     """Return the dialog from the current node."""
    #     return [node.data for node in self.get_path_before(node)]

    # def insert(self, data) -> None:
    #     """Insert a new node as a child of the current node."""
    #     node = Node(data=data, parent=self.curr)
    #     if self.curr.index is None:
    #         self.curr.index = 0
    #     else:
    #         self.curr.index += 1
    #     self.curr.children.insert(self.curr.index, node)

    # def remove(self) -> None:
    #     """Remove the current child node of the current node."""
    #     if self.curr.index is not None:
    #         self.curr.children.pop(self.curr.index)
    #         if self.curr.index >= len(self.curr.children):
    #             self.curr.index = len(self.curr.children) - 1

    # def insert_move(self, data) -> None:
    #     """Insert a new node and move to it."""
    #     self.insert(data)
    #     self.move_down()

    # def remove_move(self) -> None:
    #     """Move up and remove all children of the current node."""
    #     self.move_up()
    #     self.curr.children = []

    # def move_up(self) -> None:
    #     """Move up the tree to the parent node."""
    #     if self.curr.parent is not None:
    #         self.curr = self.curr.parent
    #         self.renders.append(Render.POP)

    # def move_down(self) -> None:
    #     """Move down the tree to the current child node."""
    #     if self.curr.child is not None:
    #         self.curr = self.curr.child
    #         self.renders.append(Render.PUSH)

    # def move_left(self) -> None:
    #     """Move left in the current node's children."""
    #     if self.curr.index is not None:
    #         if self.curr.index > 0:
    #             self.curr.index -= 1
    #             self.renders.append(Render.REPEAT)

    # def move_right(self) -> None:
    #     """Move right in the current node's children."""
    #     if self.curr.index is not None:
    #         if self.curr.index < len(self.curr.children) - 1:
    #             self.curr.index += 1
    #             self.renders.append(Render.REPEAT)

    # def move_top(self) -> None:
    #     """Move to the top of the tree."""
    #     self.curr = self.root
    #     self.renders.append(Render.RELOAD)

    # def move_bottom(self) -> None:
    #     """Move to the bottom of the tree."""
    #     while self.curr.child is not None:
    #         self.curr = self.curr.child
    #     self.renders.append(Render.RELOAD)

    # def move_first(self) -> None:
    #     """Move to the first child of the current node."""
    #     if self.curr.child is not None:
    #         self.curr.index = 0
    #         self.renders.append(Render.REPEAT)

    # def move_last(self) -> None:
    #     """Move to the last child of the current node."""
    #     if self.curr.child is not None:
    #         self.curr.index = len(self.curr.children) - 1
    #         self.renders.append(Render.REPEAT)
