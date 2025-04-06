import sys
from os import listdir
from os.path import isfile, join
from pathlib import Path
import playlist


def gen_listing(src_path):
    only_files = [f for f in listdir(src_path) if isfile(join(src_path, f))]
    only_files.sort()

    return only_files

def create_new_playlist(dir_to_list, out_name):
    data_dir = Path(dir_to_list)
    playlist_name = input("Playlist name      : ")
    card_id = int(input("Id of playlist card: "))

    play_list = playlist.PlayList(card_id, out_name, gen_listing(data_dir))
    play_list.play_list = playlist_name
    play_list.data_dir = str(data_dir)

    play_list.save()


if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print("usage: create_list <dir to list> <new playlist file>")
            sys.exit(42)
        
        create_new_playlist(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(e)