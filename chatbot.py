import argparse
import os
import json
import openai
import curses
import time
import threading

from chatlog import ChatLog
from chatUI import ChatUI
from text import TextBox

CONFIG_FILE = "config.json"
ROLEPLAY_DIR = "roleplay/"

def print_config(config):
    print(f"- Role: {config['role']}")
    print(f"- Memorable: {config['memorable']}")
    print(f"- Temperature: {config['temperature']}")
    print(f"- Presence Penalty: {config['presence_penalty']}")
    print(f"- Frequency Penalty: {config['frequency_penalty']}")
    print()
    
class Control:
    def __init__(self, config):
        self.log: ChatLog = ChatLog(config)
        self.tb: TextBox = TextBox()

    def run(self, stdscr: curses.window):
        self.ui: ChatUI = ChatUI(stdscr, self.log)
        self.ui.refresh_log()
        self.ui.refresh_pad()
        self.alt: bool = False
        while True:
            key = stdscr.getch()
            if key == 526:
                self.put_key('!')
            if not self.put_key(key):
                break

    def put_key(self, key):
        if not self.alt and key == 27: # ALT
            self.alt = True
        elif self.alt and key == 10: # ALT + ENTER
            self.log.add_prompt(self.tb.s)
            self.tb.clear()
            self.ui.refresh_log()
            self.ui.refresh_pad()
            self.log.add_response()
            self.ui.refresh_log()
            self.alt = False
        elif self.alt and key == 27: # doubel ESC
            return False
        elif key == 336: # SHIFT + DOWN
            self.ui.scroll_down()
        elif key == 337: # SHIFT + UP
            self.ui.scroll_up()
        elif key == 393: # SHIFT + LEFT
            self.ui.page_down()
        elif key == 402: # SHIFT + RIGHT
            self.ui.page_up()
        # elif key == 410: # RESIZE
        #     curses.update_lines_cols()
        #     self.pad.resize(1000, curses.COLS)
        #     self.update_pad()
        elif key == 546: # CTRL + LEFT
            self.log.move_prev()
            self.ui.refresh_log()
        elif key == 561: # CTRL + RIGHT
            self.log.move_next()
            self.ui.refresh_log()
        else:
            self.tb.put_key(key)
            self.ui.refresh_tb(self.tb)
        self.ui.refresh_pad()
        return True

def run_infile(self, infile):
    f = open(infile)
    line = f.readline()
    while line:
        for r in range(0,1):
            self.set_initial_chat()
            self.set_user_message(line)
            response = self.set_bot_message()
            print(response)
            time.sleep(0.5)
        print()
        line = f.readline()
    f.close()

def run_single(self, request):
    self.set_initial_chat()
    self.set_user_message(request)
    response = self.set_bot_message()
    print(response)

def init_config():
    oldConfig = {}
    if os.path.exists(CONFIG_FILE):
        oldConfig = load_config()
    
    def config_key(key, prompt, defaultValBackUp):
        defaultVal = oldConfig.get(key)
        if defaultVal is None:
            defaultVal = defaultValBackUp
        res = input(f"{prompt}(Default: {defaultVal}): ").strip()
        if not res:
            res = str(defaultVal)
        return res
    
    print("Configuring...")
    newConfig = {}

    newConfig["roleDir"] = config_key("roleDir", "Roleplay Content Directory", ROLEPLAY_DIR)

    roleFileList = os.listdir(ROLEPLAY_DIR)
    if roleFileList is None:
        roleFileList[0] = None
    roleListStr = " ".join(roleFile[:-4] for roleFile in roleFileList)
    newConfig["role"] = config_key("role", f"Role ({roleListStr})", roleFileList[0][:-4])

    newConfig["memorable"] = config_key("memorable", "Memorable (y/n)", "n")
    newConfig["temperature"] = float(config_key("temperature", "Temperature", 1))
    newConfig["presence_penalty"] = float(config_key("presence_penalty", "Presence Penalty", 0))
    newConfig["frequency_penalty"] = float(config_key("frequency_penalty", "Frequency Penalty", 0))

    return newConfig

def load_config():
    return json.load(open(CONFIG_FILE))

def parse_command_line():
    parser = argparse.ArgumentParser(description="A simple chatBot using Openai gpt-3.5-turdo model")
    parser.add_argument('-i', '--infile', 
                        type=str, default='', 
                        help='Specify a file as a prompt collections.')
    parser.add_argument('-c', '--config',
                        action="store_true",
                        help='Configuring the config file.')
    parser.add_argument('-t', '--temp',
                        action="store_true",
                        help='Start a new chat with temparary specified configuration. ')
    parser.add_argument('request',
                        type=str, nargs='*',
                        help='Input your request directly in the command line and the program will exit after respond to the request')
    return parser.parse_args()

def save_config(config):
    try:
        json.dump(
            config,
            open(CONFIG_FILE, mode="w", encoding="utf-8"),
            indent=4
        )
    except Exception as e:
        print(f"\nError: {e.__class__.__name__}. Failed to create config file.")
        exit(1)

def main():
    args = parse_command_line()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if args.config or not os.path.exists(CONFIG_FILE):
        save_config(init_config())
    elif args.infile:
        chatbot = ChatBot(load_config())
        chatbot.print_config()
        chatbot.run_infile(args.infile)
    elif args.request:
        chatbot = ChatBot(load_config())
        chatbot.run_single(args.request)
    elif args.temp:
        chatbot = ChatBot(init_config())
        chatbot.run_normal()
    else:
        config = load_config()
        print_config(config)
        ctrl = Control(config)
        curses.wrapper(ctrl.run)

if __name__ == '__main__':
    main()

