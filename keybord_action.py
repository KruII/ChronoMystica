import json
import os
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from pomocnicze.get_os_path import get_config_path

DEFAULT_KEYS = {
    "JUMP": ["Key.space", None],
    "QUIT": ["Key.esc", None],
    "FORWARD": ["'w'", None],
    "BACKWARD": ["'s'", None],
    "LEFT": ["'a'", None],
    "RIGHT": ["'d'", None],
    "LOOK_UP": ["Key.up", None],
    "LOOK_DOWN": ["Key.down", None],
    "LOOK_LEFT": ["Key.left", None],
    "LOOK_RIGHT": ["Key.right", None]
}

class Keyboard(object):
    def __init__(self):
        self.config_file = get_config_path()
        if not os.path.exists(self.config_file):
            self.key_list = DEFAULT_KEYS
            self.save_config()
        else:
            self.load_config()
        self.pressed_keys = set()
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.key_list, file, indent=4)

    def load_config(self):
        with open(self.config_file, 'r') as file:
            self.key_list = json.load(file)

    def set_key(self, action, primary_key, secondary_key=None):
        if action in self.key_list:
            self.key_list[action] = [primary_key, secondary_key]
            self.save_config()

    def get_assigned_keys(self, action):
        return self.key_list.get(action, None)
    
    def on_press(self, key):
        self.pressed_keys.add(key)

    def on_release(self, key):
        self.pressed_keys.discard(key)

    def is_key_pressed(self, key):
        # Jeśli key jest stringiem, należy przekonwertować go na odpowiedni obiekt Key lub KeyCode
        if isinstance(key, str):
            if key.startswith('Key.'):
                key = getattr(Key, key.split('.')[1])
            else:
                key = KeyCode.from_char(key.strip("'"))
        return key in self.pressed_keys