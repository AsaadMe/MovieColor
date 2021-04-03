"""moviecolor module contains movcolor class
to generate the barcode image of video and show it
in real-time on a tkinter canvas.
"""

import sys
import time
import logging
import threading

from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
import numpy as np
import ffmpeg


class Movcolor:
    """Create an object to generate a barcode of a video file.

    Functions:
        - get_video_duration()
        - get_video_size()
        - start_ffmpeg_process(start, end)
        - read_frame(process, width, height)
        - process_frame_average_color(frame)
        - process_frame_compress_width(frame)
        - draw_alt()
        - draw_normal()
        - refresh_image_alt(canvas, x_pixel, number_of_frames, *param)
        - refresh_image_normal(canvas, x_pixel, number_of_frames)
        - worker(process_frame, draw_func, start, end)
        - run()
    """

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    def __call__(self, *args):
        self.run(*args)

    def __init__(self, instance_id, in_path, out_path,
                start_point, end_point, draw_mode="normal"):
        self.instance_id = instance_id
        self.in_path = in_path
        self.out_path = out_path
        self.start_point = start_point

        if end_point != 0:
            self.end_point = end_point
            self.number_of_frames = end_point * 60 * 3
        else:
            duration = self.get_video_duration()
            self.number_of_frames = duration * 3
            self.end_point = int(duration/60)

        self.draw_mode = draw_mode

        if self.draw_mode == "alt":
            self.process_func = self.process_frame_compress_width
            self.refresh_image = self.refresh_image_alt
            self.draw_func = self.draw_alt
        else:
            self.process_func = self.process_frame_average_color
            self.refresh_image = self.refresh_image_normal
            self.draw_func = self.draw_normal

        # used in refresh_image funcs to determine when to stop drawing bars
        self.bars_flag = 0
        self.rgb_list = []  # list of the bars

    def get_video_duration(self):
        """get duration of the video in seconds.

        Returns:
            int: duration of the video in seconds

        Exceptions:
            ffmpeg can't get some videos durations.
            in these cases print an error and exit.
        """

        probe = ffmpeg.probe(self.in_path)
        video_info = next(
            s for s in probe['streams'] if s['codec_type'] == 'video')

        try:
            duration = int(video_info['duration'].split('.')[0])
        except:
            print(
                """ERROR: can't extract duration of the video,
        please specify it by '-e' option.""")
            sys.exit()

        return duration

    def get_video_size(self):
        """get width and hight of the video.

        Returns:
            tuple: width(int) and height(int) of video
        """

        self.logger.info(f'Getting video size for {self.in_path}')
        probe = ffmpeg.probe(self.in_path)
        video_info = next(
            s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        return width, height

    def start_ffmpeg_process(self, start, end):
        """starting and ending time of the video to get barcode.
        each frame will piped in stream in bytes.

        Args:
            start (int): start time of the video in minute
            end (int): end time of the video in minute

        Returns:
            process object: ffmpeg process object
            which is called in read_frame to get frames in stream.
        """

        self.logger.info('Starting ffmpeg process1')
        process = (
            ffmpeg
            .input(self.in_path)
            .trim(start=start*60, end=end*60)
            .filter_('fps', fps=3)  # get 3 frames per second
            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
            .run_async(pipe_stdout=True)
        )

        return process

    def read_frame(self, process, width, height):
        """get an array of each frame of the video.

        Args:
            process (process object): ffmpeg object
            which get the frames of video

            width (int): width of video
            height (int): height of video

        Returns:
            numpy frame object: numpy array of the frame
        """

        self.logger.debug('Reading frame')

        # Note: RGB24 == 3 bytes per pixel.
        frame_size = width * height * 3
        in_bytes = process.stdout.read(frame_size)
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
        """get average color of a frame in tuple (rgb).

        Args:
            frame (numpy frame object): numpy array of the frame

        Returns:
            tuple: rgb color typle in ints
        """

        rgb_avg = int(np.average(frame[:, :, 0])), int(
            np.average(frame[:, :, 1])), int(np.average(frame[:, :, 2]))
        return rgb_avg

    @staticmethod
    def process_frame_compress_width(frame):
        """get shrinked image of a frame.

        Args:
            frame (numpy frame object): numpy array of the frame

        Returns:
            pillow.image: shrinked (resized) frame in img format
        """

        img = Image.fromarray(frame, 'RGB').resize((1, 720))
        return img

    def draw_alt(self):
        """draw and save the final barcode picture
        (alt mode = shrinked frames)."""

        len_rgb_list = len(self.rgb_list)

        image_height = int(len_rgb_list*9/16)  # to make a 16:9
        new = Image.new('RGB', (len_rgb_list, image_height))
        for i in range(len_rgb_list-1):
            new.paste(self.rgb_list[i].resize((1, image_height)), (i, 0))

        if self.out_path.suffix.lower() == ".jpg":
            suff = "JPEG"
        elif self.out_path.suffix.lower() == ".png":
            suff = "PNG"
        else:
            suff = "PNG"
            self.out_path = str(self.out_path) + ".png"

        new.save(self.out_path, suff)

    def draw_normal(self):
        """draw and save the final barcode picture
        with average color for each frame."""

        len_rgb_list = len(self.rgb_list)

        image_height = int(len_rgb_list*9/16)  # to make a 16:9
        new = Image.new('RGB', (int(len_rgb_list), image_height))
        draw = ImageDraw.Draw(new)
        x_pixel = 1  # x axis of the next line to draw
        for rgb_tuple in self.rgb_list:
            draw.line((x_pixel, 0, x_pixel, image_height), fill=rgb_tuple)
            x_pixel = x_pixel + 1

        if self.out_path.suffix.lower() == ".jpg":
            suff = "JPEG"
        elif self.out_path.suffix.lower() == ".png":
            suff = "PNG"
        else:
            suff = "PNG"
            self.out_path = str(self.out_path) + ".png"

        new.save(self.out_path, suff)

    def refresh_image_alt(self, canvas, x_pixel, number_of_frames, *param):
        """draw each bar every 0.1 second by calling canvas.after.
        (alt mode)

        Args:
            canvas (tkinter.canvas): main tkinter canvas which show the bars
            x_pixel (int): position of X axis to draw the next bar on canvas
            number_of_frames (int): count of the frames to draw on canvas
        """

        dst = Image.new('RGB', (1500, 720))

        if len(param) != 0:
            dst = param[0]

        step = 1500 / number_of_frames
        for rgb_tuple in self.rgb_list[int((x_pixel-1)*(1/step)):]:
            dst.paste(rgb_tuple, (int(x_pixel), 0))
            x_pixel += 1
        global image
        image = ImageTk.PhotoImage(dst)
        canvas.create_image((750, 360), image=image)

        if len(self.rgb_list) != self.bars_flag:
            canvas.after(100, self.refresh_image_alt, canvas,
                         x_pixel, number_of_frames, dst)

    def refresh_image_normal(self, canvas, x_pixel, number_of_frames):
        """draw each bar every 0.1 second by calling canvas.after.
        (normal mode)

        Args:
            canvas (tkinter.canvas): main tkinter canvas which show the bars
            x_pixel (int): position of X axis to draw the next bar on canvas
            number_of_frames (int): count of the frames to draw on canvas
        """

        image_height = 720
        step = 1500 / number_of_frames
        for rgb_tuple in self.rgb_list[int((x_pixel-1)*(1/step)):]:
            canvas.create_line((x_pixel, 0, x_pixel, image_height),
                               fill='#%02x%02x%02x' % rgb_tuple, width=step)
            x_pixel += 1

        if len(self.rgb_list) != self.bars_flag:
            canvas.after(100, self.refresh_image_normal,
                         canvas, x_pixel-step, number_of_frames)

    def worker(self, process_frame, draw_func, start, end):
        """run the main functionality of program to save final image.

        Args:
            process_frame (ffmpeg process object): ffmepg process object
            which is called here and pass to read_frame.

            draw_func (function): one of two alt or noraml draw function
            start (int): start time of video in minute
            end (int): end time of video in minute
        """

        width, height = self.get_video_size()
        process = self.start_ffmpeg_process(start, end)

        while True:
            in_frame = self.read_frame(process, width, height)
            if in_frame is None:
                self.logger.info('End of input stream')
                break

            self.logger.debug('Processing frame')
            out_frame = process_frame(in_frame)

            self.rgb_list.append(out_frame)

        self.bars_flag = len(self.rgb_list)
        draw_func()

        self.logger.info('Waiting for ffmpeg process1')
        process.wait()

        self.logger.info('Done')

    def run(self):
        """run the worker thread and create tkinter canvas to
        draw bars in real-time base on the --alt arg
        with it's func or normal draw func.
        """
        worker_args = (self.process_func, self.draw_func, self.start_point, self.end_point)
        work_thread = threading.Thread(target=self.worker, args=worker_args)

        work_thread.daemon = True
        work_thread.start()

        # rgb_list in refresh_image shouldnt be empty
        while len(self.rgb_list) == 0:
            time.sleep(0.1)

        root = tk.Tk()
        canvas = tk.Canvas(root, height=720, width=1500)

        root.title("MovieColor")
        root.geometry("1500x720+0+10")
        canvas.pack()

        self.refresh_image(canvas, 1, self.number_of_frames)
        root.mainloop()