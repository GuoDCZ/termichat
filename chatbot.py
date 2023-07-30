import openai
import curses

from ChatConfig import *
from LogPad import LogPad
from TextPad import TextPad

def initUI():
    curses.initscr()
    curses.start_color()
    curses.init_color(0xf0, 0xf3*1000//0x100, 0x94*1000//0x100, 0x25*1000//0x100)
    curses.init_pair(0xf0, 0xf0, 0)
    # self.COLOR_USR = curses.color_pair(0xf0)
    curses.init_color(0xf1, 0x2d*1000//0x100, 0xbc*1000//0x100, 0xec*1000//0x100) # BLUE
    curses.init_pair(0xf1, 0xf1, 0)
    # self.COLOR_BOT = curses.color_pair(0xf1)
    curses.init_pair(0xf2, curses.COLOR_RED, 0)
    # self.COLOR_SYS = curses.color_pair(0xf2)
    curses.init_color(0xf3, 500, 500, 500) # GREY
    curses.init_pair(0xf3, 0xf3, 0)
    # self.COLOR_INFO = curses.color_pair(0xf3)

class ChatBot:
    def __init__(self, config):
        self.config = config

    def run(self, stdscr: curses.window):
        ssize = stdscr.getmaxyx()
        self.textpad: TextPad = TextPad(ssize)
        self.logpad: LogPad = LogPad(ssize, self.config)
        self.logpad.update_pad()
        self.logpad.refresh(self.textpad.fnl)
        self.alt: bool = False
        while True:
            key = stdscr.get_wch()
            if not self.put_key(ord(key) if type(key) is str else key):
                break

    def cmpl_request(self, messages):
        return openai.ChatCompletion.create(
            model = "gpt-3.5-turbo", 
            messages = messages, 
            temperature = self.config['temperature'],
            presence_penalty = self.config['presence_penalty'], 
            frequency_penalty = self.config['frequency_penalty'],
            stream = True
        )
    
    def put_key(self, key):
        if not self.alt and key == 27: # ALT
            self.alt = True
        elif self.alt and key == 10: # ALT + ENTER
            if self.logpad.curr.chat['role'] != 'user':
                self.logpad.add_msg('user', self.textpad.s)
                self.textpad.clear()
                self.logpad.update_pad()
                self.textpad.refresh()
                self.logpad.refresh(self.textpad.fnl)
            messages = self.logpad.get_chat()
            cmpl = self.cmpl_request(messages)
            content = self.logpad.cmpl_stream_show(cmpl)
            self.logpad.add_msg('assistant', content)
            self.logpad.update_pad()
            self.logpad.refresh(self.textpad.fnl)
            self.alt = False
        elif self.alt and key == 27: # doubel ESC
            return False
        # elif key == 410: # RESIZE
        #     curses.update_lines_cols()
        #     self.pad.resize(1000, curses.COLS)
        #     self.update_pad()
        elif self.logpad.put_key(key):
            self.logpad.refresh()
            pass
        else:
            self.textpad.put_key(key)
            self.textpad.refresh()
            self.logpad.refresh(self.textpad.fnl)
        return True

def main():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not os.path.exists(CONFIG_FILE):
        save_config(init_config())
    else:
        initUI()
        config = load_config()
        print_config(config)
        bot = ChatBot(config)
        curses.wrapper(bot.run)

if __name__ == '__main__':
    main()
