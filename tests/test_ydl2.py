from yt_dlp import YoutubeDL
import os

ydl_opts = {
    'quiet': False,
    'no_warnings': True,
}

with YoutubeDL(ydl_opts) as ydl:
    try:
        ydl.download(['ytsearch1:Hazrat Yusuf A.S Episode 29 H.D URDU DUBBED'])
    except Exception as e:
        print(f"EXCEPTION: {e}")
