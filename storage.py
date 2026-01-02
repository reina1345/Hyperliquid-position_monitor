import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"addresses": [], "discord_token": "", "channel_id": 0}

    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"addresses": [], "discord_token": "", "channel_id": 0}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def add_address(address: str):
    config = load_config()
    if address not in config["addresses"]:
        config["addresses"].append(address)
        save_config(config)
        return True
    return False

def remove_address(address: str):
    config = load_config()
    if address in config["addresses"]:
        config["addresses"].remove(address)
        save_config(config)
        return True
    return False

def get_addresses():
    config = load_config()
    return config.get("addresses", [])

def get_discord_token():
    config = load_config()
    return config.get("discord_token", "")

def set_channel_id(channel_id: int):
    config = load_config()
    config["channel_id"] = channel_id
    save_config(config)

def get_channel_id():
    config = load_config()
    return config.get("channel_id", 0)
