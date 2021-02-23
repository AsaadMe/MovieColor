from PIL import Image, ImageDraw
import argparse
import ffmpeg
import logging
import numpy as np
import subprocess
import tkinter as tk
import threading
import time

parser = argparse.ArgumentParser()
parser.add_argument('in_filename', help='Input filename')
parser.add_argument('-o','--out_filename', type=str, default='result', help='Output filename')
parser.add_argument('-l','--length', type=int, default=200 , help='length of video from start in Minutes')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

rgb_list = []
bars_flag = 0

def get_video_size(filename):
    logger.info('Getting video size for {!r}'.format(filename))
    probe = ffmpeg.probe(filename)
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
        .filter_('fps',fps=3)
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


def process_frame_average_color(frame, height, width):
    frame =  np.frombuffer(frame, dtype='uint8')
    frame = frame.reshape((height,width,3))    
    rgb_avg = int(np.average(frame[:,:,0])),int(np.average(frame[:,:,1])),int(np.average(frame[:,:,2]))
    return rgb_avg


def draw_output(rgb_list, out_filename):
    image_height = int(len(rgb_list)*9/16) # to make a 16:9
    new = Image.new('RGB',(len(rgb_list),image_height))
    draw = ImageDraw.Draw(new)

    x_pixel = 1 # x axis of the next line to draw
    for rgb_tuple in rgb_list:
        draw.line((x_pixel,0,x_pixel,image_height), fill=rgb_tuple)
        x_pixel = x_pixel + 1
    #new.show() 
    new.save(f"{out_filename}.png", "PNG")


def run(in_filename, out_filename, length, process_frame):
    
    width, height = get_video_size(in_filename)
    process1 = start_ffmpeg_process1(in_filename, length)
    while True:
        in_frame = read_frame(process1, width, height)
        if in_frame is None:
            logger.info('End of input stream')
            break

        logger.debug('Processing frame')
        out_frame_average_color = process_frame(in_frame, height, width)
        global rgb_list      
        rgb_list.append(out_frame_average_color)

    global bars_flag
    bars_flag = len(rgb_list)
    draw_output(rgb_list, out_filename)
      
    logger.info('Waiting for ffmpeg process1')
    process1.wait()

    logger.info('Done')

def refresh_image(canvas):
    x_pixel = 1 # x axis of the next line to draw
    image_height = 720
    for rgb_tuple in rgb_list:
        canvas.create_line((x_pixel,0,x_pixel,image_height), fill='#%02x%02x%02x' % rgb_tuple)
        x_pixel = x_pixel + 0.5
    # repeat every half sec
    if len(rgb_list) != bars_flag:
        canvas.after(100, refresh_image, canvas)

if __name__ == '__main__':
    root = tk.Tk()
    args = parser.parse_args()
    th = threading.Thread(target=run, args=(args.in_filename, args.out_filename.split(".")[0], args.length ,process_frame_average_color))
    th.daemon = True  # terminates whenever main thread does
    th.start()
    while len(rgb_list) == 0:  # rgb_list in refresh_image shouldnt be empty
        time.sleep(.1)

    canvas = tk.Canvas(root, height=400, width=1800)
    canvas.pack()

    refresh_image(canvas)
    root.mainloop()