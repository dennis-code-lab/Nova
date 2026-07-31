import os
import json
from modules.logger import log_info, log_error

CONFIG_PATH = os.path.join("data", "plugin_config.json")

# Default system configuration profile template
DEFAULT_SETTINGS = {
    "profile": {
        "user_name": "Dennis",
        "favorite_team": "Arsenal",
        "favorite_color": "green",
        "default_city": "Nairobi"
    },
    "security": {
        "default_trust_level": "HIGH",
        "session_logging": "ENABLED"
    },
    "ai_engine": {
        "temperature": "0.7",
        "max_tokens": "1024"
    }
}

def initialize_settings():
    """Guarantees that the data directory and configuration file exist on disk."""
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(CONFIG_PATH):
        log_info("SettingsEngine", "Seeding default configuration schema blueprint.")
        save_config(DEFAULT_SETTINGS)

def load_config() -> dict:
    """Loads and parses the active configuration profile from storage."""
    initialize_settings()
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        log_error("SettingsEngine", f"Failed reading settings layout: {e}")
        return DEFAULT_SETTINGS

def save_config(config_data: dict):
    """Writes an updated configuration dictionary securely back to disk."""
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        log_error("SettingsEngine", f"Error saving configuration update: {e}")

def update_setting(path_string: str, value_string: str) -> str:
    """
    Updates a specific setting field using a dot-notation path (e.g., 'profile.favorite_team').
    """
    log_info("SettingsEngine", f"Attempting setting alteration for: '{path_string}' -> '{value_string}'")
    config = load_config()
    parts = path_string.strip().split(".")
    
    current = config
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            return f"Error: Invalid configuration path branch at '{part}'."
        current = current[part]
        
    target_key = parts[-1]
    if target_key not in current:
         return f"Error: Field attribute '{target_key}' does not exist inside target configuration scope."
         
    # Update value parameter
    current[target_key] = value_string.strip()
    save_config(config)
    return f"Configuration field '{path_string}' successfully updated to '{value_string}'."

def render_settings_dashboard() -> str:
    """Compiles a clean layout visualization of all active system settings values."""
    config = load_config()
    output = "\n"+"="*50+"\n"
    output += "               NOVA PERSISTENT CONFIGURATION MATRIX\n"
    output += "="*50+"\n"
    
    for category, fields in config.items():
        output += f"[{category.upper()}]\n"
        for key, val in fields.items():
            output += f"  * {key:<20} : {val}\n"
        output += "\n"
    output += "="*50+"\n"
    return output