import curses

class ChatUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.pad = curses.newpad(1000, curses.COLS)
        curses.initscr()
        curses.start_color()
        curses.init_color(1, 0xf3*1000//0x100, 0x94*1000//0x100, 0x25*1000//0x100)
        curses.init_color(2, 0x2d*1000//0x100, 0xbc*1000//0x100, 0xec*1000//0x100)
        curses.init_color(3, 300, 300, 300)
        curses.init_pair(1, 1, 0)
        curses.init_pair(2, 2, 0)
        curses.init_pair(3, 1, 3)
        curses.init_pair(4, 2, 3)
        self.curr_line = 0

    def refresh(self):
        curr_line = max(0, self.pad.getyx()[0] - (curses.LINES-1))
        self.pad.refresh(curr_line, 0, 0, 0, curses.LINES-1, curses.COLS)

    def show(self, chat: list):
        assert chat[0]['role'] == 'system'
        self.pad = curses.newpad(1000, curses.COLS)
        for i in range(len(chat)//2):
            self.pad.addstr("@User>\n", curses.color_pair(1) | curses.A_BOLD)
            self.pad.addstr(chat[i*2+1]['content']+'\n', curses.color_pair(1))
            if (i*2+2 == len(chat)):
                break
            self.pad.addstr("@Bot>\n", curses.color_pair(2) | curses.A_BOLD)
            self.pad.addstr(chat[i*2+2]['content']+'\n', curses.color_pair(2))
            if self.pad.getyx()[0] > self.pad.getmaxyx()[0] - 500:
                self.pad.resize(self.pad.getmaxyx[0] + 500, self.pad.getmaxyx[1])
        self.refresh()

    def ask_user_input(self):
        self.pad.bkgdset(' ', curses.color_pair(3))
        self.pad.addstr("@User>\n", curses.color_pair(3) | curses.A_BOLD)
        prompt = ''
        self.refresh()
        while True:
            key = self.pad.getkey()
            self.pad.addch(key, curses.color_pair(3))
            self.refresh()
            if key == '\n' and keyboard.is_pressed('shift'):
                break
            prompt += key
        self.pad.bkgdset(' ', curses.color_pair(0))
        return prompt.strip('/n')

