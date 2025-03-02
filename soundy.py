#! /usr/bin/env python3


import os
from pygame import mixer
import pygame
import cardy
import playlist

ATR_TYLER = "3B 84 80 01 80 82 90 00 97"
ATR_DES_FIRE = "3B 81 80 01 80 80"
ATR_REWIND = "3B 85 80 01 80 73 C8 21 10 0E"

STATE_IDLE = 0
STATE_PLAYING = 1

NO_SONG = -1

class Title:
    def __init__(self, title, card_id):
        self.title = title
        self.play_time = 0.0
        self.id = card_id   


class SoundyPlayer:
    def __init__(self, event_insert, event_remove, event_music_end):
        self.insert = event_insert
        self.remove = event_remove
        self.play_end = event_music_end
        self.state = STATE_IDLE
        self.playing_id = NO_SONG
        self.do_rewind = False

        #try:
        self.titles_raw = SoundyPlayer.read_config("./")
        #except:
        #    print("Unable to load config files")
        #    os.exit(42)

        self.card_id_rewind = len(self.titles_raw)

        self.titles = {}
        for i in self.titles_raw:
            self.titles[i.card_id] = i

    @staticmethod
    def read_config(dir):
        all_files = []
        for file in os.listdir(dir):
            if file.endswith(".json"):
                all_files.append(os.path.join(dir, file))
        
        res = list(map(lambda x: playlist.PlayList.from_json(x), all_files))

        return res

    def work_event_queue(self):
        event = pygame.event.wait()
        if event.type == self.insert:

            if self.state != STATE_IDLE:
                return
            
            if event.card_id == self.card_id_rewind:
                self.do_rewind = True
                print('\a')
            else:
                if event.beep:
                    print('\a')
                
                if self.do_rewind:
                    self.titles[event.card_id].reset()
                    self.do_rewind = False

                print(f"Playing {self.titles[event.card_id].current_song()}")
                mixer.music.load(self.titles[event.card_id].current_song())
                start_pos = self.titles[event.card_id].get_play_time()

                mixer.music.play(start = start_pos)
                self.playing_id = event.card_id
                self.state = STATE_PLAYING
        elif event.type == self.remove:

            if self.state != STATE_PLAYING:
                return

            if event.card_id != self.playing_id:
                return
            
            print(f"Stopping {self.titles[event.card_id].current_song()}")
            self.titles[self.playing_id].increase_play_time(mixer.music.get_pos() / 1000.0)
            self.playing_id = NO_SONG
            self.state = STATE_IDLE
            mixer.music.stop()
        elif event.type == self.play_end:

            if self.state != STATE_PLAYING:
                return
            
            print(f"End of song reached")

            playlist_end = self.titles[self.playing_id].next_song()
            if playlist_end:
                self.titles[self.playing_id].reset()
                self.playing_id = NO_SONG
                self.state = STATE_IDLE                
                print("End of playlist reached")
                return
            
            h = self.playing_id
            self.playing_id = NO_SONG
            self.state = STATE_IDLE
            pygame.event.post(pygame.event.Event(self.insert, card_id=h, beep=False))

def main():
    pygame.init()
    mixer.init()
    os.system('clear')
    
    event_insert = pygame.event.custom_type()
    event_remove = pygame.event.custom_type()
    event_music_end = pygame.event.custom_type()
    pygame.mixer.music.set_endevent(event_music_end)

    card_manager = cardy.CardManager([ATR_TYLER, ATR_DES_FIRE, ATR_REWIND], cardy.UidReader(ATR_DES_FIRE), event_insert, event_remove)
    card_manager.start()
    
    player = SoundyPlayer(event_insert, event_remove, event_music_end)

    try:
        while True:
            player.work_event_queue()
    except KeyboardInterrupt:
        pass
    finally:
        card_manager.destroy()

if __name__ == "__main__":
    main()    
