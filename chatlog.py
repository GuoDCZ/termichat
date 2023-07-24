import openai
import os
import typing

class ChatLog:
    def __init__(self, config):
        self.config = config
        fp = os.path.join(config['roleDir'], config['role'] + '.txt')
        sys_content = open(fp, 'r', encoding='utf-8').read()
        self.first = Message()
        self.first.chat = {'role': 'system', 'content': sys_content}
        self.curr = self.first 
        self.new_msg_usr()
    
    def get_chat(self, msg):
        return [msg.chat] + self.get_chat(msg.next) if msg else []

    def get_tokens(self, msg):
        return msg.tokens + self.get_tokens(msg.prev) if msg else 0
        
    def move_prev(self):
        if self.curr.prev:
            self.curr = self.curr.prev

    def move_next(self):
        if self.curr.next:
            self.curr = self.curr.next

    def move_left(self):
        self.move_prev()
        self.curr.switch_left()
        self.move_next()

    def move_right(self):
        self.move_prev()
        self.curr.switch_left()
        self.move_next()

    def new_msg_bot(self):
        self.curr.new_next()
        self.move_next()
        self.curr.chat = {'role':'assistant','content':'...'}

    def new_msg_usr(self):
        self.curr.new_next()
        self.move_next()
        self.curr.chat = {'role':'user','content':''}

    def add_prompt(self, prompt):
        self.curr.chat['content'] = prompt
        self.new_msg_bot()

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
        self.curr.chat = cmpl["choices"][0]["message"]
        self.curr.tokens = cmpl['usage']['completion_tokens']
        self.new_msg_usr()

class Message:
    def __init__(self):
        self.chat: dict = {}
        self.tokens: int = 0
        self.prev: Message = None
        self.next: Message = None
        self.nexts: typing.List[Message] = []

    def new_next(self):
        self.next = Message()
        self.next.prev = self
        self.nexts.append(self.next)
    
    def switch_left(self):
        index = self.nexts.index(self.next) - 1
        if index > 0:
            self.next = self.nexts[index]
            return True
        return False
    
    def switch_right(self):
        index = self.nexts.index(self.next) + 1
        if index < len(self.nexts):
            self.next = self.nexts[index]
            return True
        return False
