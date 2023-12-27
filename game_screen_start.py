import os
import curses
import numpy as np

class GameStartScreen:
    
    running = True
    resized = False
    
    def __init__(self, screen, texture):
        '''
        Funkcji inicjująca
        
        Parametry:
            screen: 
                ekran
            
            texture (str[]):
                Zapis tekstur
                Linijka po linijce jak ma wyglądać dla wszystkich wczytanych
        '''
        self.screen = screen
        self.version = "0.0.1"                                                     # Wersja Gry do wyświetlania
        self.option_history = ""                                                   # Historia wyboru opcji 
        self.options = 1                                                           # Numer przycisku/opcji                                                 # 
        self.logo_options = 0                                                      # Wysokość Logo
        self.logo_opt = 0                                                          # Ile przerwy między przyciskami
        self.logo = texture[0].lines                                               # Tablica linii w dużej teksturze
        self.mini_logo = texture[1].lines                                          # Tablica linii w małej teksturze
        self.element_menu_name = ["START", "OPTIONS", "QUIT"]                      # Tablica przycisków menu
        self.KeyboardOPT = False                                                   # Czy menu dla przypisanych klawiszy
        self.CheckingKeyboard = False                                              # Czy dodać widok wpisania klawiszy
        self.first_and_last_key = [None, None]                                     # Tablica dla wyświetlania CheckingKeyboard
        self.AudioOPT = False                                                      # Czy menu dla ustawiania głośności audio
        self.TooSmallScreen = False                                                # Czy ekran jest zbyt mały
        self.audio_level = {}                                                      # Mapa poziomu głośności
        self.connecting = ""                                                       # Czy łączy z serwerem
        self.animation_connecting = [0, 0, 5,                                      # Aktualny znak, Opóźnienie++, Opóźnienie_MAX
                                     '|', '/', '—', '\\', '|', '/', '—', '\\']     # Znaki Animacji 
        self.test =""                                                              # String do testowania działania
        self.ServerList = None                                                       # Lista Serwerów
        self.MultiPlayerServer = {
                                  "Page":        1,
                                  "MAX_Page":    1,
                                  "Option":      1,
                                  "Size_Page":   1,
                                  "Visible":     False,
                                  "Search_Text": "."*11,
                                  "Refresh":     False,
                                 }
        
        self.resize()                                                              # Inicjacja ustalenia miejsca w oknie

    def resize(self):
        '''
        Ustalanie maksymalnej wysokości i długości
        '''            
        try:         # Linux
            w, h = os.get_terminal_size()
            curses.resizeterm(h, w)
        except:      # Windows
            h, w = self.screen.getmaxyx()

        w -= 1
        self.height = h
        self.width = w
        self.angle_increment = 1 / w
        self.buffer = [" " * self.width for _ in range(self.height)]

    def scale_logo(self):
        '''
        Ustawienie odpowiedniego Logo (Logo lub mini_Logo)
        Lub jeżeli ekran zbyt mały ustawienie flagi zbyt małego ekranu na True
        '''
        
        scaled_logo = []

        max_line_length = max(len(line) for line in self.logo)
        if 60>self.width or len(self.element_menu_name)*4+9>self.height and not self.KeyboardOPT:
            scaled_logo = ["Zamaly ekran"]
            self.logo_opt = -10
        elif 60>self.width or len(self.element_menu_name)+12>self.height and self.KeyboardOPT:
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
        '''
        Centrowanie tekstu względem szerokości okna
        
        Parametry:
            text (str):
                Tekst do wycentrowania
        '''
        return text.center(self.width)

    def element_menu(self, element):
        '''
        Tworzenie przycisku menu
        
        Parametry:
            element (str):
                Nazwa przycisku
        '''
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
    
    def fix_fill_line(self, text):
        return text+" "*(self.width - len(text))
    
    def server_element_reader(self, element):
        return " "+element["nazwa"]+" "*(11-len(element["nazwa"]))+" │ "+(element["opis"][:self.width-29]+"..." if len(element["opis"])>self.width-26 else element["opis"][:self.width-26]) +" "*(self.width-26-len(element["opis"]))+" │ "+str(element["ilosc_graczy"]).rjust(5)+"   "
    
    def tab_printer(self, char):
        return "─"*13+char+"─"*(self.width-24)+char+"─"*9
    
    def tab_page_setter(self):
        server_pages = []
        
        Max_height_page = int((self.height - 12)//2)
                
        server_page = []
        for element_menu in self.element_menu_name:
            if len(server_page) < Max_height_page:
                server_page.append(element_menu)
            else:
                server_pages.append(server_page)
                server_page = [element_menu]
            
        if server_page:
            server_pages.append(server_page)
                
        self.MultiPlayerServer["MAX_Page"] = len(server_pages)
        
        return server_pages


    def load_menu(self, fps):
        '''
        Budowanie menu do wyrenderowania
        
        Parametry:
            fps (int):
                Wartość klatek na sekunde
        '''
        self.buffer = [" " * self.width for _ in range(self.height)]
        self.buffer[0] = f"FPS: {fps}"+" "*(self.width-len(f"FPS: {fps}")-1)
        self.TooSmallScreen = False
    
        if self.connecting != "":
            if self.animation_connecting[1]<self.animation_connecting[2]:
                self.animation_connecting[1]+=1
            else:
                self.animation_connecting[1]=0
                if self.animation_connecting[0]<7:
                    self.animation_connecting[0]+=1
                else:
                    self.animation_connecting[0]=0
            self.buffer[1] = self.center_text(self.connecting+"ing "+self.animation_connecting[self.animation_connecting[0]+3])
            self.buffer[self.height-1] = (f"Version: {self.version} ").rjust(self.width)
            return
        
        if self.MultiPlayerServer["Visible"] == True:
            try:
                if self.height < 14 or self.width < 37:
                    self.TooSmallScreen = True
                    self.buffer[1] = self.center_text("Zamaly ekran")
                    self.buffer[self.height-1] = (f"Version: {self.version} ").rjust(self.width)
                    return
                server_pages = self.tab_page_setter()
                self.MultiPlayerServer["Size_Page"] = len(server_pages[self.MultiPlayerServer["Page"]-1])
                start_line = 1
                self.buffer[start_line] = "─"*self.width
                self.buffer[start_line+1] = self.center_text(f'PAGE: {self.MultiPlayerServer["Page"]}')
                start_line += 2
                self.buffer[start_line] = self.tab_printer("┬")
                self.buffer[start_line+1] = " SERVER NAME │ DESCRIPTION"+" "*(self.width - 37)+" │ PLAYERS "
                start_line += 2
                
                for element_menu in server_pages[self.MultiPlayerServer["Page"]-1]:
                    self.buffer[start_line] = self.tab_printer("┼")
                    self.buffer[start_line+1] = self.server_element_reader(element_menu)
                    start_line+=2

                self.buffer[start_line] = self.tab_printer("┴")
                
                self.buffer[self.height-5] = self.fix_fill_line(" SEARCH NAME: " +self.MultiPlayerServer["Search_Text"])[:self.width-8]+"SEARCH  "
                self.buffer[self.height-4] = "  < "+" "*(self.width-8)+" >  "
                self.buffer[self.height-3] = "  BACK"+" "*(self.width-14)+"RELOAD "
                self.buffer[self.height-1] = (f"Version: {self.version} ").rjust(self.width)
            except:
                self.MultiPlayerServer["Page"] = 1
                self.options = 1
            return
        scaled_logo = self.scale_logo()
        if scaled_logo == ["Zamaly ekran"]:
            self.TooSmallScreen = True
            self.buffer[1] = self.center_text(scaled_logo[0])
            self.buffer[self.height-1] = (f"Version: {self.version} ").rjust(self.width)
            return
        self.buffer[1] = self.center_text(f"{self.test}")

        # Dodanie przeskalowanego logo
        scaled_logo = self.scale_logo()
        for i, line in enumerate(scaled_logo, start=2):
                if i < self.height:
                    self.buffer[i] = self.center_text(line)
        start_line = i-1
            
        if not self.KeyboardOPT and not self.AudioOPT:
            for element_name in self.element_menu_name:
                element_menu = self.element_menu(element_name)
                element_menu_lines = element_menu.split('\n')
                start_line+=1+self.logo_opt 

                for j, line in enumerate(element_menu_lines):
                    if start_line + j < self.height:
                        self.buffer[start_line + j] = self.center_text(line)
        elif self.KeyboardOPT and not self.AudioOPT:
            start_line+=3
            self.buffer[start_line] = "—"*self.width
            start_line+=2
            for element_name in self.element_menu_name:
                self.buffer[start_line] = self.fix_fill_line("     "+element_name)
                start_line+=1
            start_line+=1
            self.buffer[start_line] = "—"*self.width
            start_line+=1
            self.buffer[start_line] = self.fix_fill_line("     "+"SAVE")
            start_line+=1
            self.buffer[start_line] = self.fix_fill_line("     "+"CANCEL")
            if self.CheckingKeyboard:
                temps = ["———FIRST—KEY———",f"{self.first_and_last_key[0]}".center(15),"——SECOND——KEY——",f"{self.first_and_last_key[1]}".center(15),""," IF NONE PRESS ESCAPE"]
                start_line=i+4
                for i, temp in enumerate(temps):
                    temp = self.buffer[start_line+i][:self.width//2-len(temp)//2]+temp
                    self.buffer[start_line+i] = temp + " " * (self.width - len(temp))
        elif not self.KeyboardOPT and self.AudioOPT:
            start_line+=3
            self.buffer[start_line] = "—"*self.width
            start_line-=3
            temp_menu = ["MASTER", "MUSIC", "GAME", "INPUTS"]
            for temp_element in temp_menu:
                start_line+=self.logo_opt+1
                self.buffer[start_line] = self.center_text(temp_element.center(12).replace(" ", "—"))
                self.buffer[start_line+1] = self.center_text("#"*self.audio_level[temp_element]+"."*(10-len("#"*self.audio_level[temp_element])))
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
        '''
        Renderowanie Menu
        
        Parametry:
            fps (int):
                Wartość klatek na sekunde
        '''
        self.buffer = [" " * self.width for _ in range(self.height)]
        self.load_menu(fps)

        for row_num, line_to_display in enumerate(self.buffer):
            if row_num == len(self.buffer) - 1:             # Ostatnia linia (wersja)
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(2))
            elif self.logo_options + self.logo_opt*self.options+self.options <= row_num < self.logo_options + self.logo_opt*self.options+self.options + 3 and not self.KeyboardOPT and not self.MultiPlayerServer["Visible"]:
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(1))
            elif self.KeyboardOPT and self.logo_options + 4 + self.options == row_num:
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(1))
            elif self.MultiPlayerServer["Visible"] and 4+self.options*2 == row_num and self.MultiPlayerServer["Size_Page"]>=self.options:
                self.screen.addstr(row_num, 0, line_to_display, curses.color_pair(1))
            elif self.MultiPlayerServer["Visible"] and row_num == len(self.buffer) - 5 and self.MultiPlayerServer["Size_Page"]+1==self.options:
                self.screen.addstr(row_num, 0, line_to_display)
                if self.MultiPlayerServer["Option"] == 1:
                    self.screen.addstr(row_num, 0, line_to_display[:14])
                    self.screen.addstr(row_num, 14, line_to_display[14:14+len(self.MultiPlayerServer["Search_Text"])], curses.color_pair(1))
                elif self.MultiPlayerServer["Option"] == 2: 
                    self.screen.addstr(row_num, self.width-1, line_to_display[self.width-1:self.width])
                    self.screen.addstr(row_num, self.width-9, line_to_display[self.width-9:self.width-1], curses.color_pair(1))
            elif self.MultiPlayerServer["Visible"] and row_num == len(self.buffer) - 4 and self.MultiPlayerServer["Size_Page"]+2==self.options:
                self.screen.addstr(row_num, 0, line_to_display)
                if self.MultiPlayerServer["Option"] == 1:
                    self.screen.addstr(row_num, 0, line_to_display[:1])
                    self.screen.addstr(row_num, 1, line_to_display[1:4], curses.color_pair(1))
                elif self.MultiPlayerServer["Option"] == 2: 
                    self.screen.addstr(row_num, self.width-1, line_to_display[self.width-1:self.width])
                    self.screen.addstr(row_num, self.width-4, line_to_display[self.width-4:self.width-1], curses.color_pair(1))
            elif self.MultiPlayerServer["Visible"] and row_num == len(self.buffer) - 3 and self.MultiPlayerServer["Size_Page"]+3==self.options:
                self.screen.addstr(row_num, 0, line_to_display)
                if self.MultiPlayerServer["Option"] == 1:
                    self.screen.addstr(row_num, 0, line_to_display[:1])
                    self.screen.addstr(row_num, 1, line_to_display[1:7], curses.color_pair(1))
                elif self.MultiPlayerServer["Option"] == 2: 
                    self.screen.addstr(row_num, self.width-1, line_to_display[self.width-1:self.width])
                    self.screen.addstr(row_num, self.width-9, line_to_display[self.width-9:self.width-1], curses.color_pair(1))
            else:
                self.screen.addstr(row_num, 0, line_to_display)
        self.screen.refresh()
