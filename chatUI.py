import curses

class ChatUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.pad = curses.newpad(1000, curses.COLS-4)
        curses.initscr()
        curses.start_color()
        curses.init_color(101, 0xf3*1000//0x100, 0x94*1000//0x100, 0x25*1000//0x100)
        curses.init_color(102, 0x2d*1000//0x100, 0xbc*1000//0x100, 0xec*1000//0x100)
        curses.init_pair(1, 101, 0)
        curses.init_pair(2, 102, 0)
        curses.init_pair(3, curses.COLOR_RED, 0)
        self.curr_line = 0

    def check_extension(self):
        if self.pad.getyx()[0] > self.pad.getmaxyx()[0] - 500:
            self.pad.resize(self.pad.getmaxyx[0] + 500, self.pad.getmaxyx[1])

    def refresh(self):
        curr_line = max(0, self.pad.getyx()[0] - (curses.LINES-1))
        self.pad.refresh(curr_line, 0, 0, 2, curses.LINES-1, curses.COLS-3)

    def update_pad(self, chat: list):
        assert chat[0]['role'] == 'system'
        self.pad.clear()
        for message in chat:
            self.check_extension()
            if message['role'] == 'system':
                self.pad.addstr("@System>\n", curses.color_pair(3) | curses.A_BOLD)
                content = message['content']
                if len(content) > 100:
                    content = content[0:99] + '...\n\n'
                self.pad.addstr(content, curses.color_pair(3))
            elif message['role'] == 'user':     
                self.pad.addstr("@User>\n", curses.color_pair(1) | curses.A_BOLD)
                self.pad.addstr(message['content']+'\n', curses.color_pair(1))
            elif message['role'] == 'assistant':
                self.pad.addstr("@Bot>\n", curses.color_pair(2) | curses.A_BOLD)
                self.pad.addstr(message['content']+'\n\n', curses.color_pair(2))
        self.refresh()

    def ask_user_input(self):
        self.pad.addstr("@User>\n", curses.color_pair(1) | curses.A_BOLD)
        prompt = ''
        self.refresh()
        while True:
            key = self.pad.getkey()
            self.pad.addch(key)
            self.refresh()
            if key == '\n':
                break
            prompt += key
        return prompt.strip('/n')

