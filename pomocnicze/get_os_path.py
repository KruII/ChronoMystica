import os
import platform


def get_config_path(name, standard = "settings"):
    '''
    Zwraca ściężkę gdzie są lub mają być zapisywane pliki
    
    Parametry:
        name (str):
            Nazwa pliku
    '''
    if platform.system() == "Windows":
        config_dir = os.path.join(os.getenv('APPDATA'), "ChronoMystica", standard)
    else:  # Linux i inne systemy Unix
        config_dir = os.path.join(os.path.expanduser('~'), ".ChronoMystica", standard)

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    return os.path.join(config_dir, name)