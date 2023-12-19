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
        self.option_history = ""
        self.options = 1
        self.selected_option = 0
        self.logo_options = 0
        self.logo_opt = 0
        self.logo = texture[0].lines  # Przypisanie linii z pierwszego obiektu Textures
        self.mini_logo = texture[1].lines  # Przypisanie linii z drugiego obiektu Textures
        self.element_menu_name = ["START", "OPTIONS", "QUIT"]
        self.KeyboardOPT = False
        self.CheckingKeyboard = False
        self.first_and_last_key = [None, None]
        self.AudioOPT = False
        self.CheckingAudio = False
        self.ZaMalyEkran = False
        self.audio_level = {}
        self.test =""


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
        self.ZaMalyEkran = False

        max_line_length = max(len(line) for line in self.logo)
        if 60>self.width or len(self.element_menu_name)*4+9>self.height and not self.KeyboardOPT:
            self.ZaMalyEkran = True
            scaled_logo = ["Zamaly ekran"]
            self.logo_opt = -10
        elif 60>self.width or len(self.element_menu_name)+12>self.height and self.KeyboardOPT:
            self.ZaMalyEkran = True
            scaled_logo = ["Zamaly ekran"]
            self.logo_opt = -10
        elif max_line_length >= self.width or len(self.element_menu_name)*5+len(self.logo)+3 >= self.height:
            scaled_logo = self.mini_logo
            self.logo_options = len(self.mini_logo)
            self.logo_opt = 3
        else:
            scaled_logo = self.logo
            self.logo_options = len(self.logo)
            self.logo_opt = 4

        return scaled_logo
    
    def center_text(self, text):
        return text.center(self.width)

    def element_menu(self, element):
        if len(element)<11:
            frame_width = 15
        else:
            frame_width = len(element) + 4
            
        # Górna linia ramki
        top_frame = '#' * frame_width

        # Centrowanie elementu w ramce
        framed_element = f"# {element.center(frame_width - 4)} #"

        # Dolna linia ramki
        bottom_frame = '#' * frame_width

        # Łączenie wszystkiego w całość
        framed_menu_element = f"{top_frame}\n{framed_element}\n{bottom_frame}"

        return framed_menu_element



    def load_menu(self, fps):
        self.buffer = [" " * self.width for _ in range(self.height)]
        scaled_logo = self.scale_logo()
        if scaled_logo == ["Zamaly ekran"]:
            for i, line in enumerate(scaled_logo, start=1):
                if i < self.height:
                    self.buffer[i] = self.center_text(line)
            return
        self.buffer[0] = f"FPS: {fps}"+" "*(self.width-len(f"FPS: {fps}")-1)
        self.buffer[1] = self.center_text(f"{self.test}")

        # Dodanie przeskalowanego logo
        scaled_logo = self.scale_logo()
        for i, line in enumerate(scaled_logo, start=2):
                if i < self.height:
                    self.buffer[i] = self.center_text(line)
        start_line = i-1
        if not self.KeyboardOPT and not self.AudioOPT:
            for element_name in self.element_menu_name:
                element_menu = self.element_menu(element_name)  # Załóżmy, że szerokość ramki to 20
                element_menu_lines = element_menu.split('\n')
                start_line+=1+self.logo_opt  # Startowy wiersz dla elementu menu, tuż po logo

                for j, line in enumerate(element_menu_lines):
                    if start_line + j < self.height:
                        self.buffer[start_line + j] = self.center_text(line)
        elif self.KeyboardOPT and not self.AudioOPT:
            start_line+=3
            self.buffer[start_line] = "—"*self.width
            start_line+=2
            for element_name in self.element_menu_name:
                self.buffer[start_line] = "     "+element_name+" "*(self.width-len(element_name)-len("     "))
                start_line+=1
            start_line+=1
            self.buffer[start_line] = "—"*self.width
            start_line+=1
            self.buffer[start_line] = "     "+"SAVE"+" "*(self.width-len("SAVE")-len("     "))
            start_line+=1
            self.buffer[start_line] = "     "+"CANCEL"+" "*(self.width-len("CANCEL")-len("     "))
            if self.CheckingKeyboard:
                temps = ["———FIRST—KEY———",f"{self.first_and_last_key[0]}".center(15),"——SECOND——KEY——",f"{self.first_and_last_key[1]}".center(15),""," IF NONE PRESS ESCAPE"]
                start_line=i+4
                for i, temp in enumerate(temps):
                    temp = self.buffer[start_line+i][:self.width//2-len(temp)//2]+temp
                    self.buffer[start_line+i] = temp + " " * (self.width - len(temp))
        elif not self.KeyboardOPT and self.AudioOPT:
            start_line+=3
            self.buffer[start_line] = "—"*self.width
            start_line+=self.logo_opt-2
            self.buffer[start_line] = self.center_text("———MASTER———")
            self.buffer[start_line+1] = self.center_text("#"*self.audio_level["MASTER"]+"."*(10-len("#"*self.audio_level["MASTER"])))
            self.buffer[start_line+2] = self.center_text("————————————")
            start_line+=self.logo_opt+1
            self.buffer[start_line] = self.center_text("———MUSIC————")
            self.buffer[start_line+1] = self.center_text("#"*self.audio_level["MUSIC"]+"."*(10-len("#"*self.audio_level["MUSIC"])))
            self.buffer[start_line+2] = self.center_text("————————————")
            start_line+=self.logo_opt+1
            self.buffer[start_line] = self.center_text("————GAME————")
            self.buffer[start_line+1] = self.center_text("#"*self.audio_level["GAME"]+"."*(10-len("#"*self.audio_level["GAME"])))
            self.buffer[start_line+2] = self.center_text("————————————")
            start_line+=self.logo_opt+1
            self.buffer[start_line] = self.center_text("———INPUTS———")
            self.buffer[start_line+1] = self.center_text("#"*self.audio_level["INPUTS"]+"."*(10-len("#"*self.audio_level["INPUTS"])))
            self.buffer[start_line+2] = self.center_text("————————————")
            element_menu = self.element_menu("BACK")
            element_menu_lines = element_menu.split('\n')
            start_line+=self.logo_opt+1

            for j, line in enumerate(element_menu_lines):
                if start_line + j < self.height:
                    self.buffer[start_line + j] = self.center_text(line)
        else:
            self.KeyboardOPT, self.AudioOPT = False
            print("Fatal error")

        # Dodanie wersji na końcu
        self.buffer[self.height-1] = (f"Version: {self.version} ").rjust(self.width)

    def update(self, fps):
        self.buffer = [" " * self.width for _ in range(self.height)]
        self.load_menu(fps)

        for row_num, line_to_display in enumerate(self.buffer):
            if row_num == len(self.buffer) - 1:  # Ostatnia linia (wersja)
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(2))
            elif self.logo_options + self.logo_opt*self.options+self.options <= row_num < self.logo_options + self.logo_opt*self.options+self.options + 3 and not self.KeyboardOPT:
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(1))
            elif self.logo_options + 4 + self.options == row_num and self.KeyboardOPT:
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(1))
            else:
                self.screen.addstr(row_num, 0, line_to_display)
        self.screen.refresh()
