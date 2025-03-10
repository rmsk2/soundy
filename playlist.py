import os.path
import json
import functools


class PlayList:
    def __init__(self, id, file_name, files):
        self.titles = files
        self.current_title = 0
        self.play_time = 0.0
        self.card_id = id
        self.file_name = file_name
        self.play_list = ""
        self.data_dir = ""

    @staticmethod
    def from_json(file_name):
        with(open(file_name, "r") as f):
            data = json.load(f)

        res = PlayList(data["card_id"], file_name, data["titles"])
        res.current_title = data["current_title"]
        res.play_time = data["play_time"]
        res.data_dir = data["data_dir"]
        res.play_list = data["play_list"]

        return res

    def serialize(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            with(open(self.file_name, "w") as f):
                json.dump(self.to_json(), f, indent=4)
            return result
        return wrap
    
    def play_list_name(self):
        return self.play_list

    def num_songs(self):
        return len(self.titles)

    def current_song_num(self):
        return self.current_title

    def current_song(self):
        return os.path.join(self.data_dir, self.titles[self.current_title])

    def to_json(self):
        res = {
            "play_list": self.play_list,
            "file_name": self.file_name,
            "current_title": self.current_title,
            "play_time": self.play_time,
            "card_id": self.card_id,
            "data_dir": self.data_dir,
            "titles": self.titles
        }

        return res

    @serialize
    def next_song(self):
        self.set_play_time(0.0)

        self.current_title += 1
        if self.current_title >= len(self.titles):
            return True        

        return False

    @serialize
    def prev_song(self):
        if self.current_title > 0:
            self.play_time = 0.0
            self.current_title -= 1

    @serialize
    def skip_song(self):
        if self.current_title + 1 < len(self.titles):
            self.play_time = 0.0
            self.current_title += 1

    def get_play_time(self):
        return self.play_time
    
    @serialize
    def save(self):
        pass

    @serialize
    def set_play_time(self, val):
        self.play_time = val

    @serialize
    def increase_play_time(self, val):
        self.play_time += val

    @serialize
    def reset_play_time(self):
        self.play_time = 0.0

    @serialize
    def reset(self):
        self.play_time = 0.0
        self.current_title = 0
