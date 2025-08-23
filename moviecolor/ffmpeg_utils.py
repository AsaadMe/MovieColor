import os
import platform
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path


def download_with_progress(url: str, dest: Path):
    """Download a file with progress bar."""

    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = int(downloaded * 100 / total_size) if total_size > 0 else 0
        bar_len = 40
        filled_len = int(bar_len * percent // 100)
        bar = "=" * filled_len + "-" * (bar_len - filled_len)
        sys.stdout.write(f"\r[{bar}] {percent}%")
        sys.stdout.flush()

    print(f"⬇ Downloading {url}")
    urllib.request.urlretrieve(url, dest, reporthook)
    print("\n✅ Download complete.")


def get_ffmpeg_tools():
    """Return paths to ffmpeg and ffprobe, downloading if needed."""
    ffmpeg_sys = shutil.which("ffmpeg")
    ffprobe_sys = shutil.which("ffprobe")
    if ffmpeg_sys and ffprobe_sys:
        return ffmpeg_sys, ffprobe_sys

    ffmpeg_dir = Path.home() / ".moviecolor" / "ffmpeg"
    ffmpeg_bin = ffmpeg_dir / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    ffprobe_bin = ffmpeg_dir / ("ffprobe.exe" if os.name == "nt" else "ffprobe")

    if ffmpeg_bin.exists() and ffprobe_bin.exists():
        return str(ffmpeg_bin), str(ffprobe_bin)

    print("ffmpeg/ffprobe not found. Downloading prebuilt binaries...")
    ffmpeg_dir.mkdir(parents=True, exist_ok=True)

    system = platform.system().lower()
    if system == "windows":
        url = "https://github.com/GyanD/codexffmpeg/releases/download/8.0/ffmpeg-8.0-essentials_build.zip"
        zip_path = ffmpeg_dir / "ffmpeg.zip"
        download_with_progress(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(ffmpeg_dir)
        extracted_ffmpeg = next(ffmpeg_dir.glob("ffmpeg-*/bin/ffmpeg.exe"))
        extracted_ffprobe = next(ffmpeg_dir.glob("ffmpeg-*/bin/ffprobe.exe"))
        extracted_ffmpeg.replace(ffmpeg_bin)
        extracted_ffprobe.replace(ffprobe_bin)

    elif system == "linux":
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        tar_path = ffmpeg_dir / "ffmpeg.tar.xz"
        urllib.request.urlretrieve(url, tar_path)
        with tarfile.open(tar_path, "r:xz") as t:
            t.extractall(ffmpeg_dir)
        extracted_ffmpeg = next(ffmpeg_dir.glob("ffmpeg-*/ffmpeg"))
        extracted_ffprobe = next(ffmpeg_dir.glob("ffmpeg-*/ffprobe"))
        extracted_ffmpeg.replace(ffmpeg_bin)
        extracted_ffprobe.replace(ffprobe_bin)

    elif system == "darwin":  # macOS
        url = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.1.zip"
        zip_path = ffmpeg_dir / "ffmpeg.zip"
        download_with_progress(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(ffmpeg_dir)
        extracted_ffmpeg = ffmpeg_dir / "ffmpeg"
        extracted_ffmpeg.replace(ffmpeg_bin)

        if not ffprobe_bin.exists():
            print("⚠ ffprobe missing. Please install with: brew install ffmpeg")
            sys.exit(1)
    else:
        print("Unsupported OS. Please install ffmpeg manually.")
        sys.exit(1)

    # Set permissions
    if ffmpeg_bin.exists():
        os.chmod(ffmpeg_bin, 0o755)
    if ffprobe_bin.exists():
        os.chmod(ffprobe_bin, 0o755)

    return str(ffmpeg_bin), str(ffprobe_bin)
