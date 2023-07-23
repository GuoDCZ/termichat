import argparse
import os
import json
import openai
import curses
import time

from chatlog import ChatLog
from chatUI import ChatUI

CONFIG_FILE = "config.json"
ROLEPLAY_DIR = "roleplay/"

def print_config(config):
    print(f"- Role: {config['role']}")
    print(f"- Memorable: {config['memorable']}")
    print(f"- Temperature: {config['temperature']}")
    print(f"- Presence Penalty: {config['presence_penalty']}")
    print(f"- Frequency Penalty: {config['frequency_penalty']}")
    print()
    
def ask_user_message():
    prompt = ''
    while not prompt or prompt.isspace():
        prompt = input('@User> ')
    if prompt == '[':
        prompt = ''
        while True:
            line = input()
            if line == ']':
                break
            prompt += '\n' + line
    return prompt.strip('/n')

def run_normal(stdscr, config):

    chatlog = ChatLog()
    chatlog.load_config(config)
    
    ui = ChatUI(stdscr)
    chat = chatlog.get_chat()
    ui.update_pad(chat)

    while True:
        prompt = ui.ask_user_input()
        chatlog.set_prompt(prompt)
        chat = chatlog.get_chat()
        ui.update_pad(chat)
        chatlog.create_response()
        chat = chatlog.get_chat()
        ui.update_pad(chat)

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
        curses.wrapper(
        run_normal, config
        )

if __name__ == '__main__':
    main()

