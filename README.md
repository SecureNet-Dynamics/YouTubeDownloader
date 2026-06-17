# YouTube Studio Pro

A comprehensive Python application for scraping YouTube video metadata and performing bulk downloads. Features a modern, unified GUI that easily handles playlists, channels, and individual videos.

## Features

- **🔍 Intelligent Video Fetching**: Automatically scrape and list videos from channels, playlists, or individual links.
  - Option to include or exclude YouTube Shorts.
  - Set limits on the maximum number of videos to fetch.
  - Bypass YouTube's anti-bot mechanisms using browser cookies (supports Chrome, Firefox, Edge, Brave, Safari, Opera, Vivaldi).

- **⬇️ Advanced Bulk Downloader**: Download multiple YouTube videos with precision.
  - Customizable output directories and file formats (mp4, mkv, webm).
  - Select video quality (1080p, 720p, 480p, 360p, or Best Available).
  - Real-time progress tracking within the UI.
  - Auto-skips previously downloaded files to allow pausing and resuming bulk lists.
  
- **Auto-Bootstrapping**: The script will automatically prompt to install missing dependencies via `pip` on startup, making it extremely easy to run across environments.

## Download & Installation

You do not need to install Python or any dependencies to use YouTube Studio Pro! 

1. Go to the **Releases** page of this repository.
2. Download the appropriate version for your operating system:
   - **Windows**: Download the `.exe` file.
   - **Linux**: Download the `.AppImage` file.
3. Run the downloaded file directly.

*(Note: If you wish to build the application from source, please refer to [BUILD.md](BUILD.md))*

## Usage

### Typical Workflow

1. **Fetch Videos**: Enter a YouTube URL (Channel, Playlist, or Video) in section 1. 
2. **Browser Cookies (Anti-Bot Bypass)**: If you are downloading many videos, YouTube may block your IP address. Select your primary browser from the `Browser Cookies` dropdown to authenticate `yt-dlp` and bypass bot checks. Ensure the selected browser is fully closed before fetching/downloading.
3. **Configure Settings**: Select your download folder, preferred format, and resolution.
4. **Download**: Click "Download All" to begin the bulk download process. You can also export the scraped video metadata directly to a CSV file.

## License

This project is provided as-is for personal use.

## Disclaimer

This tool is for educational purposes. Users are responsible for complying with YouTube's Terms of Service and respecting content creator rights when downloading videos.
