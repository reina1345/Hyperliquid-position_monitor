import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"addresses": [], "webhook_url": ""}

    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"addresses": [], "webhook_url": ""}

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

def get_webhook_url():
    config = load_config()
    return config.get("webhook_url", "")
