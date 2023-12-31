import curses
import os

import numpy as np

from mapa_loader import Mapa
from players import Me_Player


class GamePlay:
    
    
    def __init__(self, screen, quality, data_player):
        self.screen = screen
        self.data_player = data_player
        self.game_map = Mapa(self.data_player["map"])._mapa
        # Initialize Me_Player with a starting position and direction
        start_position = [5, 5]  # Example starting position
        start_direction = [1, 0]  # Example starting direction (facing right)
        self.me_player = Me_Player(start_position, start_direction)
        self.ascii_render = self.ascii_render(quality)
        self.shades = len(self.ascii_render) - 1
        self.resize()                                                              # Inicjacja ustalenia miejsca w oknie

    def ascii_render(self, quality):
        if quality == 1:
            return np.array(list(' .:|#░▒▓█'))
        elif quality == 2:
            return np.array(list(' .:|#░▒▓█'))
        elif quality == 3:
            return np.array(list(' .:|#░▒▓█'))

    def resize(self):
        try: # linux
            w, h = os.get_terminal_size()
            curses.resizeterm(h, w)
        except: # windows
            h, w = self.screen.getmaxyx()

        w -= 1
        self.height = h
        self.width = w
        self.angle_increment = 1 / w
        self.floor = h // 2
        self.distances = np.zeros(w)
        self.buffer = [[(" ", None) for _ in range(w)] for _ in range(h)]
        
    def terrain(self, max_depth=20):
        for column in range(self.width):
            angle = (column / self.width - 0.5) * self.me_player.field_of_view
            ray_angle = self.me_player.direction + angle

            # Normalize the ray direction for consistent wall heights
            ray_direction = ray_angle / np.linalg.norm(ray_angle)

            # Cast the ray and find where it hits a wall
            for depth in range(1, max_depth):
                ray_position = self.me_player.position + ray_direction * depth
                x, y = int(ray_position[0]), int(ray_position[1])

                if 0 <= x < self.game_map.shape[0] and 0 <= y < self.game_map.shape[1]:
                    if self.game_map[x][y] == 1:
                        # Apply distance correction for the fisheye effect
                        corrected_distance = depth * np.cos(angle)
                        wall_height = self.height / corrected_distance

                        # Determine start and end points for the wall slice in the buffer
                        start = int((self.height - wall_height) / 2)
                        end = int((self.height + wall_height) / 2)

                        # Determine the shade of the wall slice based on distance
                        shade = min(int(wall_height * self.shades / self.height), self.shades)
                        char = self.ascii_render[shade]

                        # Update the buffer with the wall slice
                        for y in range(start, end):
                            if 0 <= y < self.height:
                                self.buffer[y][column] = (char, 3)  # Color 3 for the wall
                        break
                else:
                    # Handle the case where ray_position is outside the game map
                    pass  # You might want to break or continue based on your game logic
                
    def draw_mini_map(self):
    # Define the size of the mini-map
        mini_map_size = 10
        top_left_x = self.me_player.position[0] - mini_map_size // 2
        top_left_y = self.me_player.position[1] - mini_map_size // 2

        # Draw the mini-map
        for x in range(mini_map_size):
            for y in range(mini_map_size):
                map_x = int(top_left_x + x)
                map_y = int(top_left_y + y)

                # Check if we are out of the bounds of the main map
                if 0 <= map_x < self.game_map.shape[0] and 0 <= map_y < self.game_map.shape[1]:
                    # Check if the current position is a wall
                    if self.game_map[map_x][map_y] == 1:
                        mini_map_char = '#'
                    else:
                        mini_map_char = '.'
                else:
                    mini_map_char = ' '

                # Check if we are at the player's position
                if map_x == int(self.me_player.position[0]) and map_y == int(self.me_player.position[1]):
                    mini_map_char = 'P'

                # Add the mini-map character to the buffer
                # Adjust the position of the mini-map on the screen as needed
                self.buffer[y + 1][x + self.width - mini_map_size - 1] = (mini_map_char, 2)

        
    def update(self, fps):
        for y, row in enumerate(self.buffer):
            for x in range(len(row)):
                row[x] = (" ", None)

        # Draw floor (example color 1)
        for x in range(0, self.width, 1):
            for y in range(self.floor, self.height, 1):
                self.buffer[y][x] = (" ", 1)

        # Draw walls (example color 2)'''
        try:
            self.terrain()
        except Exception as e:
            print(e)

        self.draw_mini_map()
        # Draw sprites (example color 3)

        for x, char in enumerate(str(fps)):
            self.buffer[0][x] = (char, 4)
        

        
        for row_num, row in enumerate(self.buffer):
            i=0
            for char, color in row:
                if color is not None:
                    self.screen.addstr(row_num, i, char, curses.color_pair(color))
                else:
                    self.screen.addstr(row_num, i, char, curses.color_pair(3))
                i+=1
        self.screen.refresh() 