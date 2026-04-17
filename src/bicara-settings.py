#!/usr/bin/env python3
"""
Claude Bicara — Settings Window (tkinter)
Tabbed UI for tone editor, TTS config, API keys.
Launched from menu bar app or standalone.
"""

import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

CONFIG_PATH = os.path.expanduser("~/.claude/bicara-config.json")
ENV_PATH = os.path.expanduser("~/.claude/.env")
LOG_PATH = os.path.expanduser("~/.claude/cowork-listener.log")
PLIST = os.path.expanduser(
    "~/Library/LaunchAgents/com.asharijuang.cowork-listener.plist"
)

TTS_BACKENDS = ["elevenlabs", "gemini", "piper", "system"]

DEFAULT_TONES = {
    "casual": "Ringkas teks ini seperti sedang ngobrol santai di telepon ke teman.\nAturan:\n- Maksimal 1-2 kalimat pendek\n- Bahasa Indonesia casual, natural\n- Skip detail teknis, command, code, link\n- Fokus ke pesan inti saja\n- Tanpa emoji, tanpa markdown",
    "formal": "Ringkas teks berikut dengan gaya profesional dan formal.\nAturan:\n- Maksimal 1-2 kalimat\n- Bahasa Indonesia baku, jelas, to-the-point\n- Hindari slang\n- Tanpa emoji, tanpa markdown",
    "cute": "Ringkas teks ini dengan gaya super imut~\nAturan:\n- Maksimal 1-2 kalimat\n- Bahasa Indonesia casual dengan sentuhan imut\n- Tanpa emoji, tanpa markdown",
    "anime": "Ringkas teks ini dengan energi anime-sensei!\nAturan:\n- Maksimal 1-2 kalimat\n- Bahasa Indonesia + selipan kata Jepang ringan\n- Energik dan bersemangat\n- Tanpa emoji, tanpa markdown",
    "news": "Ringkas teks ini seperti presenter berita.\nAturan:\n- Maksimal 1-2 kalimat\n- Bahasa Indonesia baku dan netral\n- Tanpa emoji, tanpa markdown",
    "senpai": "Ringkas teks ini dengan gaya kouhai wibu gaul.\nAturan:\n- Maksimal 2-3 kalimat\n- Campur Indonesia gaul + Jepang romaji\n- Tanpa emoji, tanpa markdown",
}

DEFAULT_CONFIG = {
    "muted": False,
    "tone": "senpai",
    "tts_backend": "elevenlabs",
    "tone_prompts": DEFAULT_TONES,
}


def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
    except Exception:
        pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


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
        subprocess.run(["launchctl", "unload", PLIST], capture_output=True, timeout=5)
        subprocess.run(["launchctl", "load", PLIST], capture_output=True, timeout=5)
        return True
    except Exception:
        return False


