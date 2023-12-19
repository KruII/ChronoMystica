import curses
import os
from reader_files import Textures
from controll_script import Control

def curses_init(screen):
    '''
    Inicjacja curses
    
    Parametry:
        screen:
            Ekran
    '''
    curses.curs_set(0)
    curses.init_color(2, 38, 230, 0)
    curses.init_pair(1, curses.COLOR_BLACK, 2,)                             # Menu: Aktualny Element
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)               # Menu: Wersja
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)             # Menu: Domyślny
    screen.nodelay(True)

def main(screen):
    '''
    Głowna funkcja odpowiadająca za wywołanie funcji startowych
    
    Parametry:
        screen:
            Ekran
    '''
    curses_init(screen)
    textures_names = ["LOGO", "LOGO_MIN",                                   # 0     LOGO
                      "OPTIONS_LOGO", "OPTIONS_LOGO_MIN",                   # 1     OPTIONS
                      "GRAPHICS_LOGO", "GRAPHICS_LOGO_MIN",                 # 2     GRAPHICS
                      "QUALITY_LOGO", "QUALITY_LOGO_MIN",                   # 3     QUALITY
                      "CONTROLS_LOGO", "CONTROLS_LOGO_MIN",                 # 4     CONTROLS
                      "KEYBOARD_LOGO", "KEYBOARD_LOGO_MIN",                 # 5     KEYBOARD
                      "AUDIO_LOGO", "AUDIO_LOGO_MIN",                       # 6     AUDIO            
                      "GAMEMODE_LOGO", "GAMEMODE_LOGO_MIN",                 # 7     GAMEMODE
                      ]                 
    texture = [Textures(name_textures) for name_textures in textures_names]
    Control(screen, texture).start()
    curses.flushinp()
    curses.endwin()
    
if __name__ == "__main__":
    '''
    START
    '''
    os.system(f'echo -ne "\033]0;CHRONOMYSTICA\007"')
    curses.wrapper(main)
