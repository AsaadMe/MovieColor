from PIL import Image, ImageDraw, ImageTk
from pathlib import Path
import argparse
import ffmpeg
import logging
import numpy as np
import subprocess
import tkinter as tk
import threading
import time

parser = argparse.ArgumentParser()
parser.add_argument('in_file', type=Path, help='Input file path')
parser.add_argument('-o','--out_filename', type=Path, default='result', help='Output file path')
parser.add_argument('-l','--length', type=int, default=0 , help='Chosen part of the video from start in Minutes')
parser.add_argument('-a','--alt', action='store_true', help='Instead of gettig average color of frames, Each bar is the resized frame')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

rgb_list = []
bars_flag = 0

def get_video_duration(filepath):
    probe = ffmpeg.probe(filepath)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    duration = int(video_info['duration'].split('.')[0])
    return duration

def get_video_size(filepath):
    logger.info('Getting video size for {!r}'.format(filepath))
    probe = ffmpeg.probe(filepath)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    return width, height


def start_ffmpeg_process1(in_filename, length):
    logger.info('Starting ffmpeg process1')
    args = (
        ffmpeg
        .input(in_filename)
        .trim(end=length*60)
        .filter_('fps',fps=3) # get 3 frames per second
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .compile()
    )
    return subprocess.Popen(args, stdout=subprocess.PIPE)


def read_frame(process1, width, height):
    logger.debug('Reading frame')

    # Note: RGB24 == 3 bytes per pixel.
    frame_size = width * height * 3
    in_bytes = process1.stdout.read(frame_size)
    if len(in_bytes) == 0:
        frame = None
    else:
        assert len(in_bytes) == frame_size
        frame = (
            np
            .frombuffer(in_bytes, np.uint8)
            .reshape([height, width, 3])
        )
    return frame


def process_frame_average_color(frame):   
    rgb_avg = int(np.average(frame[:,:,0])),int(np.average(frame[:,:,1])),int(np.average(frame[:,:,2]))
    return rgb_avg

def process_frame_compress_width(frame):
    img = Image.fromarray(frame, 'RGB').resize((1,720))
    return img

def draw_output(rgb_list, out_path):
    len_rgb_list = len(rgb_list)
    
    if args.alt:
        image_height = int(len_rgb_list*9/16) # to make a 16:9
        new = Image.new('RGB',(int(len_rgb_list/2),image_height))
        for i in range(len_rgb_list-1):      
            new.paste(rgb_list[i], (int(i/2), 0))

    else:
        image_height = int(len_rgb_list*9/16) # to make a 16:9
        new = Image.new('RGB',(int(len_rgb_list),image_height))
        draw = ImageDraw.Draw(new)
        x_pixel = 1 # x axis of the next line to draw
        for rgb_tuple in rgb_list:
            draw.line((x_pixel,0,x_pixel,image_height), fill=rgb_tuple)
            x_pixel = x_pixel + 1
    
    if out_path.suffix.lower() == ".jpg":
        suff = "JPEG"
    elif out_path.suffix.lower() == ".png":
        suff = "PNG"
    else:
        suff = "PNG"
        out_path = str(out_path) + ".png"

    new.save(out_path, suff)


def run(in_path, out_filename, length, process_frame):
    
    width, height = get_video_size(in_path)
    process1 = start_ffmpeg_process1(in_path, length)
    while True:
        in_frame = read_frame(process1, width, height)
        if in_frame is None:
            logger.info('End of input stream')
            break

        logger.debug('Processing frame')
        out_frame = process_frame(in_frame)
        global rgb_list      
        rgb_list.append(out_frame)

    global bars_flag
    bars_flag = len(rgb_list)
    draw_output(rgb_list, out_filename)
      
    logger.info('Waiting for ffmpeg process1')
    process1.wait()

    logger.info('Done')

def refresh_image_alt(canvas, x_pixel, number_of_frames, *param):
    
    dst = Image.new('RGB', (1500, 720))

    if len(param) != 0 : 
        dst = param[0]

    step = 1500 / number_of_frames
    for rgb_tuple in rgb_list[int((x_pixel-1)*(1/step)):]: 
        dst.paste(rgb_tuple, (int(x_pixel), 0))
        x_pixel += step
    global image
    image = ImageTk.PhotoImage(dst)
    canvas.create_image((750, 360), image=image)

    if len(rgb_list) != bars_flag:
        canvas.after(100, refresh_image_alt, canvas, x_pixel, number_of_frames, dst)

def refresh_image_normal(canvas, x_pixel, number_of_frames):        
    image_height = 720
    step = 1500 / number_of_frames
    for rgb_tuple in rgb_list[int((x_pixel-1)*(1/step)):]:
        canvas.create_line((x_pixel,0,x_pixel,image_height), fill='#%02x%02x%02x' % rgb_tuple, width=step)
        x_pixel = x_pixel + step

    if len(rgb_list) != bars_flag:
        canvas.after(100, refresh_image_normal, canvas, x_pixel-step, number_of_frames)

if __name__ == '__main__':
    root = tk.Tk()
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
    if video_length != 0:
        number_of_frames = video_length * 60 * 3
    else:
        duration = get_video_duration(input_file_path)
        number_of_frames = duration * 3
        video_length = int(duration/60)

    if args.alt:
        process_func = process_frame_compress_width
        refresh_image = refresh_image_alt
    else:
        process_func = process_frame_average_color
        refresh_image = refresh_image_normal

    th = threading.Thread(target=run, args=(input_file_path, output_file_path, video_length ,process_func))
    th.daemon = True  # terminates whenever main thread does
    th.start()
    while len(rgb_list) == 0:  # rgb_list in refresh_image shouldnt be empty
        time.sleep(.1)

    canvas = tk.Canvas(root, height=720, width=1500)
    root.title("MovieColor")
    root.geometry("1500x720+0+10")
    canvas.pack()

    refresh_image(canvas, 1, number_of_frames)
    root.mainloop()