import os
import json

CONFIG_FILE = "config.json"
ROLEPLAY_DIR = "roleplay/"

def print_config(config):
    print(f"- Role: {config['role']}")
    print(f"- Memorable: {config['memorable']}")
    print(f"- Temperature: {config['temperature']}")
    print(f"- Presence Penalty: {config['presence_penalty']}")
    print(f"- Frequency Penalty: {config['frequency_penalty']}")
    print()

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

    newConfig["model"] = float(config_key("model", "Model", "gpt-3-turbo"))
    newConfig["memorable"] = config_key("memorable", "Memorable (y/n)", "n")
    newConfig["temperature"] = float(config_key("temperature", "Temperature", 1))
    newConfig["presence_penalty"] = float(config_key("presence_penalty", "Presence Penalty", 0))
    newConfig["frequency_penalty"] = float(config_key("frequency_penalty", "Frequency Penalty", 0))

    return newConfig

def load_config():
    return json.load(open(CONFIG_FILE))

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
