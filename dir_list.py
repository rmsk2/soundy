import sys
import json
from os import listdir
from os.path import isfile, join
import playlist


def add_json_listing(src_path, out_file):
    play_list = playlist.PlayList.from_json(out_file)
    only_files = [f for f in listdir(src_path) if isfile(join(src_path, f))]
    only_files.sort()

    play_list.titles = only_files
    play_list.save()

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print("usage: dir_list <dir to list> <playlist file to modify>")
            sys.exit(42)

        add_json_listing(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(e)