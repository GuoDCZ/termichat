from textual.app import App, ComposeResult
from textual.events import MouseEvent
from textual.widgets import Markdown, TextArea, Static, Button
from textual.binding import Binding
from tree import Tree, Node
from threading import Thread
from queue import Queue
import time

shut_down = False

class MyTextArea(TextArea):

    def on_mount(self) -> None:
        self.add_class("hidden")

    BINDINGS = {
        Binding("ctrl+s", "submit", "Submit", priority=True),
        Binding("ctrl+d", "cancel", "Cancel", priority=True),
    }

    def action_submit(self) -> None:
        self.parent.add_block()
        self.parent.focus()

    def action_cancel(self) -> None:
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

    stream_queue: Queue = Queue()

    @staticmethod
    def streaming():
        updater = None
        while True:
            while True:
                if shut_down:
                    return
                try:
                    response, block = Block.stream_queue.get(timeout=0.1)
                    break
                except:
                    continue
            block: Block
            child_node = block.node.child
            child_node._parent_content = ""
            for chunk in response:
                if shut_down:
                    return
                chuck_msg = chunk['choices'][0]['delta']
                if 'content' in chuck_msg:
                    child_node._parent_content += chuck_msg['content']
                    if updater is None:
                        try:
                            updater = block.updater
                            updater.resume()
                        except AttributeError:
                            pass
            if updater is not None:
                time.sleep(2)
                updater.pause()
                updater = None

    ASTBLK_MSG: str = "*[Press `Ctrl+S` to regenerate the message]*"

    def __init__(self, node: Node):
        self.node = node
        node.block = self
        super().__init__()

    def compose(self) -> ComposeResult:
        if isinstance(self, AssistantBlock):
            yield MyTextArea(Block.ASTBLK_MSG, read_only=True)
        else:
            yield MyTextArea(tab_behavior="indent")
        yield Markdown("")

    def on_mount(self) -> None:
        if self.node.role == 'system':
            self.border_title = " System "
        elif self.node.role == 'assistant':
            self.border_title = " Bot "
        elif self.node.role == 'user':
            self.border_title = " User "
        self.markdown = self.query_one(Markdown)
        self.textarea = self.query_one(MyTextArea)
        self.reload()
        self.updater = self.set_interval(
            0.1, self.reload_content, pause=True
        )
        self.focus()
        self.scroll_visible()

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

    BINDINGS = {
        Binding("ctrl+s", "submit", "Submit"),
        Binding("space,enter,ctrl+d", "edit", "Edit"),
        Binding("up", "move_up", "Move up"),
        Binding("down", "move_down", "Move down"),
        Binding("left", "move_left", "Move left"),
        Binding("right", "move_right", "Move right"),
        Binding("pageup", "move_up_most", "Move up most"),
        Binding("pagedown", "move_down_most", "Move down most"),
        Binding("home", "move_left_most", "Move left most"),
        Binding("end", "move_right_most", "Move right most"),
        Binding("delete", "remove", "Remove"),
    }

    def action_edit(self) -> None:
        self.textarea.focus()

    def action_cancel(self) -> None:
        self.textarea.blur()

    def action_submit(self) -> None:
        self.add_block()

    def action_move_up(self) -> None:
        block = self
        if block.parent_block:
            block = block.parent_block
        block.focus()
        block.scroll_visible()

    def action_move_down(self) -> None:
        block = self
        if block.child_block:
            block = block.child_block
        block.focus()
        block.scroll_visible()

    def action_move_left(self) -> None:
        if self.node.index is not None:
            self.action_move_sibling(self.node.index - 1)

    def action_move_right(self) -> None:
        if self.node.index is not None:
            self.action_move_sibling(self.node.index + 1)

    def action_move_up_most(self) -> None:
        block = self
        while block.parent_block:
            block = block.parent_block
        block.focus()
        block.scroll_visible()

    def action_move_down_most(self) -> None:
        block = self
        while block.child_block:
            block = block.child_block
        block.focus()
        block.scroll_visible()

    def action_move_left_most(self) -> None:
        if self.node.index is not None:
            self.action_move_sibling(0)

    def action_move_right_most(self) -> None:
        if self.node.index is not None:
            self.action_move_sibling(len(self.node.children) - 1)

    def action_move_sibling(self, index: int) -> None:
        self.make_child_invisible()
        self.node.switch(index)
        self.reload()
        self.make_child_visible()

    def action_remove(self) -> None:
        if self.child_block is None:
            if self.parent_block is None:
                return
            self.node.parent.remove_child()
            self.remove()
        else:
            block = self.child_block
            while block:
                block.remove()
                block = block.child_block
            self.node.remove_child()
            if self.node.child is not None:
                self.make_child_visible()
            self.reload()

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

    def reload_content(self) -> None:
        if self.node.content != "":
            self.markdown.update(self.node.content)
        else:
            self.markdown.update("…")

    def reload(self) -> None:
        self.reload_content()
        if isinstance(self, AssistantBlock):
            self.textarea.text = Block.ASTBLK_MSG
        else:
            self.textarea.text = self.node.content
        n = len(self.node.children)
        i = self.node.index

        def repr(i: int) -> str:
            content = self.node.children[i]._parent_content
            splits = content.split()
            if len(splits) == 0:
                return str(i+1)
            splits = splits[0].split("|")
            if len(splits) == 2:
                return splits[0]
            else:
                return str(i+1)

        if n >= 2:
            total_length = len(repr(i))
            sub_title = f"[b]<{repr(i)}>[/b]"
            left = i - 1
            right = i + 1
            if left >= 0:
                total_length += len(repr(left)) + 2
            if right < n:
                total_length += len(repr(right)) + 2
            while total_length < self.size.width / 2:
                if left >= 0:
                    sub_title = f"[@click='move_sibling({left})']{repr(left)} [/]" + sub_title
                    left -= 1
                    if left >= 0:
                        total_length += len(repr(left)) + 2
                if right < n:
                    sub_title += f"[@click='move_sibling({right})'] {repr(right)}[/]"
                    right += 1
                    if right < n:
                        total_length += len(repr(right)) + 2
                if left < 0 and right >= n:
                    break
            if left >= 0:
                sub_title = f"[@click='move_sibling({left})']<- [/]" + sub_title
            if right < n:
                sub_title += f"[@click='move_sibling({right})'] ->[/]"
            self.border_subtitle = sub_title
            self.add_class("has-branch")
        else: 
            self.remove_class("has-branch")

    def add_block_with_node(self, node: Node) -> None:
        if node.role == 'system':
            block = SystemBlock(node)
        elif node.role == 'assistant':
            block = AssistantBlock(node)
        elif node.role == 'user':
            block = UserBlock(node)
        self.parent.mount(block)

    def add_block(self) -> None:
        self.make_child_invisible()
        content = self.textarea.text
        node = self.node.add(content)
        self.reload()
        self.add_block_with_node(node)


