import numpy as np


class Mapa:
    def __init__(self, mapa):
        # Load map
        self._mapa = np.array([list(map(int, line)) for line in mapa.splitlines()]).T