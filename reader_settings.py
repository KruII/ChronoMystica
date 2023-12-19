import os
import json

from pomocnicze.get_os_path import get_config_path

class Settings_R:
    def __init__(self):
        self.config_file = get_config_path("main_setting.json")

    def check_is_config(self):
        if not os.path.exists(self.config_file):
            self.new_config()
            return True, True, 3, False, {"MASTER": 10, "MUSIC": 10, "GAME": 10, "INPUTS": 10}
        else:
            return self.load_config()
            
    def new_config(self):
        with open(self.config_file, 'w') as file:
            json.dump([True, True, 3, False, {"MASTER": 10, "MUSIC": 10, "GAME": 10, "INPUTS": 10}], file, indent=4)
                      
    def save_config(self, limitetFPS, SHOW_FPS, quality, advanced_control, audio_level):
        with open(self.config_file, 'w') as file:
            json.dump([limitetFPS, SHOW_FPS, quality, advanced_control, audio_level], file, indent=4)
            
    def load_config(self):
        with open(self.config_file, 'r') as file:
            return(json.load(file))

        