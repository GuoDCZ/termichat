"""
Define the dialog structure for displaying chat messages.
"""

from textual.app import App, ComposeResult
from typing import List, Optional
from textual.events import Focus, Mount, Blur
from textual.widgets import Markdown, Static, TextArea
from textual.binding import Binding

from tree import Tree, Node
from gpt import cmpl_request

EDIT_BOT_MESSAGE = "(Press ctrl+s to regenerate the response)"

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
            if self.parent:
                self.parent.query_one(Markdown).remove_class("hidden")
            self.remove()
            return super()._on_blur(event)

    node: Node

    BINDINGS = {
        Binding("space", "edit", "Edit"),
        Binding("enter", "edit", "Edit"),
        Binding("up", "move_up", "Move up"),
        Binding("down", "move_down", "Move down"),
        Binding("left", "move_left", "Move left"),
        Binding("right", "move_right", "Move right"),
        Binding("delete", "remove", "Remove"),
    }

    def __init__(self, node: Node, **kwargs):
        """Initialize the message."""
        self.node = node
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Compose the message with the node data."""
        yield Markdown(self.node.data["content"])

    def on_mount(self) -> None:
        """Focus the message."""
        self.border_title = self.node.data["role"]

    def _on_focus(self, event: Focus) -> None:
        """Focus the message."""
        self.cancel_edit()
        return super()._on_focus(event)
    
    def action_edit(self) -> None:
        """Edit the message."""
        self.query_one(Markdown).add_class("hidden")
        if self.node.data["role"] == "user":
            textarea = Message.MyTextArea(self.node.data["content"])
        elif self.node.data["role"] == "assistant":
            textarea = Message.MyTextArea(EDIT_BOT_MESSAGE, read_only=True)
        self.mount(textarea)
        textarea.focus()

    def action_cancel(self) -> None:
        """Cancel editing the message."""
        self.cancel_edit()

    def action_move_up(self) -> None:
        """Move up in the message."""
        self.parent.move_up(self)

    def action_move_down(self) -> None:
        """Move down in the message."""
        self.parent.move_down(self)

    def action_move_left(self) -> None:
        """Move left in the message."""
        if self.node.index is not None:
            if self.node.index > 0:
                self.node.index -= 1
                self.refresh_branch()

    def action_move_right(self) -> None:
        """Move right in the message."""
        if self.node.index is not None:
            if self.node.index < len(self.node.children) - 1:
                self.node.index += 1
                self.refresh_branch()

    def add(self, content: str) -> None:
        """Add a user message to the message."""
        if self.node.role == "user":
            self.node.add(content)
            self.parent.send_message(self)
        else:
            self.parent.resend_message(self)
        self.refresh_branch()

    def action_remove(self) -> None:
        """Remove the message."""
        self.node.remove()
        self.refresh_branch()

    def refresh_branch(self) -> None:
        """Refresh the branch of the message."""
        self.cancel_edit()
        # update the message content
        self.query_one(Markdown).update(self.node.data["content"])
        # unmount all subsequent messages
        messages = list(self.parent.query(Message))
        index = messages.index(self)
        for message in messages[index + 1:]:
            message.remove()
        # mount all subsequent messages
        for node in self.node.path()[1:]:
            self.parent.mount(Message(node=node))
        # focus the message
        self.focus()
    
    def cancel_edit(self) -> None:
        """Cancel editing the message."""
        textareas = self.query(Message.MyTextArea)
        for textarea in textareas:
            textarea.remove()
        self.query_one(Markdown).remove_class("hidden")


class Dialog(Static):
    """Dialog structure for displaying chat messages."""

    _tree: Tree

    messages: List[Message] = []

    def __init__(self, tree: Tree = None, **kwargs):
        """Initialize the dialog."""
        super().__init__(**kwargs)
        self._tree = tree if tree is not None else Tree()

    def compose(self) -> ComposeResult:
        """Compose the dialog with messages."""
        for node in self._tree.root.path():
            message = Message(node=node)
            self.messages.append(message)
            yield message

    def move_up(self, message: Message) -> None:
        """Move up the message."""
        index = self.messages.index(message)
        if index > 0:
            self.messages[index - 1].focus()

    def move_down(self, message: Message) -> None:
        """Move down the message."""
        index = self.messages.index(message)
        if index < len(self.messages) - 1:
            self.messages[index + 1].focus()

    def send_message(self, message: Message) -> None:
        """Send a message."""

        messages = message.node.get_messages()

        index = self.messages.index(message)
        if index < len(self.messages) - 1:
            message = self.messages[index + 1]

        response = cmpl_request(messages)
        
        content = ""
        for chunk in response:
            chuck_msg = chunk['choices'][0]['delta']
            if 'content' in chuck_msg:
                delta_content = chuck_msg['content']
                content += delta_content
                message.query_one(Markdown).update(content)
                
        message.focus()