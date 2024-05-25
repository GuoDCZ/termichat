from textual import on
from textual.timer import Timer
from textual.message_pump import MessagePump
from textual.app import App, ComposeResult
from textual.widgets import Markdown, TextArea, Static
from textual.binding import Binding
from textual.containers import ScrollableContainer
from tree import Tree, Node
from threading import Thread
from typing import Any

class MyTextArea(TextArea):

    def on_mount(self) -> None:
        self.add_class("hidden")

    BINDINGS = {
        Binding("ctrl+s", "submit", "Submit", priority=True),
    }

    def action_submit(self) -> None:
        self.parent.add_block()
        self.parent.focus()

    def _on_blur(self, event) -> None:
        self.parent.query_one(Markdown).remove_class("hidden")
        self.add_class("hidden")
        return super()._on_blur(event)
    
    def _on_focus(self, event) -> None:
        self.parent.query_one(Markdown).add_class("hidden")
        self.remove_class("hidden")
        return super()._on_focus(event)


class Block(Static, can_focus=True):

    node: Node
    updater: Any

    def __init__(self, node: Node):
        self.node = node
        node.block = self
        super().__init__()

    @property
    def parent_block(self) -> "Block":
        parent_node = self.node.parent
        if parent_node is None:
            return None
        return parent_node.block
    
    @property
    def child_block(self) -> "Block":
        child_node = self.node.child
        if child_node is None:
            return None
        return child_node.block

    def compose(self) -> ComposeResult:
        yield MyTextArea()
        yield Markdown()
    
    def on_mount(self) -> None:
        if self.node.role is not None:
            self.border_title = self.node.role

    BINDINGS = {
        Binding("space", "edit", "Edit"),
        Binding("enter", "edit", "Edit"),
        Binding("up", "move_up", "Move up"),
        Binding("down", "move_down", "Move down"),
        Binding("left", "move_left", "Move left"),
        Binding("right", "move_right", "Move right"),
        Binding("delete", "remove", "Remove"),
    }

    def action_edit(self) -> None:
        self.query_one(MyTextArea).focus()

    def action_move_up(self) -> None:
        if self.parent_block:
            self.parent_block.focus()

    def action_move_down(self) -> None:
        if self.child_block:
            self.child_block.focus()

    def action_move_left(self) -> None:
        if self.node.index is not None:
            self.move_sibling(self.node.index - 1)

    def action_move_right(self) -> None:
        if self.node.index is not None:
            self.move_sibling(self.node.index + 1)

    def move_sibling(self, index: int) -> None:
        self.make_child_invisible()
        self.node.switch(index)
        self.reload()
        self.make_child_visible()

    def make_child_visible(self) -> None:
        block = self.child_block
        if block is not None:
            block.remove_class("hidden")
            block.make_child_visible()

    def make_child_invisible(self) -> None:
        block = self.child_block
        if block is not None:
            block.add_class("hidden")
            block.make_child_invisible()

    def reload(self) -> None:
        self.query_one(Markdown).update(self.node.content)
        self.query_one(MyTextArea).text = self.node.content

        def subtitle(n: int, i: int) -> str:
            if n == 0:
                return ""
            return " *"*i + f"[{i}]" + "* "*(n-i-1)
        
        if self.node.role is not None:
            self.border_subtitle = subtitle(len(self.node.children), self.node.index)

    def reload_content(self) -> None:
        self.query_one(Markdown).update(self.node.content)

    def stop_timer(self) -> None:
        self.updater.stop()
        self.reload_content()

    def add_block_with_node(self, node: Node) -> None:
        try:
            self.reload()
        except:
            pass
        if node.role == 'system':
            block = SystemBlock(node)
        elif node.role == 'assistant':
            block = AssistantBlock(node)
        elif node.role == 'user':
            block = UserBlock(node)
        else:
            raise ValueError(f"Invalid role: {node.role}")
        return block
    
    def mount_block(self, block: "Block") -> None:
        self.parent.mount(block)

    def add_block(self) -> None:
        self.make_child_invisible()
        content = self.query_one(MyTextArea).text
        node = self.node.add(content)
        block = self.add_block_with_node(node)
        self.mount_block(block)


class SystemBlock(Block):
    pass

class AssistantBlock(Block):

    def reload(self) -> None:
        self.query_one(Markdown).update(self.node.content)
        self.query_one(MyTextArea).text = "*[Press `Ctrl+S` to regenerate the message]*"

        def subtitle(n: int, i: int) -> str:
            if n == 0:
                return ""
            return " *"*i + f"[{i}]" + "* "*(n-i-1)
        
        if self.node.role is not None:
            self.border_subtitle = subtitle(len(self.node.children), self.node.index)
    
    def compose(self) -> ComposeResult:
        yield MyTextArea("*[Press `Ctrl+S` to regenerate the message]*", read_only=True)
        yield Markdown()

    def add_block(self) -> None:
        self.make_child_invisible()
        content = self.node.parent.make_request()
        node = self.node.add(content)
        self.add_block_with_node(node)

    # def subscribe(self) -> None:
    #     """
    #     Subscribe to the update_event and finish_event of the node.
        
    #     when the update_event is called, update block with the new content.
    #     when the finish_event is called, stop the subscription.
    #     """
    #     def func():
    #         while self.node.finish_event.is_set() is False:
    #             self.node.update_event.wait()
    #             self.node.update_event.clear()
    #             self.reload()

    #     thread = Thread(target=func)
    #     thread.start()

class UserBlock(Block):

    def add_block(self) -> None:
        super().add_block()
        request = self.node.make_request()
        node = self.node.child.add("111")
        block = self.child_block.add_block_with_node(node)
        self.mount_block(block)
        if 'updater' not in self.child_block.__dict__:
            self.child_block.updater = self.set_interval(0.5, self.reload_content, pause=True)
        stream_thread = Thread(target=node.stream_update, args=(request,self.child_block.stop_timer))
        stream_thread.start()
        self.child_block.updater.resume()
        stream_thread.join()
        self.child_block.reload_content()
        # self.reload_content()
        # self.child_block.subscribe()

class Dialog(App):

    CSS_PATH = "style.tcss"
    
    def compose(self) -> ComposeResult:
        tree = Tree()
        yield SystemBlock(tree.root)


app = Dialog()

if __name__ == "__main__":
    app.run()