class SystemBlock(Block):
    pass


class AssistantBlock(Block):

    def add_block(self) -> None:
        self.make_child_invisible()
        content = self.node.parent.make_request()
        node = self.node.add("")
        self.add_block_with_node(node)
        self.reload()
        Block.stream_queue.put((content, self))


class UserBlock(Block):

    def add_block(self) -> None:
        super().add_block()
        request = self.node.make_request()
        node = self.node.child.add("")
        self.child_block.add_block_with_node(node)
        Block.stream_queue.put((request, self.child_block))


class Dialog(App):

    CSS_PATH = "style.tcss"

    BINDINGS = {
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+q", "quit", "Quit"),
    }

    def action_quit(self) -> None:
        self.exit()

    def on_mouse_scroll_up(self, _event) -> None:
        if isinstance(self.focused, Block):
            self.focused.action_move_up()

    def on_mouse_scroll_down(self, _event) -> None:
        if isinstance(self.focused, Block):
            self.focused.action_move_down()
    
    def compose(self) -> ComposeResult:
        tree = Tree.load_from_json()
        yield SystemBlock(tree.root)
        for child in tree.root.children:
            yield UserBlock(child).add_class("hidden")

    def on_mount(self) -> None:
        block = self.query_one(SystemBlock)
        block.make_child_visible()
        block.reload()
        block.action_move_down_most()


app = Dialog()

if __name__ == "__main__":
    stream_thread = Thread(target=Block.streaming)
    stream_thread.start()
    app.run()
    shut_down = True
    stream_thread.join()