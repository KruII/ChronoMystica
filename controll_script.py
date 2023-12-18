import curses
import signal
import threading
import time
import pygetwindow as gw
from game_screen_start import GameStartScreen
from keybord_action import Keyboard

class Control:
    
    running = True                  # IF FALSE GAME STOP
    resized = False                 # RESIZE SCREEN
    FPS_SET = 60                    # MAX FRAME PER SECOND
    UPS_SET = 120                   # MAX UPDATES PER SECOND
    
    def __init__(self, screen, texture):
        self.screen = screen
        self.texture = texture
        self.screen_thread = GameStartScreen(self.screen, self.texture)
        self.keyboard = Keyboard()
        self.screen_opt = 1
        self.fps = 0
        self.limitetFPS = True
        self.SHOW_FPS = True
        self.quality = 3
        self.quality_map = {3: 'H', 2: 'M', 1: 'L'}
        self.advanced_control = False
        self.last_up_press_time = 0
        self.last_down_press_time = 0
        self.last_enter_press_time = 0
        self.last_quit_press_time = 0
        self.key_repeat_delay = 0.5  # Opóźnienie między kolejnymi ruchami przy przytrzymanym klawiszu
        self.temp_keys = self.keyboard.key_list.copy()
        self.przedrotki = []
 
        try: # Fails on windows
            signal.signal(signal.SIGWINCH, self.resize) # Our solution to curses resize bug
        except:
            pass

    def resize(self, *args):
        self.resized = True
        
    def format_key_binding(self, key):
        """Formatuje pojedynczy klawisz zgodnie z mapowaniem KEYS_MAP."""
        if key is None:
            return " "
        elif key in self.keyboard.KEYS_MAP:
            return self.keyboard.KEYS_MAP[key]
        elif key.startswith("'") and key.endswith("'"):
            return key.strip("'").upper()
        return key

    def format_key_bindings(self):
        """Tworzy sformatowane ciągi dla przypisanych klawiszy."""
        formatted_bindings = []
        self.przedrotki = []
        for action, keys in self.temp_keys.items():
            action_prefix = action[0]+action[1]  # Pierwszy znak nazwy akcji
            if action_prefix in ['O_', 'A_', 'S_']:
                if (self.advanced_control and action_prefix == 'A_') or (not self.advanced_control and action_prefix == 'S_') or action_prefix == 'O_':
                    formatted_keys = [self.format_key_binding(key) for key in keys]
                    formatted_binding = f"{action[2:]}: [ {' | '.join(formatted_keys)} ]"  # Usuwamy przedrostek z nazwy akcji
                    self.przedrotki.append(action)
                    formatted_bindings.append(formatted_binding)
        return formatted_bindings

    def set_first_and_last_key(self, line):
        """
        Ustawia pierwszy i ostatni klawisz na podstawie danej linii.

        Parametry:
        line (str): Linia tekstu z przypisanymi klawiszami.
        """
        action, bindings = line.split(":")  # Rozdziela nazwę akcji od przypisanych klawiszy
        bindings = bindings.strip(" []").split(" | ")  # Usuwa zbędne spacje i znaki specjalne

        # Dodaj "NONE" jako drugi element, jeśli w bindings jest tylko jeden element
        if len(bindings) == 1:
            bindings[0] = bindings[0][:-2]
            bindings.append("NONE")

        # Przypisanie wartości do first_and_last_key
        return [b.strip() if b.strip() != "" else "NONE" for b in bindings]

    def data_button_colector(self):
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
        if opt_his:
            self.screen_thread.options = int(self.screen_thread.option_history[len(self.screen_thread.option_history)-1])
            self.screen_thread.option_history = self.screen_thread.option_history[:-1]
        else:
            self.screen_thread.option_history += str(self.screen_thread.options)
            self.screen_thread.options = 1
        self.screen_thread.logo = self.texture[logo*2].lines  # Przypisanie linii z pierwszego obiektu Textures
        self.screen_thread.mini_logo = self.texture[logo*2+1].lines  # Przypisanie linii z drugiego obiektu Textures
        self.screen_thread.element_menu_name = element_menu_name
        self.screen_opt = opt

    def user_input_menu(self):
        try:
            if gw.getActiveWindow().title != "CHRONOMYSTICA":
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
                    self.screen_thread.options -= 1
                elif self.screen_thread.KeyboardOPT:
                    if self.screen_thread.options == len(self.screen_thread.element_menu_name)+3:
                        self.screen_thread.options -= 3
                    elif self.screen_thread.options > 1:
                        self.screen_thread.options -= 1
                self.last_up_press_time = current_time
        else:
            self.last_up_press_time = 0  # Reset, jeśli klawisz nie jest wciśnięty

        # Obsługa klawisza "DOWN"
        if any(self.keyboard.is_key_pressed(key) for key in down_keys):
            if current_time - self.last_down_press_time > self.key_repeat_delay:
                if self.screen_thread.options < len(self.screen_thread.element_menu_name):
                    self.screen_thread.options += 1
                elif self.screen_thread.KeyboardOPT:
                    if self.screen_thread.options == len(self.screen_thread.element_menu_name):
                        self.screen_thread.options += 3
                    elif self.screen_thread.options < len(self.screen_thread.element_menu_name)+4:
                        self.screen_thread.options += 1
                self.last_down_press_time = current_time
        else:
            self.last_down_press_time = 0  # Reset, jeśli klawisz nie jest wciśnięty

        # Obsługa klawisza "ENTER"
        if any(self.keyboard.is_key_pressed(key) for key in enter_keys):
            if current_time - self.last_enter_press_time > self.key_repeat_delay:
                if self.screen_opt == 1:
                    if self.screen_thread.options == 1:
                        pass # screen_opt = 3
                    elif self.screen_thread.options == 2:
                        self.screen_opener(1,["GRAPHICS", "CONTROLS", "AUDIO", "BACK"],2,False)
                    elif self.screen_thread.options == 3:
                        self.running = False
                elif self.screen_opt == 2:
                    if self.screen_thread.options == 1:
                        self.screen_opener(2,[f"QUALITY [{self.quality_map.get(self.quality, '')}]", f"FPS LIMIT [{'*' if self.limitetFPS == True else ' '}]", "BACK"],21,False)
                    elif self.screen_thread.options == 2:
                        self.screen_opener(4,["KEYBOARD", f"ADVANCED CONTROL [{'*' if self.advanced_control == True else ' '}]", "BACK"],22,False)
                    elif self.screen_thread.options == 3:
                        self.screen_opener(6,["MASTER", "MUSIC", "GAME", "INPUTS" "BACK"],23,False) #Napisać wyświetlanie w game_screen_srart oraz class audio_opener 
                    elif self.screen_thread.options == 4:
                        self.screen_opener(0,["START", "OPTIONS", "QUIT"],1,True)
                elif self.screen_opt == 21:
                    if self.screen_thread.options == 1:
                        self.screen_opener(3,["HIGH", "MEDIUM", "LOW"],211,False)
                    elif self.screen_thread.options == 2:
                        if self.limitetFPS == True:
                            self.limitetFPS = False
                        else:
                            self.limitetFPS = True
                        self.screen_thread.element_menu_name[1] = f"FPS LIMIT [{'*' if self.limitetFPS == True else ' '}]"
                    elif self.screen_thread.options == 3:
                        self.screen_opener(1,["GRAPHICS", "CONTROLS", "AUDIO", "BACK"],2,True)
                elif self.screen_opt == 211:
                    if self.screen_thread.options == 1:
                        self.quality = 3
                    elif self.screen_thread.options == 2:
                        self.quality = 2
                    elif self.screen_thread.options == 3:
                        self.quality = 1
                    self.screen_opener(2,[f"QUALITY [{self.quality_map.get(self.quality, '')}]", f"FPS LIMIT [{'*' if self.limitetFPS == True else ' '}]", "BACK"],21,True)
                elif self.screen_opt == 22:
                    if self.screen_thread.options == 1:
                        self.screen_thread.KeyboardOPT = True
                        self.screen_opener(5,self.format_key_bindings(),221,False)
                    elif self.screen_thread.options == 2:
                        if self.advanced_control == True:
                            self.advanced_control = False
                        else:
                            self.advanced_control = True
                        self.screen_thread.element_menu_name[1] = f"ADVANCED CONTROL [{'*' if self.advanced_control == True else ' '}]"
                    elif self.screen_thread.options == 3:
                        self.screen_opener(1,["GRAPHICS", "CONTROLS", "AUDIO", "BACK"],2,True)
                elif self.screen_opt == 221:
                    temp = self.format_key_bindings()
                    if 1 <= self.screen_thread.options <= len(temp):
                        self.screen_thread.first_and_last_key = self.set_first_and_last_key(temp[self.screen_thread.options - 1])
                        self.screen_thread.CheckingKeyboard = True
                        threading.Thread(target=self.data_button_colector).start()
                    elif self.screen_thread.options == len(temp)+3:
                        self.keyboard.key_list = self.temp_keys
                        self.keyboard.save_config()
                        self.screen_thread.KeyboardOPT = False
                        self.screen_opener(4,["KEYBOARD", f"ADVANCED CONTROL [{'*' if self.advanced_control == True else ' '}]", "BACK"],22,True)
                    elif self.screen_thread.options == len(temp)+4:
                        self.temp_keys = self.keyboard.key_list.copy()
                        self.screen_thread.KeyboardOPT = False
                        self.screen_opener(4,["KEYBOARD", f"ADVANCED CONTROL [{'*' if self.advanced_control == True else ' '}]", "BACK"],22,True)
                            
                self.last_enter_press_time = current_time
        else:
            self.last_enter_press_time = 0  # Reset, jeśli klawisz nie jest wciśnięty
            

        if any(self.keyboard.is_key_pressed(key) for key in quit_keys):
            if current_time - self.last_quit_press_time > self.key_repeat_delay:
                if self.screen_opt == 1:
                    self.running = False
                elif 2<=self.screen_opt<=3:  
                    self.screen_opener(0,["START", "OPTIONS", "QUIT"],1, True)
                elif 21<=self.screen_opt<=23:
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
        

    def position(self, direction):
        pass
        #self.screen.addstr(0, 0, ''.join(direction))

    def start(self):
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
                elif not self.screen_thread.CheckingKeyboard:
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
                    


    def update(self):
        if self.resized or self.screen_thread.screen.getch() == curses.KEY_RESIZE: # 2nd check for windows
            self.screen_thread.resize()
            self.resized = False
        self.screen_thread.update(round(self.fps, 1))
