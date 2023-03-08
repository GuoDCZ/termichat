import argparse
import os
import json
import openai

def parse_command_line():
    parser = argparse.ArgumentParser(description="A simple chatBot using Openai gpt-3.5-turdo model")
    parser.add_argument('-r', '--role', 
                        type=str, default="0", 
                        help='Choose the bot\'s role (0 by default stands for original role). Check all roles in the file \"role_play_data.json\"')
    parser.add_argument('-m', '--memorable', 
                        action='store_true', 
                        help='The chatBot can remember previous dialogues.')
    parser.add_argument('-t', '--temperature', 
                        type=float, default=1, 
                        help='Sampling temperature to use (between 0 and 2). Higher values make the output more random, while lower values make it more focused.')
    parser.add_argument('-p', '--presence_penalty', 
                        type=float, default=0, 
                        help='Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model\'s likelihood to talk about new topics.')
    parser.add_argument('-f', '--frequency_penalty', 
                        type=float, default=0, 
                        help='Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model\'s likelihood to repeat the same line verbatim.')
    parser.add_argument('request',
                        type=str, nargs='*',
                        help='Input your request directly in the command line and the program will exit after respond to the request')
    return parser.parse_args()

def print_chatbot_config(role_info, args):
    print( "   ChatBot 1.1")
    print(f" - role: {role_info['name']}")
    print(f" - memorable: {args.memorable}")
    print(f" - temperature: {args.temperature}")
    print(f" - presence_penalty: {args.presence_penalty}")
    print(f" - frequency_penalty: {args.frequency_penalty}")
    print()

def get_user_message():
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
    return {'role': 'user', 'content': prompt.strip('\n')}

def get_role_info(args):
    with open('role_play_data.json', 'r', encoding='utf-8') as f:
        role_play_data = json.load(f)["roles"]
    role_index = 0
    if args.role.isdigit():
        role_index = int(args.role)
        if role_index >= len(role_play_data):
            role_index = 0
    else:
        for i in range(len(role_play_data)):
            if role_play_data[i]["name"] == args.role:
                role_index = i
                break
    return role_play_data[role_index]

def get_initial_messages(role_info):
    return [{'role': 'system', 'content': role_info["content"]}]

def get_bot_message(messages, args):
    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo", 
        messages = messages, 
        temperature = args.temperature, 
        presence_penalty = args.presence_penalty, frequency_penalty = args.frequency_penalty)
    bot_message = completion["choices"][0]["message"] # tokens_usage = completion["usage"]["total_tokens"]
    return bot_message

def run_chatbot(args):
    role_info = get_role_info(args)
    if not args.request:
        print_chatbot_config(role_info, args)
        messages = get_initial_messages(role_info)
        while True:
            user_message = get_user_message()
            messages.append(user_message)
            print(f'@{role_info["name"]}> ...', end='', flush=True)
            bot_message = get_bot_message(messages, args)
            response = bot_message["content"].strip('\n')
            print(f'\b\b\b{response}\n')
            if args.memorable:
                messages.append(bot_message)
            else:
                messages = get_initial_messages(role_info)
    else:
        messages = get_initial_messages(role_info)
        messages.append({'role': 'user', 'content': '\n'.join(args.request).strip('\n')})
        bot_message = get_bot_message(messages, args)
        response = bot_message["content"].strip('\n')
        print(response)

def main():
    args = parse_command_line()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    run_chatbot(args)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e.args)
    finally:
        os.system('pause')

