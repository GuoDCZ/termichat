"""
Define the dialog structure for displaying chat messages.
"""

from textual.app import App, ComposeResult
from typing import List, Optional
from textual.widgets import Markdown, Static, TextArea
from tree import Tree, Node, Render

class Message(Static):
    """Message structure for displaying chat messages."""

    def __init__(self, data: dict) -> None:
        self.data = data
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(f"@{self.data['role']}")
        yield Markdown(self.data["text"])


class Dialog(Static, can_focus=True):
    """Dialog structure for displaying chat messages."""

    def __init__(self, tree: Tree) -> None:
        """Initialize the dialog with a tree structure."""
        self.messages: List[Message] = []
        self.t: Tree = tree
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the dialog with messages."""
        path = self.t.get_path()
        for node in path[1:]:
            message = Message(node.data)
            self.messages.append(message)
            yield message

    def pop(self) -> None:
        """Remove the last message from the dialog."""
        if self.messages:
            message = self.messages.pop()
            message.remove()
    
    def push(self) -> None:
        """Mount the last message back to the dialog."""
        message = Message(self.t.curr.data)
        self.messages.append(message)
        self.mount(message)