class SettingsApp:
    def __init__(self):
        self.cfg = load_config()
        self.env = load_env()
        self.tone_widgets = {}  # name -> Text widget

        self.root = tk.Tk()
        self.root.title("Claude Bicara Settings")
        self.root.geometry("620x520")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#1a1a2e")
        style.configure("TNotebook.Tab", padding=[12, 6],
                         font=("Helvetica", 12))
        style.configure("TFrame", background="#2a2a3e")
        style.configure("TLabel", background="#2a2a3e",
                         foreground="#e0e0e0", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("TCheckbutton", background="#2a2a3e",
                         foreground="#e0e0e0", font=("Helvetica", 12))

        # Header
        hdr = tk.Label(self.root, text="🎙️ Claude Bicara",
                        font=("Helvetica", 18, "bold"),
                        bg="#1a1a2e", fg="#7c3aed")
        hdr.pack(pady=(10, 2))
        sub = tk.Label(self.root, text="Settings & Control Panel",
                        font=("Helvetica", 11), bg="#1a1a2e", fg="#888")
        sub.pack(pady=(0, 8))

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        self._build_general_tab()
        self._build_tone_tab()
        self._build_keys_tab()
        self._build_log_tab()

        # Bottom save bar
        bar = tk.Frame(self.root, bg="#1a1a2e")
        bar.pack(fill="x", padx=10, pady=(0, 10))
        tk.Button(bar, text="💾  Save & Apply", bg="#7c3aed", fg="white",
                  font=("Helvetica", 12, "bold"), relief="flat", padx=16,
                  pady=6, command=self.save_all).pack(side="left")
        tk.Button(bar, text="🔄  Restart Daemon", bg="#333", fg="#ccc",
                  font=("Helvetica", 12), relief="flat", padx=12,
                  pady=6, command=self.do_restart).pack(side="left", padx=8)
        self.status_label = tk.Label(bar, text="", bg="#1a1a2e",
                                      fg="#16a34a", font=("Helvetica", 11))
        self.status_label.pack(side="right")


    def _build_general_tab(self):
        f = ttk.Frame(self.notebook)
        self.notebook.add(f, text="  General  ")

        # Mute toggle
        self.mute_var = tk.BooleanVar(value=self.cfg.get("muted", False))
        ttk.Checkbutton(f, text="  Mute voice output",
                         variable=self.mute_var).pack(anchor="w", padx=16, pady=(16, 8))

        # Tone selector
        ttk.Label(f, text="Active Tone:").pack(anchor="w", padx=16, pady=(8, 2))
        self.tone_var = tk.StringVar(value=self.cfg.get("tone", "senpai"))
        tones = list(self.cfg.get("tone_prompts", DEFAULT_TONES).keys())
        self.tone_combo = ttk.Combobox(f, textvariable=self.tone_var,
                                        values=tones, state="readonly",
                                        font=("Helvetica", 12))
        self.tone_combo.pack(fill="x", padx=16, pady=(0, 8))

        # TTS Backend
        ttk.Label(f, text="TTS Backend:").pack(anchor="w", padx=16, pady=(8, 2))
        self.tts_var = tk.StringVar(value=self.cfg.get("tts_backend", "elevenlabs"))
        ttk.Combobox(f, textvariable=self.tts_var, values=TTS_BACKENDS,
                      state="readonly", font=("Helvetica", 12)
                      ).pack(fill="x", padx=16, pady=(0, 8))

        # Info
        ttk.Label(f, text="Fallback: elevenlabs → gemini → piper → system",
                   foreground="#666").pack(anchor="w", padx=16, pady=(4, 0))


    def _build_tone_tab(self):
        f = ttk.Frame(self.notebook)
        self.notebook.add(f, text="  Tone Editor  ")

        # Add new tone bar
        top = tk.Frame(f, bg="#2a2a3e")
        top.pack(fill="x", padx=12, pady=(12, 4))
        self.new_tone_entry = tk.Entry(top, font=("Helvetica", 12),
                                        bg="#1a1a2e", fg="#e0e0e0",
                                        insertbackground="#e0e0e0")
        self.new_tone_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.new_tone_entry.insert(0, "new tone name...")
        self.new_tone_entry.bind("<FocusIn>",
            lambda e: self.new_tone_entry.delete(0, "end")
            if self.new_tone_entry.get() == "new tone name..." else None)
        tk.Button(top, text="+ Add", bg="#16a34a", fg="white",
                  font=("Helvetica", 11), relief="flat",
                  command=self.add_tone).pack(side="right")

        # Scrollable tone list
        canvas = tk.Canvas(f, bg="#2a2a3e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(f, orient="vertical", command=canvas.yview)
        self.tone_frame = tk.Frame(canvas, bg="#2a2a3e")
        self.tone_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.tone_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=12, pady=4)
        scrollbar.pack(side="right", fill="y", pady=4)

        # Populate tones
        tones = self.cfg.get("tone_prompts", DEFAULT_TONES)
        for name, prompt in tones.items():
            self._add_tone_widget(name, prompt)


    def _add_tone_widget(self, name, prompt=""):
        block = tk.Frame(self.tone_frame, bg="#1a1a2e", relief="flat", bd=1)
        block.pack(fill="x", pady=4, padx=4)

        header = tk.Frame(block, bg="#1a1a2e")
        header.pack(fill="x")
        tk.Label(header, text=f"  {name}", font=("Helvetica", 12, "bold"),
                 bg="#1a1a2e", fg="#7c3aed").pack(side="left")
        tk.Button(header, text="✕", bg="#dc2626", fg="white",
                  font=("Helvetica", 10), relief="flat", width=3,
                  command=lambda n=name, b=block: self.delete_tone(n, b)
                  ).pack(side="right", padx=4, pady=2)

        txt = tk.Text(block, height=5, font=("Menlo", 11), bg="#222",
                       fg="#e0e0e0", insertbackground="#e0e0e0",
                       wrap="word", relief="flat", padx=8, pady=6)
        txt.insert("1.0", prompt)
        txt.pack(fill="x", padx=6, pady=(0, 6))
        self.tone_widgets[name] = txt

    def add_tone(self):
        name = self.new_tone_entry.get().strip().lower().replace(" ", "_")
        if not name or name == "new tone name...":
            return
        if name in self.tone_widgets:
            messagebox.showwarning("Exists", f"Tone '{name}' already exists")
            return
        self._add_tone_widget(name, "")
        self.new_tone_entry.delete(0, "end")
        # Update combo
        vals = list(self.tone_combo["values"]) + [name]
        self.tone_combo["values"] = vals

    def delete_tone(self, name, block):
        if not messagebox.askyesno("Delete", f"Delete tone '{name}'?"):
            return
        block.destroy()
        self.tone_widgets.pop(name, None)
        vals = [v for v in self.tone_combo["values"] if v != name]
        self.tone_combo["values"] = vals
        if self.tone_var.get() == name and vals:
            self.tone_var.set(vals[0])


    def _build_keys_tab(self):
        f = ttk.Frame(self.notebook)
        self.notebook.add(f, text="  API Keys  ")

        ttk.Label(f, text="ElevenLabs API Key:").pack(
            anchor="w", padx=16, pady=(16, 2))
        self.el_key_var = tk.StringVar(
            value=self.env.get("ELEVENLABS_API_KEY", ""))
        tk.Entry(f, textvariable=self.el_key_var, show="•",
                 font=("Helvetica", 12), bg="#1a1a2e", fg="#e0e0e0",
                 insertbackground="#e0e0e0").pack(
            fill="x", padx=16, pady=(0, 8))

        ttk.Label(f, text="ElevenLabs Voice ID:").pack(
            anchor="w", padx=16, pady=(4, 2))
        self.voice_var = tk.StringVar(
            value=self.env.get("ELEVENLABS_VOICE_ID", ""))
        tk.Entry(f, textvariable=self.voice_var,
                 font=("Helvetica", 12), bg="#1a1a2e", fg="#e0e0e0",
                 insertbackground="#e0e0e0").pack(
            fill="x", padx=16, pady=(0, 8))

        ttk.Label(f, text="Gemini API Key:").pack(
            anchor="w", padx=16, pady=(4, 2))
        self.gm_key_var = tk.StringVar(
            value=self.env.get("GEMINI_API_KEY", ""))
        tk.Entry(f, textvariable=self.gm_key_var, show="•",
                 font=("Helvetica", 12), bg="#1a1a2e", fg="#e0e0e0",
                 insertbackground="#e0e0e0").pack(
            fill="x", padx=16, pady=(0, 8))

        ttk.Label(f, text="Keys are stored in ~/.claude/.env (gitignored)",
                   foreground="#666").pack(anchor="w", padx=16, pady=(8, 0))


    def _build_log_tab(self):
        f = ttk.Frame(self.notebook)
        self.notebook.add(f, text="  Logs  ")

        top = tk.Frame(f, bg="#2a2a3e")
        top.pack(fill="x", padx=12, pady=(12, 4))
        ttk.Label(top, text="Last 40 lines").pack(side="left")
        tk.Button(top, text="🔄 Refresh", bg="#333", fg="#ccc",
                  font=("Helvetica", 11), relief="flat",
                  command=self.refresh_log).pack(side="right")

        self.log_text = scrolledtext.ScrolledText(
            f, font=("Menlo", 10), bg="#111", fg="#8f8",
            insertbackground="#8f8", wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.refresh_log()

    def refresh_log(self):
        try:
            with open(LOG_PATH) as fh:
                lines = fh.readlines()[-40:]
            text = "".join(lines)
        except Exception:
            text = "(no log)"
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", text)
        self.log_text.configure(state="disabled")
        self.log_text.see("end")


    def save_all(self):
        # Collect tone prompts from widgets
        tone_prompts = {}
        for name, widget in self.tone_widgets.items():
            tone_prompts[name] = widget.get("1.0", "end-1c")

        self.cfg["muted"] = self.mute_var.get()
        self.cfg["tone"] = self.tone_var.get()
        self.cfg["tts_backend"] = self.tts_var.get()
        self.cfg["tone_prompts"] = tone_prompts
        save_config(self.cfg)

        # Save API keys to .env
        env = load_env()
        el = self.el_key_var.get().strip()
        if el:
            env["ELEVENLABS_API_KEY"] = el
        vid = self.voice_var.get().strip()
        if vid:
            env["ELEVENLABS_VOICE_ID"] = vid
        gm = self.gm_key_var.get().strip()
        if gm:
            env["GEMINI_API_KEY"] = gm
        save_env(env)

        self.flash_status("✅ Saved & Applied!")

    def do_restart(self):
        if restart_daemon():
            self.flash_status("✅ Daemon Restarted!")
        else:
            self.flash_status("❌ Restart Failed")

    def flash_status(self, msg):
        self.status_label.configure(text=msg)
        self.root.after(3000, lambda: self.status_label.configure(text=""))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    SettingsApp().run()

