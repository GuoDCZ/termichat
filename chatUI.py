import curses
from text import TextBox
from chatlog import ChatLog

class ChatUI:
    def __init__(self, stdscr, log):
        self.log: ChatLog = log
        self.stdscr: curses.window = stdscr
        self.pad = curses.newpad(1000, curses.COLS)
        curses.initscr()
        curses.start_color()
        curses.init_color(0xf0, 0xf3*1000//0x100, 0x94*1000//0x100, 0x25*1000//0x100)
        curses.init_pair(0xf0, 0xf0, 0)
        self.COLOR_USR = curses.color_pair(0xf0)
        curses.init_color(0xf1, 0x2d*1000//0x100, 0xbc*1000//0x100, 0xec*1000//0x100) # BLUE
        curses.init_pair(0xf1, 0xf1, 0)
        self.COLOR_BOT = curses.color_pair(0xf1)
        curses.init_pair(0xf2, curses.COLOR_RED, 0)
        self.COLOR_SYS = curses.color_pair(0xf2)
        curses.init_color(0xf3, 500, 500, 500) # GREY
        curses.init_pair(0xf3, 0xf3, 0)
        self.COLOR_INFO = curses.color_pair(0xf3)
        self.pminrow = 0

    def check_extension(self):
        if self.pad.getyx()[0] > self.pad.getmaxyx()[0] - 500:
            self.pad.resize(self.pad.getmaxyx()[0] + 500, self.pad.getmaxyx()[1])

    def ensure_show(self, row):
        if self.pminrow > row:
            self.pminrow = row
        elif self.pminrow < row - (curses.LINES - 1):
            self.pminrow = row - (curses.LINES - 1)

    def get_bar_string(self, n, i):
        s = ''
        for j in range(n):
            if j == i:
                s += '<' + str(i+1) + '>'
            else:
                s += '-'
        for j in range(len(str(i+1)), len(str(n+1))):
            s += '-'
        return s

    def refresh_log(self):
        self.pad.clear()
        curr = self.log.root.get_next()
        assert curr.chat['role'] == 'system'
        while curr:
            self.check_extension()
            content = curr.chat['content']
            if curr.chat['role'] == 'system':
                attr = self.COLOR_SYS
                name = 'System'
                if len(content) > 127:
                    content = content[:127]+'...'
            elif curr.chat['role'] == 'user':
                attr = self.COLOR_USR
                name = 'User'
            elif curr.chat['role'] == 'assistant':
                attr = self.COLOR_BOT
                name = self.log.config['role']

            if curr is self.log.curr.get_next():
                attr = curses.color_pair(0)

            
            self.pad.attron(attr)

            self.pad.attron(curses.A_BOLD)
            self.pad.addstr(f"@{name}: ")
            if curr is self.log.curr.get_next():
                self.pad.attron(self.COLOR_INFO)
                self.pad.addstr(f"{curr.total_tokens - curr.tokens}+")
                self.pad.addstr(f"{curr.tokens if curr.tokens else '?'} | ")
                self.pad.addstr(f"${self.log.get_consumption()} | ")
                self.pad.addstr(self.get_bar_string(len(curr.prev.nexts),curr.prev.n))
                self.pad.attroff(self.COLOR_INFO)
            self.pad.addch('\n')
            self.pad.attroff(curses.A_BOLD)

            self.pad.addstr(content)
            if content:
                self.pad.addch('\n')
            self.pad.attroff(attr)

            curr = curr.get_next()

        self.text_yx = self.pad.getyx()
        self.ensure_show(self.pad.getyx()[0])

    def refresh_pad(self):
        self.pad.refresh(self.pminrow, 0, 0, 0, curses.LINES-1, curses.COLS)

    def refresh_tb(self, tb):
        self.pad.move(self.text_yx[0], self.text_yx[1])
        self.pad.addstr(tb.s[:tb.i])
        cursor_yx = self.pad.getyx()
        self.pad.addstr(tb.s[tb.i:]+'\n\n')
        self.pad.move(cursor_yx[0], cursor_yx[1])
        self.ensure_show(cursor_yx[0])

    def scroll_down(self):
        if self.pminrow < self.pad.getyx()[0]:
            self.pminrow += 1
    
    def scroll_up(self):
        if self.pminrow > 0:
            self.pminrow -= 1

    def page_down(self):
        self.scroll_down()
        for i in range(curses.LINES):
            self.scroll_down()
    
    def page_up(self):
        for i in range(curses.LINES):
            self.scroll_up()
