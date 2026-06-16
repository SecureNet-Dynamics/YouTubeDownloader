[Setup]
AppName=YouTube Studio Pro
AppVersion=1.0
DefaultDirName={autopf}\YouTube Studio Pro
DefaultGroupName=YouTube Studio Pro
OutputDir=Output
OutputBaseFilename=YouTubeStudioPro_Installer
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
; "SourceDir=." is the default, so paths are relative to the location of the .iss file

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
; The main executable (assuming it was built via PyInstaller in the dist folder)
Source: "dist\YT-Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion

; FFmpeg binaries required by yt-dlp for merging video and audio formats
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffprobe.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\YouTube Studio Pro"; Filename: "{app}\YT-Downloader.exe"
Name: "{group}\Uninstall YouTube Studio Pro"; Filename: "{uninstallexe}"
Name: "{commondesktop}\YouTube Studio Pro"; Filename: "{app}\YT-Downloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\YT-Downloader.exe"; Description: "Launch YouTube Studio Pro"; Flags: nowait postinstall skipifsilent
