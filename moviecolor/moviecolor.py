from PIL import Image, ImageDraw, ImageTk
import ffmpeg
import logging
import numpy as np
import subprocess

class movcolor:

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    def __call__(self, *args):
        self.run(*args)

    def __init__(self, id, in_path, out_path) -> None:
        self.id = id
        self.in_path = in_path
        self.out_path = out_path
        self.bars_flag = 0
        self.rgb_list = []

    def get_video_duration(self):
        probe = ffmpeg.probe(self.in_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        duration = int(video_info['duration'].split('.')[0])
        return duration

    def get_video_size(self):
        self.logger.info('Getting video size for {!r}'.format(self.in_path))
        probe = ffmpeg.probe(self.in_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        return width, height


    def start_ffmpeg_process1(self, start, length):
        self.logger.info('Starting ffmpeg process1')
        args = (
            ffmpeg
            .input(self.in_path)
            .trim(start=start*60, end=length*60)
            .filter_('fps',fps=3) # get 3 frames per second
            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
            .compile()
        )
        return subprocess.Popen(args, stdout=subprocess.PIPE)


    def read_frame(self, process1, width, height):
        self.logger.debug('Reading frame')

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

    @staticmethod
    def process_frame_average_color(frame):   
        rgb_avg = int(np.average(frame[:,:,0])),int(np.average(frame[:,:,1])),int(np.average(frame[:,:,2]))
        return rgb_avg
    
    @staticmethod
    def process_frame_compress_width(frame):
        img = Image.fromarray(frame, 'RGB').resize((1,720))
        return img

    def draw_alt(self):
        len_rgb_list = len(self.rgb_list)
        
        image_height = int(len_rgb_list*9/16) # to make a 16:9
        new = Image.new('RGB',(len_rgb_list,image_height))
        for i in range(len_rgb_list-1):      
            new.paste(self.rgb_list[i].resize((1,image_height)), (i, 0))

        if self.out_path.suffix.lower() == ".jpg":
            suff = "JPEG"
        elif self.out_path.suffix.lower() == ".png":
            suff = "PNG"
        else:
            suff = "PNG"
            self.out_path = str(self.out_path) + ".png"

        new.save(self.out_path, suff)

    def draw_normal(self):
        len_rgb_list = len(self.rgb_list)
        
        image_height = int(len_rgb_list*9/16) # to make a 16:9
        new = Image.new('RGB',(int(len_rgb_list),image_height))
        draw = ImageDraw.Draw(new)
        x_pixel = 1 # x axis of the next line to draw
        for rgb_tuple in self.rgb_list:
            draw.line((x_pixel,0,x_pixel,image_height), fill=rgb_tuple)
            x_pixel = x_pixel + 1
        
        if self.out_path.suffix.lower() == ".jpg":
            suff = "JPEG"
        elif self.out_path.suffix.lower() == ".png":
            suff = "PNG"
        else:
            suff = "PNG"
            self.out_path = str(self.out_path) + ".png"

        new.save(self.out_path, suff)


    def run(self, length, process_frame, draw_func, start):
        
        width, height = self.get_video_size()
        process1 = self.start_ffmpeg_process1(start, length)

        while True:
            in_frame = self.read_frame(process1, width, height)
            if in_frame is None:
                self.logger.info('End of input stream')
                break

            self.logger.debug('Processing frame')
            out_frame = process_frame(in_frame)
                 
            self.rgb_list.append(out_frame)


        self.bars_flag = len(self.rgb_list)
        draw_func()

        
        self.logger.info('Waiting for ffmpeg process1')
        process1.wait()

        self.logger.info('Done')

    def refresh_image_alt(self, canvas, x_pixel, number_of_frames, *param):
        
        dst = Image.new('RGB', (1500, 720))

        if len(param) != 0 : 
            dst = param[0]

        step = 1500 / number_of_frames
        for rgb_tuple in self.rgb_list[int((x_pixel-1)*(1/step)):]: 
            dst.paste(rgb_tuple, (int(x_pixel), 0))
            x_pixel += 1
        global image
        image = ImageTk.PhotoImage(dst)
        canvas.create_image((750, 360), image=image)

        if len(self.rgb_list) != self.bars_flag:
            canvas.after(100, self.refresh_image_alt, canvas, x_pixel, number_of_frames, dst)

    def refresh_image_normal(self, canvas, x_pixel, number_of_frames):        
        image_height = 720
        step = 1500 / number_of_frames
        for rgb_tuple in self.rgb_list[int((x_pixel-1)*(1/step)):]:
            canvas.create_line((x_pixel,0,x_pixel,image_height), fill='#%02x%02x%02x' % rgb_tuple, width=step)
            x_pixel += 1

        if len(self.rgb_list) != self.bars_flag:
            canvas.after(100, self.refresh_image_normal, canvas, x_pixel-step, number_of_frames)