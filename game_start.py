import curses
from reader_files import Textures
from controll_script import Control

def curses_init(screen):
    curses.curs_set(0)
    curses.init_color(2, 38, 230, 0)
    curses.init_pair(1, 2, curses.COLOR_BLACK)  # Ściany
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Smok
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Czerwonyc
    screen.nodelay(True)

def main(screen):
    curses_init(screen)
    textures_names = ["LOGO", "LOGO_MIN"]
    texture = [Textures(name_textures) for name_textures in textures_names]
    Control(screen, texture).start()
    curses.flushinp()
    curses.endwin()
    
if __name__ == "__main__":
    curses.wrapper(main)
