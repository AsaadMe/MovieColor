#from moviecolor import *
from moviecolor.moviecolor import movcolor
from pathlib import Path
import tkinter as tk
import argparse
import threading
#import multiprocessing
import time

parser = argparse.ArgumentParser()
parser.add_argument('in_file', type=Path, help='Input file path')
parser.add_argument('-o','--out_filename', type=Path, default='result', help='Output file path')
parser.add_argument('-l','--length', type=int, default=0 , help='Chosen part of the video from start in Minutes')
parser.add_argument('-a','--alt', action='store_true', help='Instead of gettig average color of frames, Each bar is the resized frame')

def main():

    args = parser.parse_args()

    input_file_path = args.in_file
    
    if not input_file_path.is_file():
        print(
        "\nEnter Valid input Path.\n"
        "Example (on windows): \"c:\\video\\input with white space.mp4\"\n"
        "Example (on linux): /home/video/file.mp4"
        )
        exit()

    output_file_path = args.out_filename
    video_length = args.length

    obj1 = movcolor(1, input_file_path, output_file_path)

    if video_length != 0:
        number_of_frames = video_length * 60 * 3
    else:
        duration = obj1.get_video_duration()
        number_of_frames = duration * 3
        video_length = int(duration/60)
    
    if args.alt:
        process_func = movcolor.process_frame_compress_width
        refresh_image = obj1.refresh_image_alt
        draw_func = obj1.draw_alt
    else:
        process_func = movcolor.process_frame_average_color
        refresh_image = obj1.refresh_image_normal
        draw_func = obj1.draw_normal

    obj2 = movcolor(2,input_file_path, output_file_path.parent / "res2")
    th = threading.Thread(target=obj1, args=(video_length ,process_func, draw_func, 0))
    #th2 = threading.Thread(target=obj2, args=(10 ,process_func, obj2.draw_normal, 5))

    #th = multiprocessing.Process(target=obj1, args=(video_length ,process_func, draw_func, 0))
    #th2 = multiprocessing.Process(target=obj2, args=(10 ,process_func, obj2.draw_normal, 5))
    th.daemon = True  # terminates whenever main thread does
    th.start()
    #th2.start()
    
    while len(obj1.rgb_list) == 0:  # rgb_list in refresh_image shouldnt be empty
        time.sleep(.1)

    root = tk.Tk()
    canvas = tk.Canvas(root, height=720, width=1500)

    root.title("MovieColor")
    root.geometry("1500x720+0+10")
    canvas.pack()

    refresh_image(canvas, 1, number_of_frames)
    root.mainloop()

if __name__ == "__main__":
    main()