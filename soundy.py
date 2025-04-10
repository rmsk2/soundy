#! /usr/bin/env python3


import sys
import os
import time
import pathlib
from pygame import mixer
import pygame
import cardy
import playlist
import soundy_ui
from soundyconsts import *
import uidfactory


STATE_IDLE = 0
STATE_PLAYING = 1

NO_SONG = -1

class SoundyPlayer:
    def __init__(self, ui, event_insert, event_remove, event_music_end, event_function, event_playing, event_pause, event_list_end, ui_stopped, err_generic):
        self.insert = event_insert
        self.remove = event_remove
        self.play_end = event_music_end
        self.function_event = event_function
        self.play_start_event = event_playing
        self.event_pause = event_pause
        self.event_list_end = event_list_end
        self.event_ui_stopped = ui_stopped
        self.state = STATE_IDLE
        self.playing_id = NO_SONG
        self.perform_function = None
        self._end_program = False
        self.event_err_gen = err_generic
        self.ui = ui

        c = ui.ui_config["ids"]
        self.card_id_rewind = c["rewind"]
        self.card_id_restart = c["restart"]
        self.card_id_end = c["end"]
        self.card_id_skip = c["skip"]
        self.card_id_prev = c["prev"]
        self.titles = {}

    def load_playlists(self, config_dir):
        try:
            all_files = []
            for file in os.listdir(config_dir):
                if file.endswith(".json"):
                    all_files.append(os.path.join(config_dir, file))

            titles_raw = list(map(playlist.PlayList.from_json, all_files))
        except:
            print(ERR_MSG_LOAD_PLAYLIST)
            sys.exit(42)

        self.titles = {}
        for i in titles_raw:
            self.titles[i.card_id] = i

    @staticmethod
    def prep_function_execution(f, ctx):
        def prepper(x):
            f(x)
            return ctx

        return prepper

    @property
    def end_program(self):
        return self._end_program

    def handle_insert_event(self, event):
        if self.state != STATE_IDLE:
            return
        
        if event.card_id == self.card_id_rewind:
            self.perform_function = SoundyPlayer.prep_function_execution(lambda x: x.reset(), FUNC_PLAYLIST_RESTART)
            pygame.event.post(pygame.event.Event(self.function_event, kind=FUNC_PLAYLIST_RESTART, ctx=None))            
        elif event.card_id == self.card_id_restart:
            self.perform_function = SoundyPlayer.prep_function_execution(lambda x: x.reset_play_time(), FUNC_SONG_RESTART)
            pygame.event.post(pygame.event.Event(self.function_event, kind=FUNC_SONG_RESTART, ctx=None))
        elif event.card_id == self.card_id_skip:
            self.perform_function = SoundyPlayer.prep_function_execution(lambda x: x.skip_song(), FUNC_SONG_SKIP)
            pygame.event.post(pygame.event.Event(self.function_event, kind=FUNC_SONG_SKIP, ctx=None))
        elif event.card_id == self.card_id_prev:
            self.perform_function = SoundyPlayer.prep_function_execution(lambda x: x.prev_song(), FUNC_SONG_PREV)
            pygame.event.post(pygame.event.Event(self.function_event, kind=FUNC_SONG_PREV, ctx=None))
        elif event.card_id == self.card_id_end:
            pygame.event.post(pygame.event.Event(self.function_event, kind=FUNC_END, ctx=None))
        else:
            if not event.card_id in self.titles.keys():
                return

            pl = self.titles[event.card_id]
            restore_play_time = pl.get_play_time()
            restore_title = pl.get_current_song_num()

            try:
                if self.perform_function != None:
                    context = self.perform_function(self.titles[event.card_id])
                    pygame.event.post(pygame.event.Event(self.function_event, kind=FUNC_PERFORMED, ctx=context))
                    self.perform_function = None

                if not pathlib.Path(pl.current_song()).exists():
                    raise Exception("File does not exist")

                mixer.music.load(pl.current_song())
                start_pos = pl.get_play_time()

                mixer.music.play(start = start_pos)
                self.playing_id = event.card_id
                self.state = STATE_PLAYING
                pygame.event.post(pygame.event.Event(self.play_start_event, play_list_name=pl.play_list_name(), song=pl.get_current_song_num()+1, num_songs=pl.num_songs(), beep=event.beep))
            except Exception as e:
                pygame.event.post(pygame.event.Event(self.event_err_gen, err_type=ERR_TYPE_FILE, err_msg=str(e)))
                pl.set_play_time(restore_play_time)
                pl.set_current_song_num(restore_title)

    def handle_remove_event(self, event):
        if self.state != STATE_PLAYING:
            return

        if event.card_id != self.playing_id:
            return
        
        self.titles[self.playing_id].increase_play_time(mixer.music.get_pos() / 1000.0)
        self.playing_id = NO_SONG
        self.state = STATE_IDLE
        mixer.music.stop()
        pygame.event.post(pygame.event.Event(self.event_pause))

    def handle_song_end(self):
        if self.state != STATE_PLAYING:
            return

        playlist_end = self.titles[self.playing_id].next_song()
        if playlist_end:
            self.titles[self.playing_id].reset()
            self.playing_id = NO_SONG
            self.state = STATE_IDLE
            pygame.event.post(pygame.event.Event(self.event_list_end))
            return
        
        h = self.playing_id
        self.playing_id = NO_SONG
        self.state = STATE_IDLE
        pygame.event.post(pygame.event.Event(self.insert, card_id=h, beep=False))

    def work_event_queue(self):
        event = pygame.event.wait()
        if event.type == self.insert:
            self.handle_insert_event(event)
        elif event.type == self.remove:
            self.handle_remove_event(event)
        elif event.type == self.play_end:
            self.handle_song_end()
        elif event.type == self.event_err_gen:
            self.ui.handle_error(event.err_type, event.err_msg)
        elif event.type == self.function_event:
            self.ui.handle_function_event(event)
        elif event.type == self.play_start_event:
            self.ui.handle_play_start(event)
        elif event.type == self.event_pause:
            self.ui.handle_pause()
        elif event.type == self.event_list_end:
            self.ui.handle_list_end()
        elif event.type == self.event_ui_stopped:
            self._end_program = True


