#! /usr/bin/env python3


import sys
import os
import time
from pygame import mixer
import pygame
import cardy
import playlist
import soundy_ui


ATR_DES_FIRE = "3B 81 80 01 80 80"
ATR_E_PERSO = "3B 84 80 01 80 82 90 00 97"
ATR_GIRO = "3B 87 80 01 80 31 C0 73 D6 31 C0 23"
ATR_EGK = "3B 85 80 01 30 01 01 30 30 34"

ALL_ATRS = [ATR_E_PERSO, ATR_GIRO, ATR_EGK, ATR_DES_FIRE]

STATE_IDLE = 0
STATE_PLAYING = 1

NO_SONG = -1

FUNC_PLAYLIST_RESTART = 0
FUNC_SONG_RESTART = 1
FUNC_END = 2
FUNC_PERFORMED = 3
FUNC_SONG_SKIP = 4
FUNC_SONG_PREV = 5

class SoundyPlayer:
    def __init__(self, ui, event_insert, event_remove, event_music_end, event_comm_error, event_function, event_playing, event_pause, event_list_end, ui_stopped):
        self.insert = event_insert
        self.remove = event_remove
        self.play_end = event_music_end
        self.comm_error = event_comm_error
        self.function_event = event_function
        self.play_start_event = event_playing
        self.event_pause = event_pause
        self.event_list_end = event_list_end
        self.event_ui_stopped = ui_stopped
        self.state = STATE_IDLE
        self.playing_id = NO_SONG
        self.perform_function = None
        self._end_program = False
        self.ui = ui

        c = ui.ui_config["ids"]
        self.card_id_rewind = c["rewind"]
        self.card_id_restart = c["restart"]
        self.card_id_end = c["end"]
        self.card_id_skip = c["skip"]
        self.card_id_prev = c["prev"]
        self.titles = {}

    def load_config(self, config_dir):
        try:
            titles_raw = SoundyPlayer.read_config(config_dir)
        except:
            print("Kann Playlisten nicht laden")
            os.exit(42)

        self.titles = {}
        for i in titles_raw:
            self.titles[i.card_id] = i

    @staticmethod
    def read_config(dir):
        all_files = []
        for file in os.listdir(dir):
            if file.endswith(".json"):
                all_files.append(os.path.join(dir, file))

        def loader_f(file_name):
            return playlist.PlayList.from_json(file_name)
        
        res = list(map(loader_f, all_files))

        return res

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
            if self.perform_function != None:
                context = self.perform_function(self.titles[event.card_id])
                pygame.event.post(pygame.event.Event(self.function_event, kind=FUNC_PERFORMED, ctx=context))
                self.perform_function = None

            pl = self.titles[event.card_id]
            mixer.music.load(pl.current_song())
            start_pos = pl.get_play_time()

            mixer.music.play(start = start_pos)
            self.playing_id = event.card_id
            self.state = STATE_PLAYING            
            pygame.event.post(pygame.event.Event(self.play_start_event, play_list_name=pl.play_list_name(), song=pl.current_song_num(), num_songs=pl.num_songs(), beep=event.beep))

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
        elif event.type == self.comm_error:
            self.ui.handle_card_error()
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

def main():
    # Last parameter is buffer size. Maybe increase it further if sound starts to lag
    mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    mixer.init()
    os.system('clear')

    event_insert = pygame.event.custom_type()
    event_remove = pygame.event.custom_type()
    event_music_end = pygame.event.custom_type()
    event_comm_error = pygame.event.custom_type()
    event_function = pygame.event.custom_type()
    event_playing = pygame.event.custom_type()
    event_pause = pygame.event.custom_type()
    event_list_end = pygame.event.custom_type()
    event_ui_stopped = pygame.event.custom_type()
    pygame.mixer.music.set_endevent(event_music_end)

    config_dir ="./"
    if len(sys.argv) > 1:
        config_dir = sys.argv[1]

    ui = soundy_ui.SoundyUI(event_ui_stopped)
    ui.load_config(config_dir)

    player = SoundyPlayer(ui, event_insert, event_remove, event_music_end, event_comm_error, event_function, event_playing, event_pause, event_list_end, event_ui_stopped)
    player.load_config(config_dir)

    card_manager = cardy.CardManager(ALL_ATRS, cardy.DESFireUidReader(ATR_DES_FIRE), event_insert, event_remove, event_comm_error)
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
