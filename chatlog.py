import openai
import os
import typing

class ChatLog:
    def __init__(self, config):
        self.config: dict = config
        fp = os.path.join(config['roleDir'], config['role'] + '.txt')
        system_content = open(fp, 'r', encoding='utf-8').read()
        self.first: Message = Message(
            prev=None,
            chat={
                'role': 'system',
                'content': system_content
            }
        )
        self.curr: Message = self.first
        
    def get_chat(self):
        return self.first.get_chat()

    def move_prev(self):
        if self.curr.prev:
            self.curr = self.curr.prev

    def move_next(self):
        if self.curr.next:
            self.curr = self.curr.next

    def add_prompt(self, prompt):
        self.curr.set_next(
            Message(
                prev=self.curr,
                chat={
                    'role': 'user',
                    'content': prompt
                }
            )
        )
        self.move_next()

    def create_response(self):
        cmpl = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo", 
            messages = self.get_chat(), 
            temperature = self.config['temperature'],
            presence_penalty = self.config['presence_penalty'], 
            frequency_penalty = self.config['frequency_penalty']
        )
        prev_tokens = self.curr.prev.get_tokens()
        self.curr.tokens = cmpl['usage']['prompt_tokens'] - prev_tokens
        self.curr.set_next(
            Message(
                prev=self.curr,
                chat=cmpl["choices"][0]["message"],
                tokens=cmpl['usage']['completion_tokens']
            )
        )
        self.move_next()

class Message:
    def __init__(self, 
                 chat = None, 
                 tokens = 0, 
                 prev = None):
        self.chat: dict = chat
        self.tokens: int = tokens
        self.prev: Message = prev
        self.nexts: typing.List[Message] = []
        self.next: Message = None

    def get_chat(self):
        if self.next is None:
            return [self.chat]
        else:
            return [self.chat] + self.next.get_chat()

    def get_tokens(self):
        if self.prev is None:
            return self.tokens
        else:
            return self.tokens + self.prev.get_tokens()

    def set_next(self, msg):
        self.nexts.append(msg)
        self.next = msg
    
    def move_left(self):
        index = self.nexts.index(self.next)
        index = max(0, index-1)
        self.next = self.nexts[index]

    def move_right(self):
        index = self.nexts.index(self.next)
        index = min(len(self.nexts)-1, index-1)
        self.next = self.nexts[index]
