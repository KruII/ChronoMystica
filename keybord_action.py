import json
import os
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from pomocnicze.get_os_path import get_config_path

DEFAULT_KEYS = {
    "O_JUMP": ["Key.space", None],
    "QUIT": ["Key.esc", None],
    "A_FORWARD": ["'w'", None],
    "A_BACKWARD": ["'s'", None],
    "A_LEFT": ["'a'", None],
    "A_RIGHT": ["'d'", None],
    "A_LOOK_UP": ["Key.up", None],
    "A_LOOK_DOWN": ["Key.down", None],
    "A_LOOK_LEFT": ["Key.left", None],
    "A_LOOK_RIGHT": ["Key.right", None],
    "S_FORWARD": ["'w'", "Key.up"],
    "S_BACKWARD": ["'s'", "Key.down"],
    "S_LEFT": ["'a'", "Key.left"],
    "S_RIGHT": ["'d'", "Key.right"],
    "O_RUN": ["Key.shift", None],
    "O_SNEAK": ["Key.ctrl", None],
    "UP": ["Key.up", "'w'"],
    "DOWN": ["Key.down", "'s'"],
    "CONTROL_LEFT": ["Key.left", "'a'"],
    "CONTROL_RIGHT": ["Key.right", "'d'"],
    "ENTER": ["Key.enter", "Key.space"]
}


class Keyboard(object):
    def __init__(self):
        self.KEYS_MAP = {"Key.space": "SPACE",
            "Key.left": "←",
            "Key.right": "→",
            "Key.up": "↑",
            "Key.down": "↓",
            "Key.enter": "ENTER",
            "Key.tab": "TAB",
            "Key.shift": "SHIFT",
            "Key.ctrl_l": "CTRL",
            "Key.alt_l": "ALT",
            "Key.ctrl_r": "CTRL"}
        self.config_file = get_config_path("keyboard_setting.json")
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
    
    def user_input_getKeybord(self):
        """
        Nasłuchuje wciśnięcia i odciśnięcia klawisza przez użytkownika, zwracając jego wartość.
        Zwraca None, jeśli naciśnięto klawisz Escape. Umożliwia ponowne użycie klawisza po jego odciśnięciu.
        """
        # Zapisz aktualny stan wciśniętych klawiszy
        initial_pressed_keys = set(self.pressed_keys)

        while True:

            new_pressed_keys = self.pressed_keys - initial_pressed_keys

            for key in new_pressed_keys:
                if key == Key.esc:
                    return None
                else:
                    # Jeśli key jest KeyCode, zwróć jego char, w przeciwnym razie zwróć nazwę klawisza
                    return "'"+key.char+"'" if isinstance(key, KeyCode) else "Key."+key.name
            initial_pressed_keys = set(self.pressed_keys)


