"""
Define the dialog app.

The dialog app is used to display chat messages in a hierarchical way. It uses
the tree structure to store chat messages and the dialog structure to display
them. The app also defines key bindings for moving up and down the dialog.
"""

from textual.app import App, ComposeResult
from textual.widgets import TextArea
from typing import Optional
from dialog import Dialog
from tree import Tree, Render

class DialogApp(App):

    BINDINGS = [
        ("up", "move_up", "Move up"),
        ("down", "move_down", "Move down"),
        ("left", "move_left", "Move left"),
        ("right", "move_right", "Move right"),
        ("ctrl+s", "insert_move", "Insert and move"),
        #("ctrl+delete", "remove", "Remove"),
        #("ctrl+enter", "insert_move", "Insert and move"),
    ]

    def __init__(self, path: str = "tree") -> None:
        """Initialize the dialog app."""
        self.dialog: Optional[Dialog] = None
        self.textarea: Optional[TextArea] = None
        self.t: Tree = Tree.load(path)
        self.t.insert_move({"role": "user", "text": "Hello!"})
        self.t.insert_move({"role": "bot", "text": "Hi there!"})
        self.t.insert_move({"role": "user", "text": "How are you?"})
        self.t.insert_move({"role": "bot", "text": "Goodbye!"})
        self.t.move_up()
        self.t.move_up()
        self.t.insert_move({"role": "user", "text": "Bye!"})
        self.t.insert_move(
            {
                "role": "bot",
                "text": """
        I'm doing great! How can I help you today?
                    
            ```python
                print("Hello, World!")
            ```
        """,
            }
        )
        self.t.move_up()
        self.t.move_up()
        self.t.renders = []
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the dialog app."""
        self.dialog = Dialog(self.t)
        yield self.dialog
        self.textarea = TextArea()
        yield self.textarea

    def render(self) -> None:
        """Render the dialog app."""
        while self.t.renders:
            render = self.t.renders.pop(0)
            if render == Render.PUSH:
                self.dialog.push()
            elif render == Render.POP:
                self.dialog.pop()
            elif render == Render.REPEAT:
                self.dialog.push()
                self.dialog.pop()
            elif render == Render.RELOAD:
                self.dialog = Dialog(self.t)
                self.mount(self.dialog)

    def action_move_up(self) -> None:
        """Move up the dialog."""
        self.t.move_up()
        self.render()

    def action_move_down(self) -> None:
        """Move down the dialog."""
        self.t.move_down()
        self.render()

    def action_move_left(self) -> None:
        """Move left the dialog."""
        self.t.move_left()
        self.render()

    def action_move_right(self) -> None:
        """Move right the dialog."""
        self.t.move_right()
        self.render()

    def action_insert_move(self) -> None:
        """Insert and move the dialog."""
        self.t.insert_move({"role": "user", "text": self.textarea.text})
        self.render()


if __name__ == "__main__":
    app = DialogApp()
    app.run()
