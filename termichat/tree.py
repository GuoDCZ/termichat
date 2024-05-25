"""
Define N-ary tree structure for storing chat messages.

The tree structure is used to store chat messages in a hierarchical way. It
also defines the current node and the current path in the tree. The tree also
supports moving up and down the tree, adding new messages, and getting the
current path.
"""

from typing import List, Optional, Any
from dataclasses import dataclass, field
from functools import cached_property
from threading import Thread, Event
import pickle
import asyncio

from gpt import api_request, stream_request


@dataclass
class Node:
    """N-ary node structure for storing children nodes."""

    _parent_content: str = ""
    # Invariant: index is None <=> children is [] <=> child is None
    children: List["Node"] = field(default_factory=list)
    # Any changes to index should be handled by self.switch()
    index: Optional[int] = None
    parent: Optional["Node"] = None

    # front-end weight
    block: "Block" = None

    update_event = Event()
    finish_event = Event()

    @property
    def child(self) -> Optional["Node"]:
        if self.index is not None:
            return self.children[self.index]
        return None
    
    @property
    def content(self) -> str:
        if self.child is not None:
            return self.child._parent_content
        return ""
    
    @cached_property
    def role(self) -> str:
        if self.parent is None:
            return "system"
        elif self.parent.role == "user":
            return "assistant"
        return "user"
    
    @property
    def message(self) -> str:
        return {"role": self.role, "content": self.content}
    
    @property
    def messages(self) -> List[dict]:
        if self.parent is None:
            return [self.message]
        return self.parent.messages + [self.message]

    def switch(self, index: int) -> None:
        if index is None:
            return
        if index < 0:
            index = 0
        elif index >= len(self.children):
            index = len(self.children) - 1
        else:
            self.index = index

    def add(self, content: str) -> "Node":
        """Add a new child node."""
        node = Node(_parent_content=content, parent=self)
        self.children.append(node)
        self.switch(len(self.children) - 1)
        return node
    
    def make_request(self) -> str:
        """Make a request to the bot."""
        if self.role != "user":
            raise ValueError("Only user nodes can make requests.")
        return stream_request(self.messages)

    # def send(self) -> None:
    #     """Send the messages to the bot."""
    #     return api_request(self.messages) # FIXME: handle exceptions

    def stream_update(self, response: Any, callback: Optional[callable] = None) -> None:
        """Stream the response to the current node."""
        self._parent_content = ""
        for chunk in response:
            chuck_msg = chunk['choices'][0]['delta']
            if 'content' in chuck_msg:
                self._parent_content += chuck_msg['content']
        callback() if callback else None

    def remove_child(self) -> None:
        """Remove the current child node."""
        if self.child is not None:
            index = self.index
            self.child._remove()
            self.children.remove(self.child)
            self.switch(None)
            if len(self.children) == 0:
                index = None
            elif self.index == len(self.children):
                index -= 1
            self.switch(index)

    def _remove(self) -> None:
        """Remove the current node and all its children."""
        self.on_destroy()
        for child in self.children:
            child._remove()


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
    