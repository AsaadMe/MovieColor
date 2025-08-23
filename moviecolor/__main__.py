import argparse
import sys
from pathlib import Path

from moviecolor.core import make_barcode

parser = argparse.ArgumentParser()
parser.add_argument("in_file", type=Path, help="Input file path")
parser.add_argument("-a", "--alt", action="store_true", help="Instead of average color, Each bar is the resized frame")


def main():
    args = parser.parse_args()

    input_file_path = args.in_file

    if not input_file_path.is_file():
        print("Enter Valid input Path.")
        sys.exit()

    if args.alt:
        mode = "frame"
    else:
        mode = "average"

    make_barcode(input_file_path, mode=mode)


if __name__ == "__main__":
    main()
