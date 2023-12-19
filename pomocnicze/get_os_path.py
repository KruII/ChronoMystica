import os
import platform


def get_config_path(name):
    '''
    Zwraca ściężkę gdzie są lub mają być zapisywane ustawienia
    
    Parametry:
        name (str):
            Nazwa pliku
    '''
    if platform.system() == "Windows":
        config_dir = os.path.join(os.getenv('APPDATA'), "ChronoMystica", "settings")
    else:  # Linux i inne systemy Unix
        config_dir = os.path.join(os.path.expanduser('~'), ".ChronoMystica", "settings")

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    return os.path.join(config_dir, name)