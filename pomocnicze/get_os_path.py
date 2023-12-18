import os
import platform


def get_config_path():
    if platform.system() == "Windows":
        config_dir = os.path.join(os.getenv('APPDATA'), "ChronoMystica", "settings")
    else:  # Linux i inne systemy Unix
        config_dir = os.path.join(os.path.expanduser('~'), ".ChronoMystica", "settings")

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    return os.path.join(config_dir, "keyboard_setting.json")