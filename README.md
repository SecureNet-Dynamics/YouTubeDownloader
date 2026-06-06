# YouTube Studio Pro

A comprehensive Python application for downloading YouTube videos and scraping channel data. Features a modern GUI with tab-based interface for channel scraping and bulk video downloading.

## Features

- **📹 Channel Scraper**: Extract video metadata from YouTube channels
  - Scrape videos and shorts from channel pages
  - Extract video URLs and titles
  - Support for both custom handles and channel IDs
  - Export data to CSV format

- **⬇️ Bulk Downloader**: Download multiple YouTube videos
  - Batch download videos from URLs
  - Customizable output directory
  - Download progress tracking
  - Support for various video formats

- **Modern GUI**: User-friendly tkinter-based interface
  - Tabbed interface for easy navigation
  - Status updates and progress indicators
  - Error handling and notifications

## Requirements

- Python 3.7+
- Dependencies:
  - `yt-dlp`: YouTube content extraction and downloading
  - `pandas`: Data manipulation and analysis
  - `tkinter`: GUI framework (included with Python)

## Installation

1. Clone or download this repository

2. Install required dependencies:
   ```bash
   pip install yt-dlp pandas
   ```

3. Ensure Python 3.7+ is installed on your system

## Usage

### Running the Application

Run the main application with:
```bash
python YT-Downloader.py
```

The GUI will open with two tabs:
- **Channel Scraper**: Enter a YouTube channel URL to scrape video metadata
- **Bulk Downloader**: Enter video URLs to download content

### Channel Scraper Tab

1. Enter a YouTube channel URL (e.g., `https://www.youtube.com/@channelname`)
2. Click "Scrape Channel" to extract video data
3. Preview results in the interface
4. Export results to CSV file

### Bulk Downloader Tab

1. Enter YouTube video URLs (one per line)
2. Select output directory for downloads
3. Click "Download Videos" to start batch downloading
4. Monitor progress in real-time

## File Descriptions

- **YT-Downloader.py**: Main GUI application entry point
- **channel_scraper.py**: Core logic for scraping YouTube channel data
- **TutaCuteArt.csv**: Sample data file with video metadata
- **YouTubeDownloader.spec**: PyInstaller configuration for executable compilation

## Data Files

- **TutaCuteArt-CSV-Files/**: Directory containing exported channel metadata (CSV files)
- **TutaCuteArt-Vids/**: Directory for downloaded video files

## Building Executable

To create a standalone executable using PyInstaller:

```bash
pyinstaller YouTubeDownloader.spec
```

The compiled executable will be available in the `dist/` directory.

## Notes

- Requires internet connection for YouTube access
- Respect YouTube's Terms of Service when downloading content
- Downloaded content is saved in the specified output directory
- CSV exports contain video titles and URLs for future reference

## License

This project is provided as-is for personal use.

## Disclaimer

This tool is for educational purposes. Users are responsible for complying with YouTube's Terms of Service and respecting content creator rights when downloading videos.