def init_reader(wait_time):
    sys.stdout.write("Waiting for reader ... ")
    sys.stdout.flush()

    time.sleep(wait_time)

    print("done")

def print_logger(msg):
    print(msg)

def main():
    # Last parameter is buffer size. Maybe increase it further if sound starts to lag
    mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    mixer.init()
    os.system(CLEAR_COMMAND)

    event_insert = pygame.event.custom_type()
    event_remove = pygame.event.custom_type()
    event_music_end = pygame.event.custom_type()
    event_function = pygame.event.custom_type()
    event_playing = pygame.event.custom_type()
    event_pause = pygame.event.custom_type()
    event_list_end = pygame.event.custom_type()
    event_ui_stopped = pygame.event.custom_type()
    event_err_generic = pygame.event.custom_type()
    pygame.mixer.music.set_endevent(event_music_end)

    config_dir ="./"
    if len(sys.argv) > 1:
        config_dir = sys.argv[1]

    ui = soundy_ui.SoundyUI(event_ui_stopped)
    ui.load_config(config_dir)
    #ui.logger = print_logger

    player = SoundyPlayer(ui, event_insert, event_remove, event_music_end, event_function, event_playing, event_pause, event_list_end, event_ui_stopped, event_err_generic)
    player.load_playlists(config_dir)

    card_manager = cardy.CardManager(ALL_ATRS, uidfactory.UidReaderRepo(), event_insert, event_remove, event_err_generic)
    card_manager.start()

    init_reader(ui.ui_config["wait_reader_sec"])

    try:
        # empty event queue, i.e. initial card errors
        to_ignore = pygame.event.get()
        ui.start()

        while not player.end_program:
            player.work_event_queue()
            ui.redraw()
            pygame.display.update()
    except KeyboardInterrupt:
        pass
    finally:
        card_manager.destroy()
        pygame.quit()

if __name__ == "__main__":
    main()    
