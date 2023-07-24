import openai
import os
import typing

class ChatLog:
    def __init__(self, config):
        self.config = config
        self.input_tokens = 0
        self.output_tokens = 0
        fp = os.path.join(config['roleDir'], config['role'] + '.txt')
        sys_content = open(fp, 'r', encoding='utf-8').read()
        self.first = Message()
        self.first.chat = {'role': 'system', 'content': sys_content}
        self.curr = self.first

    def get_consumption(self):
        return round((self.input_tokens * 0.0015 + self.output_tokens * 0.002) / 1000, 3)

    def get_chat(self, msg):
        return [msg.chat] + self.get_chat(msg.get_next()) if msg else []

    def get_tokens(self, msg):
        return msg.tokens + self.get_tokens(msg.prev) if msg else 0

    def move_prev(self):
        if self.curr.prev:
            self.curr = self.curr.prev

    def move_next(self):
        if self.curr.get_next():
            self.curr = self.curr.get_next()

    def move_left(self):
        self.curr.switch_left()

    def move_right(self):
        self.curr.switch_right()

    def new_msg(self):
        self.curr.new_next()
        self.move_next()

    def add_prompt(self, prompt):
        self.new_msg()
        self.curr.chat = {'role': 'user', 'content': prompt}

    def request_cmpl(self):
        return openai.ChatCompletion.create(
            model = "gpt-3.5-turbo", 
            messages = self.get_chat(self.first), 
            temperature = self.config['temperature'],
            presence_penalty = self.config['presence_penalty'], 
            frequency_penalty = self.config['frequency_penalty']
        )

    def add_response(self):
        cmpl = self.request_cmpl()
        prev_tokens = self.get_tokens(self.curr.prev.prev)
        self.curr.prev.tokens = cmpl['usage']['prompt_tokens'] - prev_tokens
        self.new_msg()
        self.curr.chat = cmpl["choices"][0]["message"]
        self.curr.tokens = cmpl['usage']['completion_tokens']
        self.input_tokens += cmpl['usage']['prompt_tokens']
        self.output_tokens += cmpl['usage']['completion_tokens']

class Message:
    def __init__(self):
        self.chat: dict = {}
        self.tokens: int = 0
        self.prev: Message = None
        self.n: int = None
        self.nexts: typing.List[Message] = []

    def get_next(self):
        if self.n is None:
            return None
        return self.nexts[self.n]

    def new_next(self):
        self.nexts.append(Message())
        self.n = len(self.nexts) - 1
        self.get_next().prev = self
    
    def switch_left(self):
        if self.n is not None and self.n > 0:
            self.n -= 1
            return True
        return False
    
    def switch_right(self):
        if self.n is not None and self.n < len(self.nexts) - 1:
            self.n += 1
            return True
        return False
