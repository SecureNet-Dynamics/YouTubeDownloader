import sys
import csv
from datetime import datetime
from yt_dlp import YoutubeDL

def extract_videos_from_url(url, label=""):
    """Try to extract videos from a given URL."""
    videos = []
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'playlist_items': '1-',
        'skip_unavailable_videos': True,
        'socket_timeout': 30,
        'retries': 3,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"🔍 Trying {label or 'URL'}: {url}")
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry and entry.get('id'):
                        title = entry.get('title', 'Unknown')
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        videos.append((title, video_url))
            else:
                print(f"⚠️ No entries found in {label or url}")
    except Exception as e:
        print(f"❌ Failed to extract from {label or url}: {e}")
    return videos

def get_channel_videos(channel_url):
    """Extract videos and shorts from a YouTube channel."""
    videos = []
    base_urls = []

    if 'youtube.com/@' in channel_url:
        handle = channel_url.split('@')[1].rstrip('/')
        base_urls = [
            (f"https://www.youtube.com/@{handle}/videos", "Videos Tab"),
            (f"https://www.youtube.com/@{handle}/shorts", "Shorts Tab"),
            (f"https://www.youtube.com/@{handle}", "Channel Root"),
        ]
    elif 'youtube.com/c/' in channel_url:
        name = channel_url.split('/c/')[1].rstrip('/')
        base_urls = [
            (f"https://www.youtube.com/c/{name}/videos", "Videos Tab"),
            (f"https://www.youtube.com/c/{name}/shorts", "Shorts Tab"),
            (f"https://www.youtube.com/c/{name}", "Channel Root"),
        ]
    elif 'youtube.com/user/' in channel_url:
        user = channel_url.split('/user/')[1].rstrip('/')
        base_urls = [
            (f"https://www.youtube.com/user/{user}/videos", "Videos Tab"),
            (f"https://www.youtube.com/user/{user}/shorts", "Shorts Tab"),
            (f"https://www.youtube.com/user/{user}", "Channel Root"),
        ]
    else:
        base_urls = [(channel_url, "Provided URL")]

    for url, label in base_urls:
        extracted = extract_videos_from_url(url, label)
        if extracted:
            videos.extend(extracted)

    # Remove duplicates
    unique_videos = list({url: title for title, url in videos}.items())
    return [(title, url) for url, title in unique_videos]

def save_to_csv(videos, output_file=None):
    if not videos:
        print("❌ No videos to save")
        return None

    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"Channel_{timestamp}.csv"

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Title', 'Video Link'])
            writer.writeheader()
            for title, url in videos:
                writer.writerow({'Title': title, 'Video Link': url})
        print(f"\n✅ CSV file created: {output_file}")
        print(f"📊 Total videos saved: {len(videos)}")
        return output_file
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python channel_scraper.py <channel_url> [output_file.csv]")
        sys.exit(1)

    channel_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if 'youtube.com' not in channel_url:
        print("❌ Invalid YouTube URL")
        sys.exit(1)

    videos = get_channel_videos(channel_url)
    if videos:
        csv_file = save_to_csv(videos, output_file)
        if csv_file:
            print("\n📁 You can now use this CSV file in the Bulk YouTube Downloader!")
            sys.exit(0)

    sys.exit(1)

if __name__ == "__main__":
    main()
