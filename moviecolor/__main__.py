#from moviecolor import Movcolor
from pathlib import Path
import argparse
import sys

from moviecolor.moviecolor import Movcolor

parser = argparse.ArgumentParser()
parser.add_argument('in_file', type=Path, help='Input file path')
parser.add_argument('-o', '--out_filename', type=Path,
                    default='result', help='Output file path')
parser.add_argument('-s', '--start', type=int, default=0,
                    help='Start point of the chosen part of the video in Minutes')
parser.add_argument('-e', '--end', type=int, default=0,
                    help='End point of the chosen part of the video in Minutes')
parser.add_argument('-a', '--alt', action='store_true',
                    help='Instead of average color, Each bar is the resized frame')


def main():
    """Starting point of the program
    to read the input args and create movcolor object"""

    args = parser.parse_args()

    input_file_path = args.in_file

    if not input_file_path.is_file():
        print(
            "\nEnter Valid input Path.\n"
            "Example (on windows): \"c:\\video\\input with white space.mp4\"\n"
            "Example (on linux): /home/video/file.mp4"
        )
        sys.exit()

    output_file_path = args.out_filename
    start_point = args.start
    end_point = args.end

    if args.alt:
        mode = "alt"
    else:
        mode = "normal"

    obj1 = Movcolor(1, input_file_path, output_file_path, start_point, end_point, mode)
    obj1.run()

if __name__ == "__main__":
    main()
