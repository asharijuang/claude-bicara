#!/bin/bash
# Build ClaudeBicara.app — macOS menu bar controller
# Usage: ./make-app.sh [--install]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/dist/ClaudeBicara.app"
INSTALL_DIR="/Applications/ClaudeBicara.app"
PYTHON="/opt/homebrew/opt/python@3.11/bin/python3.11"

echo "🔨 Building ClaudeBicara.app..."

# Create .app structure
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Copy app icon
if [ -f "$SCRIPT_DIR/src/AppIcon.icns" ]; then
    cp "$SCRIPT_DIR/src/AppIcon.icns" "$APP_DIR/Contents/Resources/"
fi
# Write launcher — PYTHONPATH cleared to avoid system 3.9 conflicts
cat > "$APP_DIR/Contents/MacOS/ClaudeBicara" << LAUNCHER
#!/bin/bash
export PYTHONPATH=""
exec $PYTHON "\$HOME/.claude/bicara-menubar.py"
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/ClaudeBicara"

# Write Info.plist
cat > "$APP_DIR/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Claude Bicara</string>
    <key>CFBundleDisplayName</key>
    <string>Claude Bicara</string>
    <key>CFBundleIdentifier</key>
    <string>com.asharijuang.claude-bicara</string>
    <key>CFBundleVersion</key>
    <string>1.1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.1.0</string>
    <key>CFBundleExecutable</key>
    <string>ClaudeBicara</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

echo "✅ Built: $APP_DIR"

# Install to /Applications if requested
if [ "$1" = "--install" ]; then
    echo "📦 Installing to /Applications..."
    rm -rf "$INSTALL_DIR"
    cp -R "$APP_DIR" "$INSTALL_DIR"
    echo "✅ Installed: $INSTALL_DIR"
    echo "   Double-click Claude Bicara in Applications to launch!"
else
    echo "   Run './make-app.sh --install' to copy to /Applications"
fi
