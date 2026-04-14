#!/usr/bin/env bash
# Cowork Voice Listener uninstaller
set -e

PLIST_PATH="$HOME/Library/LaunchAgents/com.cowork-listener.plist"

echo "=== Cowork Voice Listener Uninstaller ==="

if [[ -f "$PLIST_PATH" ]]; then
  echo "Unloading launchd agent…"
  launchctl unload "$PLIST_PATH" 2>/dev/null || true
  rm -f "$PLIST_PATH"
fi

pkill -f cowork-listener.py 2>/dev/null || true

rm -f "$HOME/.claude/cowork-listener.py"
rm -f "$HOME/.claude/cowork-listener.log"
rm -f "$HOME/.claude/cowork-listener-error.log"
rm -f "$HOME/.claude/.cowork_last_spoken"

echo "✅ Uninstalled. The Ollama model is kept — remove it with: ollama rm gemma3:1b"
