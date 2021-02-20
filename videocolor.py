from PIL import Image, ImageDraw
import ffmpeg
import numpy as np

#TODO : (Video) variable gets too big for large videos. should use threads or 
# multiprocess or pipe it as a stream directly to numpy. --> speed up the process of ffmpeg.
#TODO : Add argparse to get filename, width of each bar, height of the outpic(result).
#TODO : Add GUI with Qt or Tkinter. 
#TODO : Accept input formats other than just mp4.


def draw_next_frame_rgb_avg(raw_frame):    
    frame =  np.frombuffer(raw_frame, dtype='uint8')
    frame = frame.reshape((height,width,3))    
    rgb_avg = int(np.average(frame[:,:,0])),int(np.average(frame[:,:,1])),int(np.average(frame[:,:,2]))
    return rgb_avg

probe = ffmpeg.probe('file.mp4')
video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
width = int(video_info['width'])
height = int(video_info['height'])
num_frames = int(video_info['nb_frames'])

out, err = (
    ffmpeg
    .input('file.mp4')
    .trim(end=5*60)
    .filter_('fps',fps=3)
    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
    .run(capture_stdout=True)
)
video = (
    np
    .frombuffer(out, np.uint8)
    .reshape([-1, height, width, 3])
)

rgb_list = []
for frame in video:
    rgb_list.append(draw_next_frame_rgb_avg(frame))

image_height = 720 # OR --> int(len(rgb_list)*9/16) to make a 16:9
new = Image.new('RGB',(len(rgb_list),image_height))
draw = ImageDraw.Draw(new)

x_pixel = 1 # x axis of the next line to draw
for rgb_tuple in rgb_list:
    draw.line((x_pixel,0,x_pixel,image_height), fill=rgb_tuple)
    x_pixel = x_pixel + 1
new.show() 
new.save("outpic.png", "PNG")