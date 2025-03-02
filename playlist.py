import json
import functools


class PlayList:
    def __init__(self, id, name, files):
        self.titles = files
        self.current_title = 0
        self.play_time = 0.0
        self.card_id = id
        self.name = name

    @staticmethod
    def from_json(file_name):
        with(open(file_name, "r") as f):
            data = json.load(f)
        
        res = PlayList(data["card_id"], data["name"], data["titles"])
        res.current_title = data["current_title"]
        res.play_time = data["play_time"]

        return res

    def serialize(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            with(open(self.name, "w") as f):
                json.dump(self.to_json(), f, indent=4)
            return result
        return wrap
    
    def current_song(self):
        return self.titles[self.current_title]

    def to_json(self):
        res = {
            "name": self.name,
            "current_title": self.current_title,
            "play_time": self.play_time,
            "card_id": self.card_id,
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

    def get_play_time(self):
        return self.play_time
    
    @serialize
    def set_play_time(self, val):
        self.play_time = val

    @serialize
    def increase_play_time(self, val):
        self.play_time += val

    @serialize
    def reset(self):
        self.play_time = 0.0
        self.current_title = 0
