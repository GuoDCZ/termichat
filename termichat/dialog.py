"""
Define the dialog structure for displaying chat messages.
"""

from textual.app import App, ComposeResult
from typing import List, Optional
from textual.events import Focus, Mount, Blur
from textual.widgets import Markdown, Static, TextArea
from textual.containers import ScrollableContainer
from textual.binding import Binding
from threading import Thread
import time

from tree import Tree, Node
from gpt import cmpl_request

EDIT_BOT_MESSAGE = "(Press ctrl+s to regenerate the response)"

def subtitle(n: int, i: int) -> str:
    if n == 0:
        return ""
    return " *"*i + f"[{i}]" + "* "*(n-i-1)

class Message(Static, can_focus=True):
    """Message structure for displaying chat messages."""

    class MyTextArea(TextArea):

        BINDINGS = {
            Binding("ctrl+s", "submit", "Submit", priority=True),
        }

        def action_submit(self) -> None:
            """Blurs the text area."""
            self.parent.add(self.text)

        def _on_blur(self, event: Blur) -> None:
            """Blurs the text area."""
            mds = self.parent.query(Markdown)
            for md in mds:
                md.remove_class("hidden")
            self.remove()
            return super()._on_blur(event)

    node: Node
    dialog: "Dialog"

    BINDINGS = {
        Binding("space", "edit", "Edit"),
        Binding("enter", "edit", "Edit"),
        Binding("up", "move_up", "Move up"),
        Binding("down", "move_down", "Move down"),
        Binding("left", "move_left", "Move left"),
        Binding("right", "move_right", "Move right"),
        Binding("delete", "remove", "Remove"),
    }

    def __init__(self, node: Node, dialog: "Dialog", **kwargs):
        """Initialize the message."""
        self.node = node
        self.dialog = dialog
        self.node.on_content_change = self.call_content_change
        self.node.on_visible = self.call_visible
        self.node.on_invisible = self.call_invisible
        self.node.on_destroy = self.call_destroy
        self.node.on_add = self.call_add
        self.node.on_focus = self.call_focus
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Compose the message with the node data."""
        # content = self.node.content
        # if len(content) == 0 :
        #     raise NotImplementedError
        yield Markdown(self.node.content)
    
    def on_mount(self) -> None:
        """Focus the message."""
        if self.node.role is not None:
            self.border_title = self.node.role
            self.border_subtitle = subtitle(len(self.node.children), self.node.index)
        # self.add_class("hidden")

    # Callbacks from backend
    def call_content_change(self) -> None:
        """Call the content change."""
        try:
            self.query_one(Markdown).update(self.node.content)
        except:
            pass
        self.border_subtitle = subtitle(len(self.node.children), self.node.index)

    def call_visible(self) -> None:
        """Call the visible."""
        self.remove_class("hidden")

    def call_invisible(self) -> None:
        """Call the invisible."""
        self.add_class("hidden")

    def call_destroy(self) -> None:
        """Call the destroy."""
        self.remove()

    def call_add(self, node: Node) -> None:
        """Call the add."""
        self.dialog.mount_single(node)
        # node.on_focus()

    def call_focus(self) -> None:
        """Call the focus."""
        self.focus()

    # def _on_focus(self, event: Focus) -> None:
    #     """Focus the message."""
    #     self.cancel_edit()
    #     return super()._on_focus(event)
    
    def action_edit(self) -> None:
        """Edit the message."""
        self.query_one(Markdown).add_class("hidden")
        if self.node.role == "user":
            textarea = Message.MyTextArea(self.node.content)
        elif self.node.role == "assistant":
            textarea = Message.MyTextArea(EDIT_BOT_MESSAGE, read_only=True)
        self.mount(textarea)
        textarea.focus()

    # def action_cancel(self) -> None:
    #     """Cancel editing the message."""
    #     self.cancel_edit()

    def action_move_up(self) -> None:
        """Move up in the message."""
        if self.node.parent:
            self.node.parent.on_focus()

    def action_move_down(self) -> None:
        """Move down in the message."""
        if self.node.child:
            self.node.child.on_focus()

    def action_move_left(self) -> None:
        """Move left in the message."""
        if self.node.index is not None:
            if self.node.index > 0:
                self.node.switch(self.node.index - 1)

    def action_move_right(self) -> None:
        """Move right in the message."""
        if self.node.index is not None:
            if self.node.index < len(self.node.children) - 1:
                self.node.switch(self.node.index + 1)

    def add(self, content: str) -> None:
        """Add a user message to the message."""
        self.node.add(content)
        response = self.node.child.send()
        self.node.child.add("")
        # self.node.child.child.stream_update(response)
        # self.node.child.child.on_focus()
        self.node.stream_update(response)
        self.node.on_focus()

    def action_remove(self) -> None:
        """Remove the message."""
        self.node.remove_child()

    # def refresh_branch(self) -> None:
    #     """Refresh the branch of the message."""
    #     self.cancel_edit()
    #     # update the message content
    #     self.query_one(Markdown).update(self.node.data["content"])
    #     # unmount all subsequent messages
    #     messages = list(self.parent.query(Message))
    #     index = messages.index(self)
    #     for message in messages[index + 1:]:
    #         message.remove()
    #     # mount all subsequent messages
    #     for node in self.node.path()[1:]:
    #         self.parent.mount(Message(node=node))
    #     # focus the message
    #     self.focus()
    
    # def cancel_edit(self) -> None:
    #     """Cancel editing the message."""
    #     textareas = self.query(Message.MyTextArea)
    #     for textarea in textareas:
    #         textarea.remove()
    #     self.query_one(Markdown).remove_class("hidden")


class Dialog(ScrollableContainer, can_focus=False):
    """Dialog structure for displaying chat messages."""

    _tree: Tree

    def __init__(self, tree: Tree = None, **kwargs):
        """Initialize the dialog."""
        super().__init__(**kwargs)
        self._tree = tree if tree is not None else Tree()

    def compose(self) -> ComposeResult:
        """Compose the dialog with messages."""
        yield from self.compose_helper(self._tree.root)

    def compose_helper(self, node: Node) -> ComposeResult:
        """Compose the dialog with messages."""
        yield Message(node=node, dialog=self)
        for child in node.children:
            yield from self.compose_helper(child)
    
    def mount_single(self, node: Node) -> None:
        """Mount a single message."""
        msg = Message(node=node, dialog=self)
        self.mount(msg)
        # if 'markdown' not in msg.__dict__:
        #     msg.markdown = Markdown(node.content)
        #     msg.mount(msg.markdown)
        # if len(msg.query(Markdown)) == 2:
        #     raise NotImplementedError

    # def move_up(self, message: Message) -> None:
    #     """Move up the message."""
    #     index = self.messages.index(message)
    #     if index > 0:
    #         self.messages[index - 1].focus()

    # def move_down(self, message: Message) -> None:
    #     """Move down the message."""
    #     index = self.messages.index(message)
    #     if index < len(self.messages) - 1:
    #         self.messages[index + 1].focus()
