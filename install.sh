#!/usr/bin/env bash
# Cowork Voice Listener installer (macOS)
set -e

echo "=== Cowork Voice Listener Installer ==="
echo ""

# 1. Sanity checks
if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "❌ This installer is for macOS. For Windows/Linux see README.md"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Install Python 3.8+ first."
  exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "⚠️  Ollama not found. Install from https://ollama.com then rerun."
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLAUDE_DIR="$HOME/.claude"
DAEMON_PATH="$CLAUDE_DIR/cowork-listener.py"
PLIST_PATH="$HOME/Library/LaunchAgents/com.cowork-listener.plist"
MODEL="gemma3:1b"

mkdir -p "$CLAUDE_DIR"
mkdir -p "$HOME/Library/LaunchAgents"

# 2. Copy daemon
echo "📦 Installing daemon to $DAEMON_PATH"
cp "$SCRIPT_DIR/src/cowork-listener.py" "$DAEMON_PATH"
chmod +x "$DAEMON_PATH"

# 3. Install Python deps
echo "📦 Installing Python dependency: requests"
python3 -m pip install --user requests --quiet || true

# 4. Pull Ollama model if missing
if ! ollama list | grep -q "$MODEL"; then
  echo "🧠 Pulling Ollama model: $MODEL (~777 MB, one-time download)"
  ollama pull "$MODEL"
else
  echo "✓ Ollama model $MODEL already present"
fi

# 5. Generate plist
PY_SITE="$(python3 -c 'import site; print(site.getusersitepackages())')"
cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cowork-listener</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$DAEMON_PATH</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CLAUDE_DIR/cowork-listener.log</string>
    <key>StandardErrorPath</key>
    <string>$CLAUDE_DIR/cowork-listener-error.log</string>
    <key>Environment</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>PYTHONPATH</key>
        <string>$PY_SITE</string>
    </dict>
    <key>WorkingDirectory</key>
    <string>$HOME</string>
</dict>
</plist>
PLIST

# Validate plist
plutil -lint "$PLIST_PATH" >/dev/null

# 6. (Re)load
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo ""
echo "✅ Install complete!"
echo ""
echo "Status:   launchctl list | grep cowork-listener"
echo "Logs:     tail -f ~/.claude/cowork-listener.log"
echo "Stop:     launchctl unload $PLIST_PATH"
echo "Start:    launchctl load   $PLIST_PATH"
echo ""
echo "Open Claude Cowork and send a message — you should hear a summary spoken aloud."
