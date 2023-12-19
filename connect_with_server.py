import json
import os
import socket

from pomocnicze.get_os_path import get_config_path

class OnlineServer:
    
    def __init__(self):
        self.ip = "83.168.107.86"
        self.port = 65432
        self.config_file = get_config_path("IP_Config.json")
        if not os.path.exists(self.config_file):
            self.save_config()
        else:
            self.load_config()
        
    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump([self.ip, self.port], file, indent=4)

    def load_config(self):
        with open(self.config_file, 'r') as file:
            self.ip, self.port = json.load(file)
        
    def connect_with_serwer(self):
        # Tworzy gniazdo (socket) i łączy się z serwerem
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                return True
        except Exception as e:
            print(f"Nie można połączyć: {e}")
            return False

