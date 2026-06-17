from yt_dlp import YoutubeDL
ydl_opts = {'quiet': False, 'no_warnings': True}
with YoutubeDL(ydl_opts) as ydl:
    try:
        ydl.download(['https://www.youtube.com/watch?v=dQw4w9WgXcQ'])
    except Exception as e:
        print(f"EXCEPTION: {e}")
