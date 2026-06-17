from yt_dlp import YoutubeDL

ydl_opts = {
    'quiet': False,
    'no_warnings': True,
    'js_runtimes': {'node': {}}
}

with YoutubeDL(ydl_opts) as ydl:
    try:
        ydl.download(['https://www.youtube.com/watch?v=aft0Xj1Nm88'])
    except Exception as e:
        print(f"EXCEPTION: {e}")
