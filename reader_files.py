import os

class Textures:
    
    def __init__(self, texture_name):
        self.lines = []  # Inicjalizacja pustej listy dla wierszy tekstury
        texture_path = os.path.join("textures", texture_name)
        try:
            with open(texture_path) as file:
                self.lines = [line.rstrip('\n') for line in file.readlines()]
        except FileNotFoundError:
            self.lines = [f"Error: Textura {texture_name} nie odnaleziona"]
