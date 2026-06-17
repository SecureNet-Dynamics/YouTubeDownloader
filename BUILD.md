# Building YouTube Studio Pro

This guide explains how to compile YouTube Studio Pro into a standalone executable for Linux and Windows. 

## Requirements

- Python 3.7+
- **Node.js** (Required by `yt-dlp` to successfully decrypt YouTube's complex video signatures).
- Core Python Dependencies:
  - `yt-dlp`
  - `pandas`

## Linux (AppImage)

An automated bash script is provided to compile the application into a highly portable Linux AppImage.

```bash
chmod +x build_appimage.sh
./build_appimage.sh
```
The script will run PyInstaller, structure the `.AppDir`, configure the desktop icon, and compile a single `YouTubeStudioPro-x86_64.AppImage` file.

## Windows (.exe)

You can build a Windows standalone executable using PyInstaller with the provided spec file:

```cmd
pyinstaller YouTubeDownloader.spec
```
The compiled executable will be placed in the `dist/` directory.
