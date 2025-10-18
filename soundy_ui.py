import os
import json
import pygame
import soundy
from soundyconsts import *


class SoundyUI:
    def __init__(self, event_ui_stopped):
        self.stopped_event = event_ui_stopped
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.blue = (0, 0, 255)
        self._x_size = 800
        self._y_size = 600
        self._text = all_messages[STD_MSG]
        self._func_text = EMPTY_STR
        self._background_col = self.white
        self._font_size = 48
        self._func_font_size = 32
        self._logger = self.err_logger

        self._err_map = {
            ERR_TYPE_COMM: self.red,
            ERR_TYPE_FILE: self.blue
        }

    def load_config(self, config_dir):
        try:
            with(open(os.path.join(config_dir, "ui_config"), "r") as f):
                all_data = json.load(f)
        except:
            print(all_messages[ERR_MSG_LOAD_CONFIG])
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
    def logger(self):
        return self._logger
    
    @logger.setter
    def logger(self, val):
        self._logger = val

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
        pygame.display.set_caption(all_messages[CAPTION_DEFAULT])
        self._font = pygame.font.Font('freesansbold.ttf', self._font_size)
        self._func_font = pygame.font.Font('freesansbold.ttf', self._func_font_size)

    def err_logger(self, msg):
        self.sound_bell()

    def sound_bell(self):
        sound = pygame.mixer.Sound(self._sound_error)
        sound.play()

    def handle_error(self, err_type, err_msg):
        self._logger(err_msg)
        h = self._text
        b = self._background_col

        self._background_col = self._err_map[err_type]
        self.redraw()
        pygame.display.update()
        pygame.time.wait(175)

        self._text = h
        self._background_col = b
        self.redraw()        

    def handle_play_start(self, event):
        if event.beep:
            self.sound_bell()

        self._text = all_messages[MSG_PLAY_FORMAT_STR].format(song=event.song, num_songs=event.num_songs)
        pygame.display.set_caption(event.play_list_name)

    def handle_pause(self):
        pygame.display.set_caption(all_messages[CAPTION_DEFAULT])
        self._text = all_messages[STD_MSG]

    def handle_list_end(self):
        pygame.display.set_caption(all_messages[CAPTION_DEFAULT])
        self._text = all_messages[STD_MSG]

    def handle_function_event(self, event):
        self.sound_bell()
        if event.kind == soundy.FUNC_END:
            pygame.time.wait(200)
            pygame.event.post(pygame.event.Event(self.stopped_event))
        elif event.kind == FUNC_PLAYLIST_RESTART:
            self._func_text = all_messages[MSG_PLAYLIST_BEGINING]
        elif event.kind == FUNC_SONG_RESTART:
            self._func_text =  all_messages[MSG_RESTART_SONG]
        elif event.kind == FUNC_SONG_SKIP:
            self._func_text =  all_messages[MSG_SKIP_SONG]
        elif event.kind == FUNC_SONG_PREV:
            self._func_text = all_messages[MSG_NEXT_SONG]
        elif event.kind == FUNC_PERFORMED:
            self._func_text = EMPTY_STR
