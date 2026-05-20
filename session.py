import os
import json
from gi.repository import GLib

APP_ID = "com.github.revivenotes"
STATE_DIR = os.path.join(GLib.get_user_state_dir(), "revivenotes")
SESSION_FILE = os.path.join(STATE_DIR, "session.json")
SETTINGS_FILE = os.path.join(STATE_DIR, "settings.json")

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"theme": "system", "font": "Monospace 12"}
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {"theme": "system", "font": "Monospace 12"}

def save_settings(settings_data):
    if not os.path.exists(STATE_DIR):
        os.makedirs(STATE_DIR, exist_ok=True)
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings_data, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_session():
    if not os.path.exists(SESSION_FILE):
        return []
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading session: {e}")
        return []

def save_session(tabs_data):
    if not os.path.exists(STATE_DIR):
        os.makedirs(STATE_DIR, exist_ok=True)
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(tabs_data, f, indent=4)
    except Exception as e:
        print(f"Error saving session: {e}")
