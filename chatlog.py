import openai
import os

class ChatLog:
    def __init__(self, config):
        self.role = config['role']
        self.memorable = config['memorable']
        self.temperature = config['temperature']
        self.presence_penalty = config['presence_penalty']
        self.frequency_penalty = config['frequency_penalty']
        roleInfoFilePath = os.path.join(config['roleDir'], config['role'] + '.txt')
        self.sys_msg = open(roleInfoFilePath, 'r', encoding='utf-8').read()
        self.first: Message = None
        self.curr: Message = None
        pass

    def incre_curr(self):
        if self.curr.get_next() is None:
            return False
        self.curr = self.curr.get_next()
        return True

    def load_chat(self, chat):
        assert chat[0]['role'] == 'system'
        self.sys_msg = chat[0]['content']
        self.curr = self.first = Message()
        for i in range(len(chat)//2):
            self.curr.load_chat(chat[i*2+1:i*2+2])
            self.curr.add_next(Message(self.curr))
            self.curr = self.curr.get_next()

    def get_chat(self):
        curr_backup = self.curr
        self.curr = self.first
        chat = [
            {
                'role': 'system',
                'content': self.sys_msg
            }
        ]
        while True:
            chat += self.curr.get_chat()
            if self.incre_curr() is False:
                break
        self.curr = curr_backup
        return chat

    def set_prompt(self, prompt):
        msg = Message(self.curr)
        msg.prompt = prompt
        if self.curr is None:
            self.first = msg
        else:
            self.curr.add_next(msg)
        self.curr = msg

    def switch_branch(self, n):
        self.curr = self.curr.last
        self.curr.n = n
        self.curr = self.curr.get_next()

    def create_response(self):
        completion = openai.ChatCompletion.create (
            model = "gpt-3.5-turbo", 
            messages = self.get_chat(), 
            temperature = self.temperature,
            presence_penalty = self.presence_penalty, 
            frequency_penalty = self.frequency_penalty
        )
        response = completion["choices"][0]["message"]['content']
        self.curr.set_response(response)
        return response

class Message:
    def __init__(self, last = None):
        self.prompt = None
        self.response = None
        self.n = None
        self.last = last
        self.nexts = []

    def load_chat(self, chat):
        assert chat[0]['role'] == 'user'
        self.prompt = chat[0]['content']
        assert chat[1]['role'] == 'assistant'
        self.response = chat[1]['content']

    def add_next(self, next):
        self.nexts.append(next)
        self.set_next(len(self.nexts)-1)

    def set_next(self, n):
        assert n < len(self.nexts) and n >= 0
        self.n = n

    def get_next(self):
        if self.n is None:
            return None
        return self.nexts[self.n]

    def set_prompt(self, prompt):
        self.prompt = prompt

    def set_response(self, response):
        self.response = response

    def get_chat(self):
        chat = []
        chat.append(
            {
                'role': 'user',
                'content': self.prompt
            }
        )
        if self.response:
            chat.append(
                {
                    'role': 'assistant',
                    'content': self.response
                }
            )
        return chat

    
