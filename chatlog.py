import openai
import os

class ChatLog:
    def __init__(self, config):
        self.config = config
        fp = os.path.join(config['roleDir'], config['role'] + '.txt')
        system_content = open(fp, 'r', encoding='utf-8').read()
        self.curr = self.first = Message(None)
        self.first.chat = {
            'role': 'system',
            'content': system_content
        }
        
    def get_chat(self):
        return self.first.get_chat()

    def move_left(self):
        assert self.curr.left
        self.curr = self.curr.left

    def move_right(self):
        assert self.curr.right
        self.curr = self.curr.right

    def move_prev(self):
        assert self.curr.prev
        self.curr = self.curr.prev

    def move_next(self):
        assert self.curr.next
        self.curr = self.curr.next

    def make_next(self):
        assert self.curr.chat
        assert self.curr.next is None
        msg = Message(self.curr)
        self.curr.next = msg
        self.move_next()

    def make_right(self):
        assert self.curr.chat
        msg = Message(self.curr.prev)
        msg.left = self.curr
        msg.right = self.curr.right
        if self.curr.right:
            self.curr.right.left = msg
        self.curr.right = msg
        self.curr.prev.next = msg
        self.move_right()

    def make(self):
        
        

    def add_prompt(self, prompt):
        self.incre_curr()
        self.curr.chat = {
            'role': 'user',
            'content': prompt
        }

    def create_response(self):
        cmpl = openai.ChatCompletion.create (
            model = "gpt-3.5-turbo", 
            messages = self.get_chat(), 
            temperature = self.config['temperature'],
            presence_penalty = self.config['presence_penalty'], 
            frequency_penalty = self.config['frequency_penalty']
        )
        prev_tokens = self.curr.prev.get_tokens_bottom_up()
        self.curr.tokens = cmpl['usage']['prompt_tokens'] - prev_tokens
        self.incre_curr()
        self.curr.chat = cmpl["choices"][0]["message"]
        self.curr.tokens = cmpl['usage']['completion_tokens']

class Message:
    def __init__(self, last):
        self.chat: dict = None
        self.tokens: int = None
        self.prev: Message = last
        self.next: Message = None
        self.left: Message = None
        self.right: Message = None

    def get_tokens(self):
        if self.prev is None:
            return self.tokens
        else:
            return self.tokens + self.prev.get_tokens()

    def get_chat(self):
        if self.get_next() is None:
            return self.chat
        else:
            return self.chat + self.next.get_chat()

    
