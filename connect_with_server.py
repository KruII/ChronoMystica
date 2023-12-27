import json
import os
import socket
import time

from pomocnicze.get_os_path import get_config_path

class OnlineServer:
    
    def __init__(self):
        '''
        Funkcji inicjująca
        '''
        self.ip = "localhost"                                   # Adres IP serwera
        self.port = 65432                                       # Numer Portu serwera
        self.config_file = get_config_path("IP_Config.json")
        if not os.path.exists(self.config_file):
            self.create_config()
        else:
            self.load_config()
        self.connected = False                                  # Czy połączony z serwerem
        self.ping = 0
        self.ping_measurements = []                              # Lista do przechowywania pomiarów pingów

        
    def create_config(self):
        '''
        Tworzy plik JSON z adresem IP i numerem Portu
        '''
        with open(self.config_file, 'w') as file:
            json.dump([self.ip, self.port], file, indent=4)

    def load_config(self):
        '''
        Wczytuję z pliku JSON adres IP i numer Portu
        '''
        with open(self.config_file, 'r') as file:
            self.ip, self.port = json.load(file)

    def monitor_connection(self):
        if self.connected:
            try:
                start_time = time.time()  # Rozpoczęcie pomiaru czasu
                self.socket.send(b'heartbeat')
                response = self.socket.recv(1024)
                if response:
                    
                    end_time = time.time()
                    ping = (end_time - start_time) * 1000  # Ping w milisekundach
                    self.ping_measurements.append(ping)
                    if len(self.ping_measurements) > 20:
                        self.ping = sum(self.ping_measurements) / len(self.ping_measurements)
                        self.ping_measurements = []
                else:
                    #raise ConnectionError("Brak odpowiedzi od serwera")
                    pass
            except Exception as e:
                #print(f"Połączenie z serwerem zostało zerwane: {e}")
                self.connected = False


    def connect_with_serwer(self):
        '''
        Próba połączenia się z serwerem
        '''
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
            self.connected = True

            return True
        except Exception as e:
            self.connected = False
            return False

    def get_server_list(self, search_query=""):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                s.send(b'get_servers')
                response = s.recv(4096)
                server_list = json.loads(response.decode('utf-8'))
                if server_list == []:
                    return [{'id': 1, 'nazwa': 'Brak', 'opis': 'Brak Serwerów', 'ilosc_graczy': -1}]

                # Filtruj serwery według szukanej frazy (case-insensitive)
                if search_query:
                    search_query = search_query.replace('.', '').lower()
                    server_list = [server for server in server_list if search_query in server["nazwa"].lower()]
                    
                return server_list
        except Exception as e:
            #print(f"Błąd podczas pobierania listy serwerów: {e}")
            return []
            
        