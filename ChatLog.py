class ChatLog:
    def __init__(self):
        self.root = ChatItem()
        self.curr = self.root

    def add_item(self, chat):
        item = ChatItem()
        item.prev = self.curr
        item.chat = chat
        self.curr.nexts.append(item)
        self.curr.n = len(self.curr.nexts) - 1
        self.move_next()

    def get_chat(self):
        curr = self.curr
        chat = []
        while curr != self.root:
            chat = [curr.chat] + chat
            curr = curr.prev
        return chat
    
    def move_first(self):
        self.curr = self.root.get_next()

    def move_last(self):
        while self.curr.get_next():
            self.curr = self.curr.get_next()

    def move_prev(self):
        if self.curr.prev is not self.root:
            self.curr = self.curr.prev

    def move_next(self):
        if self.curr.get_next():
            self.curr = self.curr.get_next()

    def move_left(self):
        if self.curr.n is not None:
            if self.curr.n > 0:
                self.curr.n -= 1

    def move_right(self):
        if self.curr.n is not None:
            if self.curr.n < len(self.curr.nexts) - 1:
                self.curr.n += 1

class ChatItem:
    def __init__(self):
        self.chat: dict = {}
        self.prev: ChatItem = None
        self.nexts: list[ChatItem] = []
        self.n: int = None

    def get_next(self):
        return self.nexts[self.n] if self.n is not None else None
