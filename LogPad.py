import curses
import json
from ChatLog import ChatLog

def get_bar_string(n, i):
    s = ''
    if n > 1:
        for j in range(n):
            if j == i:
                s += '<' + str(i+1) + '>'
            else:
                s += '-'
        for j in range(len(str(i+1)), len(str(n+1))):
            s += '-'
    return s

class LogPad(ChatLog):
    def __init__(self, ncols):
        ChatLog.__init__(self)
        self.psize = (1000, ncols)
        self.pad: curses.window = curses.newpad(*self.psize)
        self.godown = True
        self.yu = self.yl = 0
        self.ymax = 0

    def load_config(self, config):
        self.config = config
        self._init_style()
        # filepath = os.path.join(config['roleDir'], config['role'] + '.txt')
        # sys_content = open(filepath, 'r', encoding='utf-8').read()
        # self.add_item({'role':'system','content':sys_content})
        filepath = "prompts-zh.json"
        prompts = json.load(open(filepath))
        for p in prompts:
            self.add_item({'role':'system','content':p['content']})
            self.move_prev()
        self.add_item({'role':'system','content':''})


    def _init_style(self):
        self.name = {
            'user': 'User',
            'assistant': self.config['role'],
            'system': 'System'
        }
        self.attr = {
            'user': curses.color_pair(0xf0),
            'assistant': curses.color_pair(0xf1),
            'system': curses.color_pair(0xf2)
        }
    
    def _check_size(self):
        if self.psize[0] < self.ymax+500 or self.psize[0] > self.ymax+1000:
            self.pad.resize(self.ymax+500, self.psize[1])
            self.psize = self.pad.getmaxyx()

    def _resize(self, ncols):
        nlines = self.psize[0] * self.psize[1] // ncols + 1
        while nlines % 500 != 0:
            nlines += 1
        self.pad.resize(nlines, ncols)
        self.psize = self.pad.getmaxyx()

    def _print_name_hl(self, chat, pair = (1,1)):
        self.yu = self.pad.getyx()[0]
        role = chat['role']
        name = self.name[role]
        self.pad.addstr(f"@{name}: ", curses.color_pair(0) | curses.A_BOLD)
        self.pad.addstr(get_bar_string(*pair) + '\n', curses.color_pair(0xf3))

    def _print_name(self, chat):
        role = chat['role']
        attr = self.attr[role]
        name = self.name[role]
        self.pad.addstr(f'@{name}: ' + '\n', attr | curses.A_BOLD)

    def _print_content_hl(self, chat):
        content = chat['content']
        self.pad.addstr(content, curses.color_pair(0))
        self.yl = self.pad.getyx()[0]
        if content:
            self.pad.addch('\n')

    def _print_content(self, chat):
        role = chat['role']
        attr = self.attr[role]
        content = chat['content']
        if role == 'system':
            if len(content) > 127:
                content = content[:127]+'...'
        self.pad.addstr(content, attr)
        if content:
            self.pad.addch('\n')

    def _update_pad(self, up_to_curr = False):
        self.pad.clear()
        curr = self.root.get_next()
        assert curr.chat['role'] == 'system'
        while curr:
            chat = curr.chat
            if curr is self.curr.get_next():
                self._print_name_hl(chat,(len(curr.prev.nexts),curr.prev.n))
                self._print_content_hl(chat)
            else:
                self._print_name(chat)
                self._print_content(chat)
            if up_to_curr and curr is self.curr:
                break
            curr = curr.get_next()
        if self.curr.get_next() is None:
            self.yl = self.yu = self.pad.getyx()[0]
            if self.curr.chat['role'] != 'user':
                self._print_name_hl({'role':'user'})
                self._print_content_hl({'content':'...'})
        self.ymax = self.pad.getyx()[0]
        self._check_size()

    def _add_msg(self, role, content):
        self.add_item({'role': role,'content': content})
        self._update_pad()
        self.godown = True

    def add_bot_msg(self, content):
        self._add_msg('assistant', content)

    def add_usr_msg(self, content):
        self._add_msg('user', content)

    def put_key(self, key):
        if key == 336: # SHIFT + DOWN
            self.move_next()
            self.godown = True
        elif key == 337: # SHIFT + UP
            self.move_prev()
            self.godown = False
        elif key == 393: # SHIFT + LEFT
            self.move_left()
            self.godown = False
        elif key == 402: # SHIFT + RIGHT
            self.move_right()
            self.godown = False
        else:
            return False
        self._update_pad()
        return True
    