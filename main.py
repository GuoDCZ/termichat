import openai
import curses

from ChatConfig import *
from TextUI import *
from LogUI import *

def initUI():
    curses.initscr()
    curses.start_color()
    curses.init_color(0xf0, 0xf3*1000//0x100//2+500, 0x94*1000//0x100//2+500, 0x25*1000//0x100//2+500)
    curses.init_pair(0xf0, 0xf0, 0)
    # self.COLOR_USR = curses.color_pair(0xf0)
    curses.init_color(0xf1, 0x2d*1000//0x100//2+500, 0xbc*1000//0x100//2+500, 0xec*1000//0x100//2+500) # BLUE
    curses.init_pair(0xf1, 0xf1, 0)
    # self.COLOR_BOT = curses.color_pair(0xf1)
    curses.init_color(0xf2, 0x25*1000//0x100//2+500, 0xf3*1000//0x100//2+500, 0x94*1000//0x100//2+500)
    curses.init_pair(0xf2, 0xf2, 0)
    # self.COLOR_SYS = curses.color_pair(0xf2)
    curses.init_color(0xf3, 500, 500, 500) # GREY
    curses.init_pair(0xf3, 0xf3, 0)
    # self.COLOR_INFO = curses.color_pair(0xf3)

class ChatBot:
    def __init__(self, config):
        self.config = config

    def run(self, stdscr: curses.window):
        ssize = stdscr.getmaxyx()
        self.stdscr = stdscr
        self.text: TextUI = TextUI(ssize)
        self.log: LogUI = LogUI(ssize)
        self.log.load_config(self.config)
        self.text.refresh()
        self.log.update_yshow(self.text.yshow)
        self.log._update_pad()
        self.log.refresh()
        self.alt: bool = False
        while True:
            key = stdscr.get_wch()
            if not self.put_key(ord(key) if type(key) is str else key):
                break

    def cmpl_request(self, messages):
        return openai.ChatCompletion.create(
            #model = "gpt-3.5-turbo", 
            model = "gpt-3.5-turbo-0301",
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
            if not 'role' in self.log.curr.chat:
                self.log._add_msg('system', self.text.s)
                self.text.clear()
            else:
                if self.log.curr.chat['role'] != 'user':
                    self.log.add_usr_msg(self.text.s)
                    self.text.clear()
                    self.log.update_yshow(self.text.yshow)
                    self.log.refresh()
                    self.text.refresh()
                messages = self.log.get_chat()
                cmpl = self.cmpl_request(messages)
                content = self.log.stream_show_cmpl(cmpl)
                self.log.add_bot_msg(content)
            self.log.update_yshow(self.text.yshow)
            self.alt = False
        elif self.alt and key == 27: # doubel ESC
            pass
            # return False
        elif key == 410: # RESIZE
            ssize = self.stdscr.getmaxyx()
            self.text.resize(ssize)
            self.log.update_yshow(self.text.yshow)
            self.log.resize(ssize)
        elif self.log.put_key(key):
            if not self.text.saved:
                self.text.save()
            item = self.log.curr.get_next()
            if item:
                if item.chat['role'] != 'assistant':
                    self.text.set(item.chat['content'])
                else:
                    self.text.set("Press Alt + Enter to regenerate")
            else:
                self.text.load()
        else:
            self.text.put_key(key)
            self.log.update_yshow(self.text.yshow)
        self.log.refresh()
        self.text.refresh()
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
