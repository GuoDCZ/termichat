import curses
import os
from ChatLog import ChatLog

def get_bar_string(n, i):
    s = ''
    if n > 0:
        for j in range(n):
            if j == i:
                s += '<' + str(i+1) + '>'
            else:
                s += '-'
        for j in range(len(str(i+1)), len(str(n+1))):
            s += '-'
    return s

class LogPad(ChatLog):
    def __init__(self, ssize, config):
        ChatLog.__init__(self)
        filepath = os.path.join(config['roleDir'], config['role'] + '.txt')
        sys_content = open(filepath, 'r', encoding='utf-8').read()
        self.add_item({'role':'system','content':sys_content})
        self.config = config
        self.ssize = ssize
        self.psize = (1000, ssize[1])
        self.pad: curses.window = curses.newpad(*self.psize)
        self.lmaxy = 0
        self.fminy = 0
        self._init_style()

    def _init_style(self):
        self.style = {
            'user': {
                'attr': curses.color_pair(0xf0),
                'name': 'User'
            },
            'assistant': {
                'attr': curses.color_pair(0xf1),
                'name': self.config['role']
            },
            'system': {
                'attr': curses.color_pair(0xf2),
                'name': 'System'
            }
        }
    
    def _check_extension(self):
        if self.psize[0] < self.lmaxy+500 or self.psize[0] > self.lmaxy+1000:
            self.pad.resize(self.lmaxy+1000, self.psize[1])
        self.psize = self.pad.getmaxyx()

    def _update_fminy(self):
        curr_y = self.curr_ly if self.godown else self.curr_uy
        if curr_y < self.fminy:
            self.fminy = curr_y
        elif curr_y - self.fnl > self.fminy:
            self.fminy = curr_y - self.fnl

    def update_nlines(self, ssize):
        self.ssize = ssize
        self._update_fminy()
        self.refresh()

    def update_pad(self):
        self.pad.clear()
        curr = self.root.get_next()
        assert curr.chat['role'] == 'system'
        while curr:
            content = curr.chat['content']
            role = curr.chat['role']
            name = self.style[role]['name']
            attr = self.style[role]['attr']
            if role == 'system':
                if len(content) > 127:
                    content = content[:127]+'...'
            if curr is self.curr.get_next():
                attr = curses.color_pair(0)
                self.curr_uy = self.pad.getyx()[0]

            self.pad.addstr(f"@{name}: ", attr | curses.A_BOLD)

            if curr is self.curr.get_next():
                self.pad.addstr(get_bar_string(len(curr.prev.nexts),
                                               curr.prev.n),
                                curses.color_pair(0xf3))
            
            self.pad.addch('\n')
            self.pad.addstr(content, attr)

            if curr is self.curr.get_next():
                self.curr_ly = self.pad.getyx()[0]

            if content:
                self.pad.addch('\n')

            curr = curr.get_next()

        if self.curr.get_next() is None:
            self.curr_ly = self.curr_uy = self.pad.getyx()[0]

        self.lymax = self.pad.getmaxyx()[0]

        self._check_extension()

    def cmpl_stream_show(self, cmpl):
        attr = curses.color_pair(0xf1)
        name = self.config['role']
        collected_msg = []
        self.pad.addstr(f"@{name}: ", attr | curses.A_BOLD)
        self.pad.addch('\n')
        for chunk in cmpl:
            chuck_msg = chunk['choices'][0]['delta']
            collected_msg.append(chuck_msg)
            if 'content' in chuck_msg:
                self.pad.addstr(chuck_msg['content'], attr)
                self.refresh()
        return ''.join([m.get('content','') for m in collected_msg])
        
    def refresh(self, textfnl = None):
        if textfnl is not None:
            self.fnl = self.ssize[0] - textfnl - 2
        smin = (0, 0)
        smax = (self.fnl-1, self.ssize[1]-1)
        self._update_fminy()
        self.pad.refresh(self.fminy, 0, *smin, *smax)

    def scroll_down(self):
        if self.fminy < self.pad.getyx()[0]:
            self.fminy += 1

    def scroll_up(self):
        if self.fminy > 0:
            self.fminy -= 1

    def page_down(self):
        self.scroll_down()
        for i in range(curses.LINES):
            self.scroll_down()
    
    def page_up(self):
        for i in range(curses.LINES):
            self.scroll_up()

    def add_msg(self, role, content):
        self.add_item(
            {
                'role': role,
                'content': content
            }
        )

    def put_key(self, key):
        if key in [336, 337, 393, 402]:
            if key == 336: # SHIFT + DOWN
                self.move_next()
            elif key == 337: # SHIFT + UP
                self.move_prev()
            elif key == 393: # SHIFT + LEFT
                self.move_left()
            else: # SHIFT + RIGHT
                self.move_right()
            self.update_pad()
        elif key == 525: # ALT + SHIFT + DOWN
            self.scroll_down()
        elif key == 545: # ALT + SHIFT + LEFT
            self.page_up()
        elif key == 560: # ALT + SHIFT + RIGHT
            self.page_down()
        elif key == 566: # ALT + SHIFT + UP
            self.scroll_up()
        else:
            return False
        return True