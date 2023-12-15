import os
import curses
import threading
import numpy as np

class GameStartScreen:
    
    running = True
    resized = False
    
    def __init__(self, screen, texture):
        self.screen = screen
        self.resize()
        self.version = "0.0.1"
        self.options = 1
        self.logo_options = 0
        self.logo = texture[0].lines  # Przypisanie linii z pierwszego obiektu Textures
        self.mini_logo = texture[1].lines  # Przypisanie linii z drugiego obiektu Textures


    def resize(self):
        try:  # Linux
            w, h = os.get_terminal_size()
            curses.resizeterm(h, w)
        except:  # Windows
            h, w = self.screen.getmaxyx()

        w -= 1
        self.height = h
        self.width = w
        self.angle_increment = 1 / w
        self.buffer = [" " * self.width for _ in range(self.height)]

    def scale_logo(self):
        scaled_logo = []

        max_line_length = max(len(line) for line in self.logo)
        if max_line_length >= self.width or self.height <= 3:
            scaled_logo = self.mini_logo
            self.logo_options = len(self.mini_logo)
        else:
            scaled_logo = self.logo
            self.logo_options = len(self.logo)

        return scaled_logo
    
    def center_text(self, text):
        return text.center(self.width)

    def load_menu(self, fps):
        self.buffer = [" " * self.width for _ in range(self.height)]
        self.buffer[0] = f"FPS: {fps}"
        self.buffer[1] = self.center_text("")

        # Dodanie przeskalowanego logo
        scaled_logo = self.scale_logo()
        for i, line in enumerate(scaled_logo, start=2):
            if i < self.height:
                self.buffer[i] = self.center_text(line)

        # Dodanie wersji na końcu
        self.buffer[self.height-1] = (f"Version: {self.version}").rjust(self.width)

    def update(self, fps):
        self.buffer = [" " * self.width for _ in range(self.height)]
        self.load_menu(fps)

        for row_num, line_to_display in enumerate(self.buffer):
            if row_num == len(self.buffer) - 1:  # Ostatnia linia (wersja)
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(2))
            elif self.options == 1 and 1 + 1 + self.logo_options + 3 <= row_num <= 1 + 1 + self.logo_options + 3 + 3:
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(2))
            elif self.options == 2 and 1 + 1 + self.logo_options + 8 <= row_num <= 1 + 1 + self.logo_options + 8 + 3:
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(2))
            else:
                self.screen.addstr(row_num, 0, line_to_display)
        self.screen.refresh()
