#!/bin/bash
set -e

echo "======================================"
echo " YouTube Studio Pro AppImage Builder"
echo "======================================"

# 1. Install necessary build dependencies
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing via pip..."
    python3 -m pip install pyinstaller
fi

# 2. Build Standalone Binary
echo "Running PyInstaller..."
# We use the existing YouTubeDownloader.spec if it exists, otherwise command line
if [ -f "YouTubeDownloader.spec" ]; then
    pyinstaller YouTubeDownloader.spec
else
    pyinstaller --onefile --windowed --name YouTubeDownloader YT-Downloader.py
fi

# 3. Create AppDir Structure
echo "Preparing AppDir structure..."
APPDIR="AppDir"
mkdir -p "$APPDIR/usr/bin"
cp dist/YouTubeDownloader "$APPDIR/usr/bin/"

# 4. Handle Icon (Convert .ico to .png)
echo "Setting up Icon..."
if command -v convert &> /dev/null && [ -f "icon.ico" ]; then
    # Extract the first frame of the ico to use as the icon.png
    convert icon.ico[0] "$APPDIR/icon.png"
    ICON_NAME="icon"
elif [ -f "icon.ico" ]; then
    # Fallback to just copying the ico if ImageMagick is not available
    cp icon.ico "$APPDIR/icon.png"
    ICON_NAME="icon"
else
    # Fallback missing icon
    echo "Warning: icon.ico not found."
    ICON_NAME="utilities-terminal"
fi

# 5. Create Desktop Entry
echo "Creating .desktop file..."
cat << EOF > "$APPDIR/YouTubeDownloader.desktop"
[Desktop Entry]
Type=Application
Name=YouTube Studio Pro
Exec=YouTubeDownloader
Icon=$ICON_NAME
Categories=Utility;Video;AudioVideo;
Terminal=false
EOF

# 6. Create AppRun Execution Script
echo "Creating AppRun script..."
cat << 'EOF' > "$APPDIR/AppRun"
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/YouTubeDownloader" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# 7. Download AppImageTool
APPIMAGETOOL="appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Downloading appimagetool..."
    wget -qO "$APPIMAGETOOL" "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

# 8. Package the AppImage
echo "Packaging the AppImage..."
# We extract it and run it extracted to avoid FUSE dependency issues on some Linux systems
./"$APPIMAGETOOL" --appimage-extract > /dev/null
./squashfs-root/AppRun "$APPDIR" YouTubeStudioPro-x86_64.AppImage

# 9. Cleanup
echo "Cleaning up temporary build files..."
rm -rf "$APPDIR" squashfs-root

echo "======================================"
echo "✅ Build Complete!"
echo "Your executable is: YouTubeStudioPro-x86_64.AppImage"
echo "======================================"
