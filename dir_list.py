import sys
import json
from os import listdir
from os.path import isfile, join


def create_json_listing(src_path, out_file):
    only_files = [f for f in listdir(src_path) if isfile(join(src_path, f))]
    only_files.sort()

    with(open(out_file, "w") as f):
        json.dump(only_files, f, indent=4)


if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print("usage: dir_list <dir to list> <out_file>")
            sys.exit(42)

        create_json_listing(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(e)