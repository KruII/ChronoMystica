import curses
import signal
import threading
import time
from game_screen_start import GameStartScreen
from keybord_action import Keyboard

class Control:
    
    running = True
    resized = False
    FPS_SET = 60
    UPS_SET = 120
    
    def __init__(self, screen, texture):
        self.screen = screen
        self.texture = texture
        self.screen_thread = GameStartScreen(self.screen, self.texture)
        self.keyboard = Keyboard()
        self.screen_opt = 1
        self.fps = 0
        self.limitetFPS = True
        self.SHOW_FPS = True
 
        try: # Fails on windows
            signal.signal(signal.SIGWINCH, self.resize) # Our solution to curses resize bug
        except:
            pass

    def resize(self, *args):
        self.resized = True

    def user_input(self):
        quit_keys = self.keyboard.get_assigned_keys("QUIT")
        for key in quit_keys:
            if key and self.keyboard.is_key_pressed(key):
                self.running = False
                break

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
                self.user_input()
                updates += 1
                deltaU -= 1

            if deltaF >= 1:
                self.update()
                frames += 1
                deltaF -= 1

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
