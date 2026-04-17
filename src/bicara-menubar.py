#!/usr/bin/env python3
"""
Claude Bicara — macOS Menu Bar Controller
Controls the cowork-listener daemon: tone, mute, TTS backend, API keys.
"""

import os
import json
import subprocess
import rumps

CONFIG_PATH = os.path.expanduser("~/.claude/bicara-config.json")
ENV_PATH = os.path.expanduser("~/.claude/.env")
PLIST_PATH = os.path.expanduser(
    "~/Library/LaunchAgents/com.asharijuang.cowork-listener.plist"
)

DEFAULT_CONFIG = {
    "muted": False,
    "tone": "senpai",
    "tts_backend": "elevenlabs",
    "tts_fallback_order": ["elevenlabs", "gemini", "piper", "system"],
}

TONES = ["casual", "formal", "cute", "anime", "news", "senpai"]
TTS_BACKENDS = ["elevenlabs", "gemini", "piper", "system"]


def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            # Merge with defaults for any missing keys
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
    except Exception:
        pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def save_env(env):
    with open(ENV_PATH, "w") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")



def restart_daemon():
    try:
        subprocess.run(["launchctl", "unload", PLIST_PATH],
                       capture_output=True, timeout=5)
        subprocess.run(["launchctl", "load", PLIST_PATH],
                       capture_output=True, timeout=5)
        return True
    except Exception:
        return False


def is_daemon_running():
    try:
        r = subprocess.run(["launchctl", "list"],
                           capture_output=True, text=True, timeout=5)
        return "cowork-listener" in r.stdout
    except Exception:
        return False



class BicaraMenuBar(rumps.App):
    def __init__(self):
        self.cfg = load_config()
        icon_title = "🔇" if self.cfg["muted"] else "🎙️"
        super().__init__(icon_title, quit_button=None)

        # --- Mute toggle ---
        mute_label = "🔊 Unmute" if self.cfg["muted"] else "🔇 Mute"
        self.mute_item = rumps.MenuItem(mute_label, callback=self.toggle_mute)
        
        # --- Tone submenu ---
        self.tone_menu = rumps.MenuItem("🎭 Tone")
        for t in TONES:
            item = rumps.MenuItem(t, callback=self.set_tone)
            item.state = t == self.cfg["tone"]
            self.tone_menu.add(item)

        # --- TTS Backend submenu ---
        self.tts_menu = rumps.MenuItem("🔊 TTS Backend")
        for b in TTS_BACKENDS:
            item = rumps.MenuItem(b, callback=self.set_tts)
            item.state = b == self.cfg["tts_backend"]
            self.tts_menu.add(item)

        # --- Settings window ---
        self.settings_item = rumps.MenuItem("⚙️ Settings...", callback=self.open_settings)

        # --- Daemon control ---
        self.daemon_menu = rumps.MenuItem("⚙️ Daemon")
        self.daemon_menu.add(rumps.MenuItem("Restart", callback=self.do_restart))
        self.daemon_menu.add(rumps.MenuItem("View Log", callback=self.view_log))
        status = "Running ✅" if is_daemon_running() else "Stopped ❌"
        self.status_item = rumps.MenuItem(f"Status: {status}")
        self.status_item.set_callback(None)
        self.daemon_menu.add(self.status_item)

        # --- Quit ---
        self.quit_item = rumps.MenuItem("Quit Bicara Menu", callback=self.do_quit)

        self.menu = [
            self.mute_item,
            None,
            self.tone_menu,
            self.tts_menu,
            None,
            self.settings_item,
            self.daemon_menu,
            None,
            self.quit_item,
        ]


    def _apply_config(self):
        """Write config JSON and restart daemon to pick up changes."""
        save_config(self.cfg)
        restart_daemon()
        # Update icon
        self.title = "🔇" if self.cfg["muted"] else "🎙️"

    def toggle_mute(self, sender):
        self.cfg["muted"] = not self.cfg["muted"]
        sender.title = "🔊 Unmute" if self.cfg["muted"] else "🔇 Mute"
        self._apply_config()
        state = "Muted" if self.cfg["muted"] else "Unmuted"
        rumps.notification("Claude Bicara", "", f"Voice {state}")

    def set_tone(self, sender):
        self.cfg["tone"] = sender.title
        for item in self.tone_menu.values():
            item.state = item.title == sender.title
        self._apply_config()

    def set_tts(self, sender):
        self.cfg["tts_backend"] = sender.title
        for item in self.tts_menu.values():
            item.state = item.title == sender.title
        self._apply_config()


    def open_settings(self, _):
        settings_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "bicara-settings.py"
        )
        if not os.path.exists(settings_script):
            settings_script = os.path.expanduser("~/.claude/bicara-settings.py")
        subprocess.Popen(["python3", settings_script])

    def do_restart(self, _):
        if restart_daemon():
            rumps.notification("Claude Bicara", "", "Daemon restarted")
            self.status_item.title = "Status: Running ✅"
        else:
            rumps.notification("Claude Bicara", "", "Restart failed")

    def view_log(self, _):
        log_path = os.path.expanduser("~/.claude/cowork-listener.log")
        subprocess.Popen(["open", "-a", "Console", log_path])

    def do_quit(self, _):
        rumps.quit_application()


if __name__ == "__main__":
    BicaraMenuBar().run()

