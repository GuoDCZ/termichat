"""
Define the dialog app.

The dialog app is used to display chat messages in a hierarchical way. It uses
the tree structure to store chat messages and the dialog structure to display
them. The app also defines key bindings for moving up and down the dialog.
"""

from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.binding import Binding
from typing import Optional
from dialog import Dialog
from tree import Tree, Node

def gen_tree():
    tree = Tree()
    node = tree.root
    node.add("User message 1")
    node = node.child
    node.add("Bot response 1")
    node = node.child
    node.add("User message 2")
    node = node.child
    node.add("Bot response 2")
    return tree

class DialogApp(App):

    CSS_PATH = "style.tcss"

    # BINDINGS = [
    #     Binding("up", "move_up", "Move up"),
    #     Binding("down", "move_down", "Move down"),
    #     Binding("left", "move_left", "Move left"),
    #     Binding("right", "move_right", "Move right"),
    # ]

    def compose(self) -> ComposeResult:
        """Compose the dialog app."""
        dialog = Dialog(tree=gen_tree())
        yield dialog

    # def render(self) -> None:
    #     """Render the dialog app."""
    #     while self.t.renders:
    #         render = self.t.renders.pop(0)
    #         if render == Render.PUSH:
    #             self.dialog.push()
    #         elif render == Render.POP:
    #             self.dialog.pop()
    #         elif render == Render.REPEAT:
    #             self.dialog.push()
    #             self.dialog.pop()
    #         elif render == Render.RELOAD:
    #             self.dialog = Dialog(self.t)
    #             self.mount(self.dialog)

    # def action_move_up(self) -> None:
    #     """Move up the dialog."""
    #     self.t.move_up()
    #     self.render()

    # def action_move_down(self) -> None:
    #     """Move down the dialog."""
    #     self.t.move_down()
    #     self.render()

    # def action_move_left(self) -> None:
    #     """Move left the dialog."""
    #     self.t.move_left()
    #     self.render()

    # def action_move_right(self) -> None:
    #     """Move right the dialog."""
    #     self.t.move_right()
    #     self.render()

    # def action_insert_move(self) -> None:
    #     """Insert and move the dialog."""
    #     self.t.insert_move({"role": "user", "content": self.textarea.text})
    #     self.render()

if __name__ == "__main__":
    app = DialogApp()
    app.run()
