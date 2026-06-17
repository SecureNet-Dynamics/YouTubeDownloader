from yt_dlp import YoutubeDL
import os

quality_map = {
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "Best Available": "bestvideo+bestaudio/best"
}

ydl_opts = {
    'outtmpl': os.path.join('/home/sadaqaty/Projects/YouTubeDownloader/test', '%(title)s.%(ext)s'),
    'format': quality_map.get("720p", "bestvideo[height<=720]+bestaudio/best[height<=720]"),
    'merge_output_format': "mp4",
    'quiet': False,
    'no_warnings': True,
    'nooverwrites': True,
    'extractor_args': {'youtube': ['player_client=android,web']}
}

class MyLogger:
    def debug(self, msg):
        print(f"DEBUG: {msg}")
    def info(self, msg):
        print(f"INFO: {msg}")
    def warning(self, msg):
        print(f"WARNING: {msg}")
    def error(self, msg):
        print(f"ERROR: {msg}")

ydl_opts['logger'] = MyLogger()

# Since I don't know the exact URL, let me search for the video title on YouTube and get its URL.
# Actually I can just search for "Hazrat Yusuf A.S Episode 29 H.D ｜ URDU DUBBED"
with YoutubeDL(ydl_opts) as ydl:
    try:
        ydl.download(['ytsearch1:Hazrat Yusuf A.S Episode 29 H.D URDU DUBBED'])
    except Exception as e:
        print(f"EXCEPTION: {e}")
