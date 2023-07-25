import openai
import os
import typing

class ChatLog:
    def __init__(self, config):
        self.config = config
        self.input_tokens = 0
        self.output_tokens = 0
        self.root = ChatItem()
        self.curr = self.root
        self.add_sys_msg()

    def new_msg(self):
        item = ChatItem()
        item.prev = self.curr
        self.curr.nexts.append(item)
        self.curr.n = len(self.curr.nexts) - 1
        self.curr = item

    def add_sys_msg(self):
        self.new_msg()
        fp = os.path.join(self.config['roleDir'], self.config['role'] + '.txt')
        sys_content = open(fp, 'r', encoding='utf-8').read()
        self.curr.chat = {'role': 'system', 'content': sys_content}

    def add_usr_msg(self, prompt):
        self.new_msg()
        self.curr.chat = {'role': 'user', 'content': prompt}

    def add_bot_msg(self):
        cmpl = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo", 
            messages = self.get_chat(), 
            temperature = self.config['temperature'],
            presence_penalty = self.config['presence_penalty'], 
            frequency_penalty = self.config['frequency_penalty']
        )
        self.curr.total_tokens = cmpl['usage']['prompt_tokens']
        self.curr.tokens = self.curr.total_tokens - self.curr.prev.total_tokens
        self.new_msg()
        self.curr.chat = cmpl["choices"][0]["message"]
        self.curr.tokens = cmpl['usage']['completion_tokens']
        self.curr.total_tokens = cmpl['usage']['total_tokens']
        self.input_tokens += cmpl['usage']['prompt_tokens']
        self.output_tokens += cmpl['usage']['completion_tokens']

    def get_consumption(self):
        return round((self.input_tokens * 0.0015 + self.output_tokens * 0.002) / 1000, 3)
    
    def get_chat(self):
        curr = self.root.get_next()
        chat = []
        while curr:
            chat.append(curr.chat)
            curr = curr.get_next()
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
        if self.curr.n > 0:
            self.curr.n -= 1

    def move_right(self):
        if self.curr.n < len(self.curr.prev.nexts) - 1:
            self.curr.n += 1

class ChatItem:
    def __init__(self):
        self.chat: dict = {}
        self.tokens: int = 0
        self.total_tokens: int = 0
        self.prev: ChatItem = None
        self.nexts: typing.List[ChatItem] = []
        self.n: int = None

    def get_next(self):
        return self.nexts[self.n] if self.n is not None else None
