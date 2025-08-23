import subprocess
import tkinter as tk

from PIL import Image, ImageTk

from moviecolor import ffmpeg_utils

FFMPEG, FFPROBE = ffmpeg_utils.get_ffmpeg_tools()


def get_video_info(video_path, fps=1):
    """Return estimated frame count at the given FPS."""
    dur = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    duration = float(dur.stdout.strip())
    frame_count = int(duration * fps)
    return frame_count


def make_barcode(video_path, fps=1, height=800, preview_update=10, mode="average", bar_width=1):
    """
    Create a movie barcode.

    mode:
        "average" - each bar is the average color of the frame
        "frame"   - each bar is a shrunken version of the actual frame
    bar_width: width of each frame bar (only used for 'frame' mode)
    """
    frame_count = get_video_info(video_path, fps=fps)
    print(f"~{frame_count} frames at {fps} fps, mode={mode}")

    if mode == "average":
        cmd = [
            FFMPEG,
            "-i",
            video_path,
            "-vf",
            f"fps={fps},scale=1:1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "pipe:1",
        ]
        chunk = 3
        barcode_width = frame_count
    elif mode == "frame":
        cmd = [
            FFMPEG,
            "-i",
            video_path,
            "-vf",
            f"fps={fps},scale={bar_width}:{height}",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "pipe:1",
        ]
        chunk = 3 * bar_width * height
        barcode_width = frame_count * bar_width
    else:
        raise ValueError("mode must be 'average' or 'frame'")

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # Tkinter preview
    root = tk.Tk()
    root.title("MovieColor")
    canvas = tk.Label(root)
    canvas.pack()

    barcode = Image.new("RGB", (barcode_width, height), (0, 0, 0))
    frame_index = 0

    while True:
        raw = proc.stdout.read(chunk)
        if not raw or len(raw) < chunk:
            break

        if mode == "average":
            # raw = 3 bytes (R, G, B)
            r, g, b = raw[0], raw[1], raw[2]
            for y in range(height):
                barcode.putpixel((frame_index, y), (r, g, b))
        else:  # frame mode
            frame_img = Image.frombytes("RGB", (bar_width, height), raw)
            barcode.paste(frame_img, (frame_index * bar_width, 0))

        # Update preview
        if frame_index % preview_update == 0 or frame_index == frame_count - 1:
            imgTk = ImageTk.PhotoImage(barcode.resize((800, height // 3)))
            canvas.config(image=imgTk)
            canvas.image = imgTk
            root.update_idletasks()
            root.update()

        frame_index += 1
        if frame_index >= frame_count:
            break

    # Save final barcode
    filename = "barcode_average.jpg" if mode == "average" else "barcode_frame.jpg"
    barcode.save(filename, "JPEG")
    print(f"Saved {filename} with {frame_index} frames")

    root.mainloop()
