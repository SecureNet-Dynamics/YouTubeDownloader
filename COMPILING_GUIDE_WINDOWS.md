# Windows Compiling & Packaging Guide

This guide explains how to compile the `YouTube Studio Pro Downloader` Python script into a standalone Windows Executable (`.exe`) and package it into an installer using **Inno Setup**.

This approach ensures the end-user doesn't need to install Python, `yt-dlp`, or `ffmpeg` manually.

---

## 1. Prerequisites

Before you start on your Windows build machine, ensure you have the following installed:

1. **Python 3.8+**: Installed and added to your System PATH.
2. **Inno Setup**: Download and install from [jrsoftware.org](https://jrsoftware.org/isdl.php).
3. **FFmpeg Windows Builds**: `yt-dlp` requires FFmpeg to merge high-quality video and audio (like 1080p). 
   - Download the essentials build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z).
   - Extract `ffmpeg.exe` and `ffprobe.exe` from the `bin` folder.

## 2. Prepare the Environment

Open Command Prompt or PowerShell and install the required Python dependencies:

```cmd
pip install pandas yt-dlp pyinstaller
```

Create a dedicated build folder, for example, `C:\Build\YouTubeDownloader\`. Place the following files into this folder:
1. `YT-Downloader.py` (The main Python script)
2. `icon.ico` (Your application icon)
3. `ffmpeg.exe` (Downloaded in step 1)
4. `ffprobe.exe` (Downloaded in step 1)

## 3. Compile the Python Script (PyInstaller)

We will use PyInstaller to compile the python script into a single executable. Since `yt-dlp` is a Python module, PyInstaller will automatically package it inside the executable.

Run the following command in your build folder:

```cmd
pyinstaller --noconsole --onefile --icon=icon.ico YT-Downloader.py
```

- `--noconsole`: Hides the background terminal window.
- `--onefile`: Packages the entire Python environment into a single `.exe`.
- `--icon`: Assigns your custom icon to the executable.

Once completed, navigate to the newly created `dist` folder. You will find `YT-Downloader.exe`.

## 4. Package with Inno Setup

To create a professional installer that extracts the executable and `ffmpeg` together (so `yt-dlp` can access FFmpeg), we use Inno Setup.

1. Open **Inno Setup Compiler**.
2. Go to **File -> New** and cancel the wizard.
3. Paste the following script into the editor. 
   *(Make sure to adjust the `Source:` paths to match your actual folders!)*

```pascal
[Setup]
AppName=YouTube Studio Pro
AppVersion=1.0
DefaultDirName={autopf}\YouTube Studio Pro
DefaultGroupName=YouTube Studio Pro
OutputDir=Output
OutputBaseFilename=YouTubeStudioPro_Installer
SetupIconFile=C:\Build\YouTubeDownloader\icon.ico
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
; The main executable
Source: "C:\Build\YouTubeDownloader\dist\YT-Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion

; FFmpeg binaries required by yt-dlp for merging
Source: "C:\Build\YouTubeDownloader\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Build\YouTubeDownloader\ffprobe.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\YouTube Studio Pro"; Filename: "{app}\YT-Downloader.exe"
Name: "{group}\Uninstall YouTube Studio Pro"; Filename: "{uninstallexe}"
Name: "{commondesktop}\YouTube Studio Pro"; Filename: "{app}\YT-Downloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\YT-Downloader.exe"; Description: "Launch YouTube Studio Pro"; Flags: nowait postinstall skipifsilent
```

### 5. Build the Installer
Click the **Compile** button (the green play button) in Inno Setup.

Once it finishes, look inside the `Output` folder (created next to your `.iss` script). You will find `YouTubeStudioPro_Installer.exe`. 

**You're Done!** You can now distribute this single Installer. When a user runs it, it will install the app and FFmpeg seamlessly, providing a desktop shortcut and a perfect `yt-dlp` downloading experience.
