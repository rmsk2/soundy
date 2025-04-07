import sys
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import playlist
import cardy
from soundyconsts import *
import desfire
import pygame


def gen_listing(src_path):
    only_files = [f for f in listdir(src_path) if isfile(join(src_path, f))]
    only_files.sort()

    return only_files

def create_new_playlist(dir_to_list, out_name, card_id, playlist_name):
    data_dir = Path(dir_to_list)    

    print("Generating directory listing ...")
    play_list = playlist.PlayList(card_id, out_name, gen_listing(data_dir))
    play_list.play_list = playlist_name
    play_list.data_dir = str(data_dir)

    play_list.save()

def main(playlist_dir, out_name, event_insert):
    playlist_name = input("Enter playlist name          : ")
    sys.stdout.write("Place playlist card on reader: ")
    sys.stdout.flush()
    card_id = None

    while card_id == None:
        event = pygame.event.wait()
        if event.type == event_insert:
            card_id = event.card_id
            print(f"Card id {card_id}")

    create_new_playlist(playlist_dir, out_name, card_id, playlist_name)


if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print("usage: create_list <dir to list> <new playlist file>")
            sys.exit(42)

        pygame.init()
        os.system(CLEAR_COMMAND)
        event_insert = pygame.event.custom_type()
        event_remove = pygame.event.custom_type()
        event_err_generic = pygame.event.custom_type()

        card_manager = cardy.CardManager(ALL_ATRS, desfire.DESFireUidReader(ATR_DES_FIRE), event_insert, event_remove, event_err_generic)
        card_manager.start()

        main(sys.argv[1], sys.argv[2], event_insert)
        print("\nNew playlist successfully created")
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(e)
    finally:
        card_manager.destroy()
        pygame.quit()
        