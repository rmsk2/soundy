import os
import json
#from pygame import mixer
import pygame
import soundy

EMPTY_STR = '                           '
STD_MSG = "Hallo Erna"

class SoundyUI:
    def __init__(self, event_ui_stopped):
        self.stopped_event = event_ui_stopped
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self._x_size = 800
        self._y_size = 600
        self._text = 'Hallo Erna'
        self._func_text = EMPTY_STR
        self._background_col = self.white
        self._font_size = 48
        self._func_font_size = 32

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

        data = all_data["size"]
        self._x_size = data["x_size"]
        self._y_size = data["y_size"]
        self._font_size = data["font_size1"]
        self._func_font_size = data["font_size2"]

        self._ui_config = all_data

    @property
    def ui_config(self):
        return self._ui_config

    def redraw(self):
        text = self._font.render(self._text, True, self.black, self._background_col)
        text_rect = text.get_rect()
        text_rect.center = (self._x_size // 2, self._y_size // 2)
        self._display_surface.fill(self._background_col)
        self._display_surface.blit(text, text_rect)

        text = self._func_font.render(self._func_text, True, self.black, self._background_col)
        text_rect = text.get_rect()
        text_rect.center = (self._x_size // 2, self._y_size // 4)
        self._display_surface.blit(text, text_rect)

    def start(self):
        self._display_surface = pygame.display.set_mode((self._x_size, self._y_size))
        pygame.display.set_caption("Ernas Hörbuchspieler")
        self._font = pygame.font.Font('freesansbold.ttf', self._font_size)
        self._func_font = pygame.font.Font('freesansbold.ttf', self._func_font_size)

    def sound_bell(self):
        sound = pygame.mixer.Sound(self._sound_error)
        sound.play()

    def handle_card_error(self):
        h = self._text
        b = self._background_col

        self._background_col = self.red
        self.redraw()
        pygame.display.update()
        pygame.time.wait(175)

        self._text = h
        self._background_col = b
        self.redraw()

    def handle_play_start(self, event):
        if event.beep:
            self.sound_bell()

        self ._text = f"Kapitel {event.song + 1} von {event.num_songs}"

    def handle_pause(self):
        self._text = STD_MSG

    def handle_list_end(self):
        self._text = STD_MSG

    def handle_function_event(self, event):
        self.sound_bell()
        if event.kind == soundy.FUNC_END:
            pygame.time.wait(200)
            pygame.event.post(pygame.event.Event(self.stopped_event))
        elif event.kind == soundy.FUNC_PLAYLIST_RESTART:
            self._func_text = "Hörbuch von Anfang an hören"
        elif event.kind == soundy.FUNC_SONG_RESTART:
            self._func_text =  "Zurück zum Anfang des Kapitels"
        elif event.kind == soundy.FUNC_SONG_SKIP:
            self._func_text =  "Zum nächsten Kapitel"
        elif event.kind == soundy.FUNC_SONG_PREV:
            self._func_text = "Zum vorherigen Kapitel"
        elif event.kind == soundy.FUNC_PERFORMED:
            self._func_text = EMPTY_STR
