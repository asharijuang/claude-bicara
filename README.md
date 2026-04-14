# 🎙️ Cowork Voice Listener

Listen to Claude Cowork responses hands-free — a tiny background daemon that watches your Cowork session, asks a local Ollama model to summarize each reply into a short, phone-conversation-style sentence, and reads it out loud with your OS's built-in TTS.

**Everything runs locally.** No cloud calls. No API keys. No data leaves your machine.

> _"Jadi kamu bisa lanjut ngoding, scroll dokumen, atau ngopi santai — sambil tetap dengerin apa yang Claude lagi kerjakan."_

---

## ✨ Features

- **Automatic monitoring** — watches the latest Cowork session transcript (`.jsonl`)
- **Local summarization** — uses Ollama (`gemma3:1b` by default, ~777 MB, super fast)
- **Natural speech** — strips emojis, markdown, and code blocks before speaking
- **Conversational tone** — summaries sound like a friend calling you on the phone
- **Cross-platform TTS** — macOS (`say`), Windows (SAPI), Linux (`espeak`)
- **Auto-start on boot** — via `launchd` on macOS
- **Deduped by hash** — never speaks the same response twice

---

## 📦 Requirements

- **Claude Desktop** with Cowork mode
- **[Ollama](https://ollama.com)** running locally
- **Python 3.8+** with `requests` package
- macOS 11+ (tested), Windows 10+, or Linux with `espeak`

---

## 🚀 Quick Install (macOS)

```bash
git clone https://github.com/<your-username>/cowork-voice-listener.git
cd cowork-voice-listener
bash install.sh
```

The installer will:
1. Copy the daemon to `~/.claude/cowork-listener.py`
2. Install the `requests` Python package
3. Pull the `gemma3:1b` model into Ollama (if not already present)
4. Register a `launchd` agent at `~/Library/LaunchAgents/com.cowork-listener.plist`
5. Start the daemon immediately and on every login

---

## 🎯 Usage

Once installed, it just runs. Open Claude Desktop, use Cowork, and you'll hear summaries of each response.

**Watch live logs:**

```bash
tail -f ~/.claude/cowork-listener.log
```

**Check the daemon is alive:**

```bash
launchctl list | grep cowork-listener
```

**Stop it:**

```bash
launchctl unload ~/Library/LaunchAgents/com.cowork-listener.plist
```

**Start it again:**

```bash
launchctl load ~/Library/LaunchAgents/com.cowork-listener.plist
```

---

## ⚙️ Configuration

Open `~/.claude/cowork-listener.py` and edit the top of the file:

| Variable         | Default        | What it does                              |
| ---------------- | -------------- | ----------------------------------------- |
| `VOICE_NAME`     | `Damayanti`    | macOS voice (try `say -v '?'` for list)   |
| `SPEECH_RATE`    | `200`          | words per minute                          |
| `CHECK_INTERVAL` | `10`           | poll interval in seconds                  |
| `OLLAMA_MODEL`   | `gemma3:1b`    | any model you have pulled in Ollama       |
| `OLLAMA_TIMEOUT` | `20`           | max seconds before falling back to raw    |

Restart the daemon after editing:

```bash
launchctl unload ~/Library/LaunchAgents/com.cowork-listener.plist
launchctl load   ~/Library/LaunchAgents/com.cowork-listener.plist
```

---

## 🧠 Recommended Ollama Models

| Model           | Size    | Speed      | Notes                          |
| --------------- | ------- | ---------- | ------------------------------ |
| `qwen2.5:0.5b`  | ~400 MB | ⚡ fastest | Smallest, surprisingly capable |
| `gemma3:1b`     | ~777 MB | ⚡ fast    | ✅ default — great balance     |
| `llama3.2:1b`   | ~1.3 GB | ⚡ fast    | Strong multilingual            |
| `qwen2.5:1.5b`  | ~1 GB   | 🏃 medium  | Better quality, still quick    |
| `phi3:mini`     | ~2.3 GB | 🚶 slower  | Microsoft's efficient flash    |

Pull any of them:

```bash
ollama pull qwen2.5:0.5b
```

---

## 🛠️ How It Works

```
┌─────────────────────┐      ┌──────────────────────┐      ┌─────────────┐
│  Cowork writes      │      │  Listener polls      │      │  Ollama     │
│  JSONL transcript   │ ───▶ │  every 10 seconds    │ ───▶ │  summarizes │
│  in ~/Library/…     │      │  → finds latest msg  │      │  locally    │
└─────────────────────┘      └──────────────────────┘      └──────┬──────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │  macOS say  │
                                                            │  (TTS)      │
                                                            └─────────────┘
```

1. Claude Cowork writes each message to a JSONL file under `~/Library/Application Support/Claude/local-agent-mode-sessions/…`
2. The daemon polls that file every 10 seconds, finds the latest assistant message, and MD5-hashes it
3. If the hash differs from the last spoken one, the text is sent to Ollama for a short, casual summary
4. Emojis and markdown are stripped, then the OS TTS speaks it
5. The hash is saved so we never speak the same reply twice

---

## 🗑️ Uninstall

```bash
bash uninstall.sh
```

Or manually:

```bash
launchctl unload ~/Library/LaunchAgents/com.cowork-listener.plist
rm ~/Library/LaunchAgents/com.cowork-listener.plist
rm ~/.claude/cowork-listener.py
rm ~/.claude/cowork-listener.log
rm ~/.claude/.cowork_last_spoken
```

---

## 🐛 Troubleshooting

**Daemon runs but no sound?**
- Check system volume
- Test `say` directly: `say -v Damayanti "halo"`
- Verify voice exists: `say -v '?' | grep Damayanti`

**"Ollama not available"?**
- Start Ollama: `brew services start ollama` or open the Ollama app
- Verify the model is pulled: `ollama list`

**Daemon doesn't detect new responses?**
- Check the log for the session file path: `grep 'Session file' ~/.claude/cowork-listener.log`
- Cowork must actually be writing the session — try sending a message in Cowork first

**launchctl load fails with I/O error?**
- Validate the plist: `plutil -lint ~/Library/LaunchAgents/com.cowork-listener.plist`
- Re-run `install.sh` to regenerate a clean plist

---

## 🤝 Contributing

PRs welcome. Good first issues:

- Add more voice options (OpenAI TTS, ElevenLabs local, Piper)
- Support English / multilingual prompts
- Add a menu-bar icon for start/stop/mute
- Windows auto-start (Scheduled Task)

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

Built with ☕ and a lot of `say -v Damayanti "halo"`.
