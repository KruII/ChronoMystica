import curses
import signal
import threading
import time
import pygetwindow as gw
from game_screen_start import GameStartScreen
from keybord_action import Keyboard
from audio_player import Audio
from reader_settings import Settings_R
from connect_with_server import OnlineServer

class Control:
    
    running = True                  # Jeżeli fałsz kończy grę                       | IF FALSE GAME STOP
    resized = False                 # Zmiana rozmiaru okna                          | RESIZE SCREEN
    FPS_SET = 60                    # Maksymanalna ilość remek na sekunde           | MAX FRAME PER SECOND
    UPS_SET = 120                   # Maksymanalna ilość aktualizacji na sekunde    | MAX UPDATES PER SECOND
    
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
        self.texture = texture
        self.screen_thread = GameStartScreen(self.screen, self.texture)                            # Ustawienia ekranu początkowego
        self.keyboard = Keyboard()                                                  
        self.audio = Audio()
        self.settings_r = Settings_R()
        self.onlineServer = OnlineServer()
        self.screen_opt = 1
        self.fps = 0                                                                               # Ustawia początkową wartość FPS na 0
        self.limitetFPS, self.SHOW_FPS, self.quality, self.advanced_control, self.audio_level = self.settings_r.check_is_config()
        self.quality_map = {3: 'H', 2: 'M', 1: 'L'}                                                # Mapa do wyświetlania znaku jakości dla
        self.last_up_press_time = 0
        self.last_down_press_time = 0
        self.last_enter_press_time = 0
        self.last_quit_press_time = 0
        self.key_repeat_delay = 0.5                                                                 # Opóźnienie między kolejnymi ruchami przy przytrzymanym klawiszu
        self.temp_keys = self.keyboard.key_list.copy()
        self.przedrotki = []
        self.audio.set_audio_list([0],[self.audio_level["INPUTS"]*self.audio_level["MASTER"]/100])  # Inicjalizacja z wszystkimi dostępnymi ścieżkami
        self.screen_thread.audio_level = self.audio_level
        self.CheckingAudio = False         
 
        try:
            signal.signal(signal.SIGWINCH, self.resize)
        except:
            pass

    def resize(self, *args):
        '''
        Po prostu zmienia resize na True
        '''
        self.resized = True
        
    def format_key_binding(self, key):
        '''
        Formatuje pojedynczy klawisz zgodnie z mapowaniem KEYS_MAP
        
        Parametry:
            key (str):
                Nazwa klawisza do sformatowania
        '''
        if key is None:
            return " "
        elif key in self.keyboard.KEYS_MAP:
            return self.keyboard.KEYS_MAP[key]
        elif key.startswith("'") and key.endswith("'"):
            return key.strip("'").upper()
        return key

    def format_key_bindings(self):
        '''
        Tworzy sformatowane ciągi dla przypisanych klawiszy
        '''
        formatted_bindings = []
        self.przedrotki = []
        for action, keys in self.temp_keys.items():
            action_prefix = action[0]+action[1]                                             # Pierwsze 2 znak nazwy akcji
            if action_prefix in ['O_', 'A_', 'S_']:
                if (self.advanced_control and action_prefix == 'A_') or (not self.advanced_control and action_prefix == 'S_') or action_prefix == 'O_':
                    formatted_keys = [self.format_key_binding(key) for key in keys]
                    formatted_binding = f"{action[2:]}: [ {' | '.join(formatted_keys)} ]"   # Usuwamy przedrostek z nazwy akcji
                    self.przedrotki.append(action)
                    formatted_bindings.append(formatted_binding)
        return formatted_bindings

    def off_on_switch(self, bool_value):
        '''
        Zmienia wartości True na False i odwrotnie
        
        Parametry:
            bool_value (bool):
                Jeżeli True:
                    Wydaję dźwięk "button_off"
                    Zwraca False
                Jeżeli False:
                    Wydeję dźwięk "button_on"
                    Zwraca True
        '''
        if bool_value:
            self.button_click_audio("button_off")
            return False
        else:
            self.button_click_audio("button_on")
            return True
        

    def set_first_and_last_key(self, line):
        '''
        Ustawia pierwszy i ostatni klawisz na podstawie danej linii

        Parametry:
            line (str): 
                Linia tekstu z przypisanymi klawiszami
        '''
        action, bindings = line.split(":")              # Rozdziela nazwę akcji od przypisanych klawiszy
        bindings = bindings.strip(" []").split(" | ")   # Usuwa zbędne spacje i znaki specjalne

        # Dodaj "NONE" jako drugi element, jeśli w bindings jest tylko jeden element
        if len(bindings) == 1:
            bindings[0] = bindings[0][:-2]              # Nie działa prawidłowo dla pojedynczego second_key
            bindings.append("NONE")

        # Przypisanie wartości do first_and_last_key
        return [b.strip() if b.strip() != "" else "NONE" for b in bindings]

    def data_button_colector(self):
        '''
        Kolekcjonuję jakie znaki zostały naciśnietę i wrzuca do ustawień
        '''
        temp = []
        temp.append(self.keyboard.user_input_getKeybord())
        self.screen_thread.first_and_last_key[0] = self.format_key_binding(temp[0])
        temp.append(self.keyboard.user_input_getKeybord())
        self.screen_thread.first_and_last_key[1] = self.format_key_binding(temp[1])
        time.sleep(0.5)
        self.temp_keys[self.przedrotki[self.screen_thread.options - 1]] = temp
        self.screen_thread.CheckingKeyboard = False
        self.screen_thread.element_menu_name = self.format_key_bindings()

    def screen_opener(self, logo, element_menu_name, opt, opt_his):
        '''
        Otwiera nowy układ/warstwę 
        
        Parametry:
            logo (int): 
                ID Loga, Znajduję się w game_start.py 

            element_menu_name (str[]): 
                Tablica nazwy przycisków jakie znajdują się w układzie/warstwię
            
            opt (int):
                ID układu/warstwy zgodny z nowo wyświetlanym układem/warstwą
                
            opt_his (bool):
                Jeżeli True:
                    Wczytuję na który przycisk ma ustawić zaznaczenie
                    Usuwa ostatni znak
                Jeżeli False:
                    Dodaję na jakim przycisku jest
                    Ustawia pozycję zaznaczenia przycisku na 1 
        '''
        self.button_click_audio("button2")
        if opt_his:
            self.screen_thread.options = int(self.screen_thread.option_history[len(self.screen_thread.option_history)-1])
            self.screen_thread.option_history = self.screen_thread.option_history[:-1]
        else:
            self.screen_thread.option_history += str(self.screen_thread.options)
            self.screen_thread.options = 1
        self.screen_thread.logo = self.texture[logo*2].lines            # Przypisanie linii z pierwszego obiektu Textures
        self.screen_thread.mini_logo = self.texture[logo*2+1].lines     # Przypisanie linii z drugiego obiektu Textures
        self.screen_thread.element_menu_name = element_menu_name
        self.screen_opt = opt
        
    def connecting_server(self):
        '''
        Łączenie z serwerem
        '''
        self.screen_thread.connecting = True

        if self.onlineServer.connected:
            self.screen_thread.test = "d"
        else:
            self.onlineServer.connect_with_serwer()
            self.screen_thread.test = "T"
            
        self.screen_thread.connecting = False
        
        
    def button_click_audio(self, name):
        '''
        Sprawdzanie czy głośnośc nie jest 0
        Jeżeli nie jest otwarza dźwięk
        
        Parametry:
            name (str):
                Nazwa pliku audio do otworzenia
        '''
        if self.audio_level["MASTER"]>0 and self.audio_level["INPUTS"]>0:
            self.audio.audio_play(name,0)

    def user_input_menu(self):
        '''
        Obsługa reakcji działania na obsługę klawiszy w Menu
        Jeżeli okno nie jest aktywne bądź zbyt małe nie obsługuję klawiszy
        '''
        try:
            if gw.getActiveWindow().title != "CHRONOMYSTICA" or self.screen_thread.ZaMalyEkran:
                return
        except AttributeError:
            pass
        current_time = time.time()

        up_keys = self.keyboard.get_assigned_keys("UP")
        down_keys = self.keyboard.get_assigned_keys("DOWN")
        enter_keys = self.keyboard.get_assigned_keys("ENTER")
        quit_keys = self.keyboard.get_assigned_keys("QUIT")
        # Obsługa klawisza "UP"
        if any(self.keyboard.is_key_pressed(key) for key in up_keys):
            if current_time - self.last_up_press_time > self.key_repeat_delay:
                if self.screen_thread.options > 1 and not self.screen_thread.KeyboardOPT:
                    self.button_click_audio("button")
                    self.screen_thread.options -= 1
                elif self.screen_thread.KeyboardOPT:
                    if self.screen_thread.options == len(self.screen_thread.element_menu_name)+3:
                        self.button_click_audio("button")
                        self.screen_thread.options -= 3
                    elif self.screen_thread.options > 1:
                        self.button_click_audio("button")
                        self.screen_thread.options -= 1
                self.last_up_press_time = current_time
        else:
            self.last_up_press_time = 0  # Reset, jeśli klawisz nie jest wciśnięty

        # Obsługa klawisza "DOWN"
        if any(self.keyboard.is_key_pressed(key) for key in down_keys):
            if current_time - self.last_down_press_time > self.key_repeat_delay:
                if self.screen_thread.options < len(self.screen_thread.element_menu_name):
                    self.button_click_audio("button")
                    self.screen_thread.options += 1
                elif self.screen_thread.KeyboardOPT:
                    if self.screen_thread.options == len(self.screen_thread.element_menu_name):
                        self.button_click_audio("button")
                        self.screen_thread.options += 3
                    elif self.screen_thread.options < len(self.screen_thread.element_menu_name)+4:
                        self.button_click_audio("button")
                        self.screen_thread.options += 1
                self.last_down_press_time = current_time
        else:
            self.last_down_press_time = 0  # Reset, jeśli klawisz nie jest wciśnięty

        # Obsługa klawisza "ENTER"
        if any(self.keyboard.is_key_pressed(key) for key in enter_keys):
            if current_time - self.last_enter_press_time > self.key_repeat_delay:
                # Okno Menu Główne
                if self.screen_opt == 1:
                    # Przycisk Startu
                    if self.screen_thread.options == 1:
                        self.screen_opener(7,["SINGLEPLAYER", "MULTIPLAYER", "BACK"],3,False)
                    # Przycisk Ustawień
                    elif self.screen_thread.options == 2:
                        self.screen_opener(1,["GRAPHICS", "CONTROLS", "AUDIO", "BACK"],2,False)
                    # Przycisk Wyłączenia
                    elif self.screen_thread.options == 3:
                        self.running = False
                # Okno Ustawień
                elif self.screen_opt == 2:
                    # Przycisk Opcji Grafiki
                    if self.screen_thread.options == 1:
                        self.screen_opener(2,[f"QUALITY [{self.quality_map.get(self.quality, '')}]", f"FPS LIMIT [{'*' if self.limitetFPS == True else ' '}]", "BACK"],21,False)
                    # Przycisk Opcji Sterowania
                    elif self.screen_thread.options == 2:
                        self.screen_opener(4,["KEYBOARD", f"ADVANCED CONTROL [{'*' if self.advanced_control == True else ' '}]", "BACK"],22,False)
                    # Przycisk Opcji Audio
                    elif self.screen_thread.options == 3:
                        self.screen_thread.AudioOPT = True
                        self.screen_opener(6,["MASTER", "MUSIC", "GAME", "INPUTS", "BACK"],23,False) #Napisać wyświetlanie w game_screen_srart oraz class audio_opener 
                    # Przycisk Powrotu
                    elif self.screen_thread.options == 4:
                        self.screen_opener(0,["START", "OPTIONS", "QUIT"],1,True)
                # Okno Ustawień Grafiki
                elif self.screen_opt == 21:
                    # Przycisk Opcji Grafiki Jakości
                    if self.screen_thread.options == 1:
                        self.screen_opener(3,["HIGH", "MEDIUM", "LOW"],211,False)
                    # Przycisk Opcji Grafiki LimituFPS      SWITCH
                    elif self.screen_thread.options == 2:
                        self.limitetFPS = self.off_on_switch(self.limitetFPS)
                        self.screen_thread.element_menu_name[1] = f"FPS LIMIT [{'*' if self.limitetFPS == True else ' '}]"
                        self.settings_r.save_config(self.limitetFPS, self.SHOW_FPS, self.quality, self.advanced_control, self.audio_level)
                    # Przycisk Powrotu
                    elif self.screen_thread.options == 3:
                        self.screen_opener(1,["GRAPHICS", "CONTROLS", "AUDIO", "BACK"],2,True)
                # Okno Ustawień Grafiki Jakości
                elif self.screen_opt == 211:
                    # Przycisk Opcji Grafiki Jakości Wysoki
                    if self.screen_thread.options == 1:
                        self.quality = 3
                        self.settings_r.save_config(self.limitetFPS, self.SHOW_FPS, self.quality, self.advanced_control, self.audio_level)
                    # Przycisk Opcji Grafiki Jakości Średni
                    elif self.screen_thread.options == 2:
                        self.quality = 2
                        self.settings_r.save_config(self.limitetFPS, self.SHOW_FPS, self.quality, self.advanced_control, self.audio_level)
                    # Przycisk Opcji Grafiki Jakości Niski
                    elif self.screen_thread.options == 3:
                        self.quality = 1
                        self.settings_r.save_config(self.limitetFPS, self.SHOW_FPS, self.quality, self.advanced_control, self.audio_level)
                    self.screen_opener(2,[f"QUALITY [{self.quality_map.get(self.quality, '')}]", f"FPS LIMIT [{'*' if self.limitetFPS == True else ' '}]", "BACK"],21,True)
                # Okno Ustawień Sterowania
                elif self.screen_opt == 22:
                    # Przycisk Opcji Sterowania Przypisanych_Klawiszy
                    if self.screen_thread.options == 1:
                        self.screen_thread.KeyboardOPT = True
                        self.screen_opener(5,self.format_key_bindings(),221,False)
                    # Przycisk Opcji Sterowania Zaawansowanych_Ustawień_Klawiszy    SWITCH
                    elif self.screen_thread.options == 2:
                        self.advanced_control = self.off_on_switch(self.advanced_control)
                        self.screen_thread.element_menu_name[1] = f"ADVANCED CONTROL [{'*' if self.advanced_control == True else ' '}]"
                        self.settings_r.save_config(self.limitetFPS, self.SHOW_FPS, self.quality, self.advanced_control, self.audio_level)
                    # Przycisk Powrotu
                    elif self.screen_thread.options == 3:
                        self.screen_opener(1,["GRAPHICS", "CONTROLS", "AUDIO", "BACK"],2,True)
                # Okno Ustawień Sterowania Przypisanych_Klawiszy
                elif self.screen_opt == 221:
                    temp = self.format_key_bindings()
                    # Przycisk Opcji Sterowania Przypisanych_Klawiszy Przypisywanie
                    if 1 <= self.screen_thread.options <= len(temp):
                        self.screen_thread.first_and_last_key = self.set_first_and_last_key(temp[self.screen_thread.options - 1])
                        self.screen_thread.CheckingKeyboard = True
                        threading.Thread(target=self.data_button_colector, daemon=True).start()
                    # Przycisk Opcji Sterowania Przypisanych_Klawiszy Zapisywanie
                    elif self.screen_thread.options == len(temp)+3:
                        self.keyboard.key_list = self.temp_keys
                        self.keyboard.save_config()
                        self.screen_thread.KeyboardOPT = False
                        self.screen_opener(4,["KEYBOARD", f"ADVANCED CONTROL [{'*' if self.advanced_control == True else ' '}]", "BACK"],22,True)
                    # Przycisk Opcji Sterowania Przypisanych_Klawiszy Odrzucanie
                    elif self.screen_thread.options == len(temp)+4:
                        self.temp_keys = self.keyboard.key_list.copy()
                        self.screen_thread.KeyboardOPT = False
                        self.screen_opener(4,["KEYBOARD", f"ADVANCED CONTROL [{'*' if self.advanced_control == True else ' '}]", "BACK"],22,True)
                # Okno Ustawień Audio
                elif self.screen_opt == 23:
                    # Przycisk Opcji Audio Ustawiania_Master
                    if self.screen_thread.options == 1:
                        threading.Thread(target=self.user_input_audio, args=("MASTER",), daemon=True).start()
                    # Przycisk Opcji Audio Ustawiania_Music
                    elif self.screen_thread.options == 2:
                        threading.Thread(target=self.user_input_audio, args=("MUSIC",), daemon=True).start()
                    # Przycisk Opcji Audio Ustawiania_Game
                    elif self.screen_thread.options == 3:
                        threading.Thread(target=self.user_input_audio, args=("GAME",), daemon=True).start()
                    # Przycisk Opcji Audio Ustawiania_Inputs
                    elif self.screen_thread.options == 4:
                        threading.Thread(target=self.user_input_audio, args=("INPUTS",), daemon=True).start()
                    # Przycisk Powrotu
                    elif self.screen_thread.options == 5:
                        self.screen_thread.AudioOPT = False
                        self.screen_opener(1,["GRAPHICS", "CONTROLS", "AUDIO", "BACK"],2,True)
                # Okno Graj
                elif self.screen_opt == 3:
                    if self.screen_thread.options == 1:
                        pass
                    elif self.screen_thread.options == 2:
                        threading.Thread(target=self.connecting_server, daemon=True).start()
                    elif self.screen_thread.options == 3:
                        self.screen_opener(0,["START", "OPTIONS", "QUIT"],1, True)                          
                self.last_enter_press_time = current_time
        else:
            self.last_enter_press_time = 0  # Reset, jeśli klawisz nie jest wciśnięty
            

        if any(self.keyboard.is_key_pressed(key) for key in quit_keys):
            if current_time - self.last_quit_press_time > self.key_repeat_delay:
                if self.screen_opt == 1:
                    self.running = False
                elif 2<=self.screen_opt<=3:  
                    self.screen_opener(0,["START", "OPTIONS", "QUIT"],1, True)
                elif 21<=self.screen_opt<=22:
                    self.screen_opener(1,["GRAPHICS", "CONTROLS", "AUDIO", "BACK"],2,True)
                elif self.screen_opt == 23:
                    self.screen_thread.AudioOPT = False
                    self.screen_opener(1,["GRAPHICS", "CONTROLS", "AUDIO", "BACK"],2,True)
                elif self.screen_opt == 211:
                    self.screen_opener(2,[f"QUALITY [{self.quality_map.get(self.quality, '')}]", f"FPS LIMIT [{'*' if self.limitetFPS == True else ' '}]", "BACK"],21, True)
                elif self.screen_opt == 221:
                    self.temp_keys = self.keyboard.key_list.copy()
                    self.screen_thread.KeyboardOPT = False
                    self.screen_opener(4,["KEYBOARD", f"ADVANCED CONTROL [{'*' if self.advanced_control == True else ' '}]", "BACK"],22,True)
                self.last_quit_press_time = current_time
        else:
            self.last_quit_press_time = 0  # Reset, jeśli klawisz nie jest wciśnięty
            

        
    def user_input_audio(self, name):
        '''
        Obsługa klawiszy do pogłośnienia i przyciszenia audio w ustawienia audio
        
        Parametry:
            name(str):
                Nazwa kontrolki audio dla jakiej ma być zmieniona głośność
        '''
        self.CheckingAudio = True

        volume_lvl = self.audio_level[name]

        while True:
            key_get = self.keyboard.user_input_getKeybord()

            left_keys = self.keyboard.get_assigned_keys("CONTROL_LEFT")
            right_keys = self.keyboard.get_assigned_keys("CONTROL_RIGHT")
            enter_keys = self.keyboard.get_assigned_keys("ENTER")
            quit_keys = self.keyboard.get_assigned_keys("QUIT")

            if any(key_get == key for key in left_keys):
                if self.audio_level[name] > 0:
                    self.audio_level[name] -= 1
            if any(key_get == key for key in right_keys):
                if self.audio_level[name] < 10:
                    self.audio_level[name] += 1
            if any(key_get == key for key in enter_keys):
                break
            if any(key_get == key for key in quit_keys):
                self.audio_level[name] = volume_lvl
                break

        self.audio.set_audio_list([0],[self.audio_level["INPUTS"]*self.audio_level["MASTER"]/100])
        self.settings_r.save_config(self.limitetFPS, self.SHOW_FPS, self.quality, self.advanced_control, self.audio_level)
        time.sleep(0.5)
        self.CheckingAudio = False


    def position(self, direction):
        pass
        #self.screen.addstr(0, 0, ''.join(direction))

    def start(self):
        '''
        Główna Pętla Gry
        Obsługująca Aktualizacje i Odświerzanie na sekunde
        Działa póki self.running = True
        '''
        time_per_frame = 1.0 / self.FPS_SET
        time_per_update = 1.0 / self.UPS_SET

        previous_time = time.time()
        deltaU = 0
        deltaF = 0

        frames = 0
        updates = 0
        last_check = time.time()

        while self.running:
            current_time = time.time()

            deltaU += (current_time - previous_time) / time_per_update
            deltaF += (current_time - previous_time) / time_per_frame
            previous_time = current_time

            if deltaU >= 1:
                if self.screen_opt == 0:
                    self.user_input()
                elif not self.screen_thread.CheckingKeyboard and not self.CheckingAudio:
                    self.user_input_menu()
                updates += 1
                deltaU -= 1

            if deltaF >= 1:
                self.update()
                frames += 1
                deltaF -= 1
            elif not self.limitetFPS:
                self.update()
                frames += 1

            if self.SHOW_FPS and (time.time() - last_check >= 1):
                last_check = time.time()
                self.fps = frames
                frames = 0
                updates = 0
        self.onlineServer.monitor_heart = False
                    


    def update(self):
        '''
        Odświerzanie ekranu
        Wywołuję funckje renderowania
        '''
        if self.resized or self.screen_thread.screen.getch() == curses.KEY_RESIZE:
            self.screen_thread.resize()
            self.resized = False
        self.screen_thread.test = int(self.onlineServer.ping)
        self.screen_thread.update(round(self.fps, 1))
