import curses
from text import Textbox
from chatlog import ChatLog

class ChatUI:
    def __init__(self, log, stdscr):
        self.log: ChatLog = log
        self.stdscr: curses.window = stdscr
        self.pad = curses.newpad(1000, curses.COLS)
        curses.initscr()
        curses.start_color()
        curses.init_color(101, 0xf3*1000//0x100, 0x94*1000//0x100, 0x25*1000//0x100)
        curses.init_color(102, 0x2d*1000//0x100, 0xbc*1000//0x100, 0xec*1000//0x100)
        curses.init_color(103, 300, 300, 300)
        curses.init_pair(1, 101, 0)
        curses.init_pair(2, 102, 0)
        curses.init_pair(3, curses.COLOR_RED, 0)
        curses.init_pair(4, 101, 103)
        curses.init_pair(5, 102, 103)
        curses.init_pair(6, curses.COLOR_RED, 103)
        self.pminrow = 0

    def check_extension(self):
        if self.pad.getyx()[0] > self.pad.getmaxyx()[0] - 500:
            self.pad.resize(self.pad.getmaxyx[0] + 500, self.pad.getmaxyx[1])

    def ensure_show(self, row):
        if self.pminrow > row:
            self.pminrow = row
        elif self.pminrow < row - (curses.LINES - 1):
            self.pminrow = row - (curses.LINES - 1)
    
    def refresh(self):
        self.update_pad()
        self.pad.refresh(self.pminrow, 0, 0, 0, curses.LINES-1, curses.COLS)

    def put_message(self, message):
        if message['role'] == 'system':
            self.pad.addstr("@System:\n", curses.color_pair(3) | curses.A_BOLD)
            content = message['content']
            if len(content) > 100:
                content = content[0:99] + '...'
            self.pad.addstr(content, curses.color_pair(3))
        elif message['role'] == 'user':     
            self.pad.addstr("@User:\n", curses.color_pair(1) | curses.A_BOLD)
            self.pad.addstr(message['content'], curses.color_pair(1))
        elif message['role'] == 'assistant':
            self.pad.addstr(f"@{self.log.config['role']}:\n", curses.color_pair(2) | curses.A_BOLD)
            self.pad.addstr(message['content'], curses.color_pair(2))

    def update_pad(self):
        chat = self.log.get_chat()
        assert chat[0]['role'] == 'system'
        self.pad.clear()
        for message in chat:
            self.check_extension()
            self.put_message(message)
            self.pad.addch('\n')
        if chat[-1]['role'] == 'user':
            self.put_message({
                'role': 'assistant',
                'content': '...'
            })
            self.pad.addch('\n')
        self.ensure_show(self.pad.getyx()[0])

    def key_handler(self, key):
        if key == 410: # RESIZE
            curses.update_lines_cols()
            self.pad.resize(1000, curses.COLS)
            self.update_pad()
        elif key == 336: # SHIFT + DOWN
            self.pminrow += 1
            self.ensure_show(self.pad.getyx()[0])
        elif key == 337: # SHIFT + UP
            if self.pminrow > 0:
                self.pminrow -= 1
        else:
            return False
        return True

    def ask_user_input(self):
        self.put_message({
            'role': 'user',
            'content': ''
        })
        textbox = Textbox()
        cursor_yx = text_yx = self.pad.getyx()
        while True:
            self.pad.move(cursor_yx[0], cursor_yx[1])
            self.refresh()
            key = self.stdscr.getch()
            if key == 393: # SHIFT + LEFT
                break
            if self.key_handler(key):
                continue
            textbox.type(key)
            self.pad.move(text_yx[0], text_yx[1])
            self.pad.addstr(textbox.s[:textbox.i])
            cursor_yx = self.pad.getyx()
            self.pad.addstr(textbox.s[textbox.i:]+'\n\n')
        return textbox.s.strip('/n')
