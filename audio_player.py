import os
import wave
import numpy as np
import simpleaudio as sa

class Audio:
    
    def __init__(self):
        self.sciezki = ["audio/inputs/", "audio/game/", "audio/music/"]
        self.format = ".wav"
        self.audia = {}

    def set_audio_list(self, numery_audio, volume_scales):
        self.audia = {}  # Resetowanie słownika
        for i, numer in enumerate(numery_audio):
            sciezka = self.sciezki[numer]
            volume_scale = volume_scales[i]
            for plik in os.listdir(sciezka):
                if plik.endswith(self.format):
                    nazwa_audio = os.path.join(sciezka, plik.replace(self.format, ""))
                    pelna_sciezka = os.path.join(sciezka, plik)
                    self.audia[nazwa_audio] = self.change_volume(pelna_sciezka, volume_scale)

    def audio_play(self, audio_name, numer_sciezki):
        audio_name = self.sciezki[numer_sciezki]+audio_name
        try:
            self.audia[audio_name].play()
        except KeyError:
            print(f"Error: Audio '{audio_name}' nie odnaleziona")
        except FileNotFoundError:
            print(f"Error: Plik '{audio_name}' nie istnieje")
            
    def change_volume(self, file_path, volume_scale):
        # Otwórz plik WAV i przeczytaj dane
        with wave.open(file_path, 'rb') as wave_file:
            params = wave_file.getparams()
            frames = wave_file.readframes(params.nframes)
        
        # Konwertuj ramki na tablicę numpy
        audio_data = np.frombuffer(frames, dtype=np.int16)

        # Zmień głośność
        new_audio_data = (audio_data * volume_scale).astype(np.int16)

        # Utwórz nowy obiekt WaveObject z zmodyfikowanymi danymi
        return sa.WaveObject(new_audio_data.tobytes(), params.nchannels, params.sampwidth, params.framerate)

