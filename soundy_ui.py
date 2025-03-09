import os
import json
from pygame import mixer
import pygame
import soundy

class SoundyUI:
    def __init__(self, event_ui_stopped):
        self.stopped_event = event_ui_stopped
        pass

    def load_config(self, config_dir):
        try:
            with(open(os.path.join(config_dir, "ui_config"), "r") as f):
                all_data = json.load(f)
        except:
            print("Kann Konfiguration nicht laden")
            os.exit(42)
        
        data = all_data["sounds"]
        self._sound_info = data["info_sound"]
        self._sound_warning = data["warning_sound"]
        self._sound_error = data["error_sound"]

        self._ui_config = all_data

    @property
    def ui_config(self):
        return self._ui_config

    def sound_bell(self):
        sound = pygame.mixer.Sound(self._sound_error)
        sound.play()

    def handle_card_error(self):
        print("Kartenlesefehler!")

    def handle_play_start(self, event):
        if event.beep:
            self.sound_bell()

        print(f"Kapitel {event.song + 1} von {event.num_songs} in {event.play_list_name}")

    def handle_pause(self):
        print("Pausiert")

    def handle_list_end(self):
        print("Hörbuch zu Ende")

    def handle_function_event(self, event):
        self.sound_bell()
        if event.kind == soundy.FUNC_END:
            print("Beende Programm")
            pygame.time.wait(200)
            pygame.event.post(pygame.event.Event(self.stopped_event))
        elif event.kind == soundy.FUNC_PLAYLIST_RESTART:
            print("Hörbuch von Anfang an hören")
        elif event.kind == soundy.FUNC_SONG_RESTART:
            print("Zurück zum Anfang des Kapitels")
        elif event.kind == soundy.FUNC_SONG_SKIP:
            print("Zum nächsten Kapitel")
        elif event.kind == soundy.FUNC_SONG_PREV:
            print("Zum vorherigen Kapitel")
        elif event.kind == soundy.FUNC_PERFORMED:
            print(f"Sonderfunktion ausgeführt: {event.ctx}")
