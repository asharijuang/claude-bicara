# 🎙️ Claude Bicara

> _"Claude yang bisa ngomong."_

<p align="left">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Platform" src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey">
  <img alt="Python" src="https://img.shields.io/badge/python-3.8%2B-yellow">
  <img alt="Ollama" src="https://img.shields.io/badge/ollama-local-green">
  <img alt="Status" src="https://img.shields.io/badge/status-active-brightgreen">
</p>

Listen to Claude Cowork responses hands-free — a tiny background daemon that watches your Cowork session, asks a **local** Ollama model to summarize each reply into a short, phone-conversation-style sentence, and reads it out loud with your OS's built-in TTS.

**Runs locally by default.** Summarization via local Ollama, TTS via Piper or system voice. Optional cloud TTS via Google Gemini for the highest quality voices.

> _"Jadi kamu bisa lanjut ngoding, scroll dokumen, atau ngopi santai — sambil tetap dengerin apa yang Claude lagi kerjakan."_

---

## 🎬 Demo

```
[You:]       buatkan cerita pendek tentang harry potter

[Claude:]    Keajaiban di Hogsmeade. Harry Potter berjalan melalui jalan bersalju
             menuju Hogsmeade, sekolah sihir terlarang untuk pelajar...
             (400+ words)

[Bicara 🎙️] "Harry ketemu Ron dan Hermione di Tiga Sapu, ngobrolin
              Magic Quidditch sambil minum cokelat panas."
```

> 💡 _Add a screen-recording or animated GIF here to show it in action._

---

## ✨ Features

- 🔎 **Automatic monitoring** — watches the latest Cowork session transcript (`.jsonl`)
- 🧠 **Local summarization** — uses Ollama (`gemma3:1b` by default, ~777 MB, super fast)
- 🗣️ **Natural speech** — strips emojis, markdown, and code blocks before speaking
- ☎️ **Conversational tone** — summaries sound like a friend calling you on the phone
- 💻 **Cross-platform TTS** — macOS (`say`), Windows (SAPI), Linux (`espeak`)
- 🔁 **Auto-start on boot** — via `launchd` on macOS
- 🧼 **Deduped by hash** — never speaks the same response twice
- 🔒 **Privacy-first** — offline by default with Piper/system TTS, optional cloud via Gemini TTS

---

## 📦 Requirements

- [**Claude Desktop**](https://claude.ai/download) with Cowork mode
- [**Ollama**](https://ollama.com) running locally
- **Python 3.8+** with `requests`
- macOS 11+, Windows 10+, or Linux with `espeak`

---

## 🚀 Quick Install (macOS)

```bash
git clone https://github.com/asharijuang/claude-bicara.git
cd claude-bicara
bash install.sh
```

The installer will:
1. Copy the daemon to `~/.claude/cowork-listener.py`
2. Install the `requests` Python package
3. Pull the `gemma3:1b` model into Ollama (if not already present)
4. Register a `launchd` agent at `~/Library/LaunchAgents/com.cowork-listener.plist`
5. Start the daemon immediately and on every login

---

## 🪟 Quick Install (Windows)

**Prerequisites:** Python 3.8+, [Ollama](https://ollama.com), [Claude Desktop](https://claude.ai/download)

```powershell
# 1. Clone the repo
git clone https://github.com/asharijuang/claude-bicara.git
cd claude-bicara

# 2. Install dependencies
pip install requests

# 3. Pull the Ollama model
ollama pull gemma3:1b

# 4. Copy the daemon script
mkdir $env:USERPROFILE\.claude -Force
copy src\cowork-listener.py $env:USERPROFILE\.claude\cowork-listener.py
```

**Set up .env (optional, for cloud TTS):**

```powershell
# Create .env in ~/.claude/
@"
ELEVENLABS_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
"@ | Out-File $env:USERPROFILE\.claude\.env -Encoding utf8
```

**Run manually:**

```powershell
python $env:USERPROFILE\.claude\cowork-listener.py
```

**Auto-start on login (Task Scheduler):**

```powershell
# Create a scheduled task that runs on login
$action = New-ScheduledTaskAction `
    -Execute "pythonw" `
    -Argument "$env:USERPROFILE\.claude\cowork-listener.py"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask `
    -TaskName "CoworkListener" `
    -Action $action `
    -Trigger $trigger `
    -Description "Claude Bicara — voice listener for Cowork"

# Verify it's registered
Get-ScheduledTask -TaskName "CoworkListener"
```

**Stop / Remove:**

```powershell
# Stop
Stop-ScheduledTask -TaskName "CoworkListener"

# Remove entirely
Unregister-ScheduledTask -TaskName "CoworkListener" -Confirm:$false
```

> _Windows uses built-in SAPI for TTS by default. For better quality, set `TTS_BACKEND = "elevenlabs"` or `"gemini"` in the script._

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

**Stop / Start:**

```bash
launchctl unload ~/Library/LaunchAgents/com.cowork-listener.plist
launchctl load   ~/Library/LaunchAgents/com.cowork-listener.plist
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
| `TTS_BACKEND`    | `system`       | `elevenlabs`, `gemini`, `piper`, `system`, `hybrid` |
| `ELEVENLABS_API_KEY` | _(env var)_ | ElevenLabs API key                         |
| `ELEVENLABS_VOICE_ID` | `JBFqnCBsd6RMkjVDRZzb` | Voice ID (see ElevenLabs section) |
| `ELEVENLABS_MODEL` | `eleven_v3`  | TTS model (most expressive)                |
| `ELEVENLABS_STABILITY` | `0.3`    | 0.0–1.0, lower = more expressive           |
| `GEMINI_API_KEY` | _(env var)_    | Google AI Studio API key for Gemini TTS    |
| `GEMINI_TTS_MODEL` | `gemini-2.5-flash-preview-tts` | Gemini TTS model          |
| `GEMINI_VOICE`   | `Kore`         | Prebuilt voice (see Gemini TTS section)    |
| `GEMINI_LANGUAGE_CODE` | `id-ID`  | Language hint for pronunciation            |
| `PIPER_MODEL`    | id_ID-news_tts | Piper voice .onnx path                    |
| `PIPER_LENGTH_SCALE` | `0.8`      | <1.0 = faster/younger voice               |
| `PIPER_NOISE_SCALE`  | `0.8`      | voice variability                         |
| `PIPER_VOLUME_BOOST` | `2.0`      | afplay -v multiplier (macOS)              |

### 🎙️ ElevenLabs TTS (premium quality, most expressive)

Industry-leading cloud TTS with incredibly natural, expressive voices. Free tier: 10,000 chars/month (~10 min audio).

**1. Get API key:** Sign up at [elevenlabs.io](https://elevenlabs.io) → Profile → API Keys

**2. Set your API key:**

```bash
# In .env file (recommended)
ELEVENLABS_API_KEY=your-key-here
```

**3. Configure in `~/.claude/cowork-listener.py`:**

```python
TTS_BACKEND = "elevenlabs"
ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George (narrative)
ELEVENLABS_STABILITY = 0.3     # Lower = more expressive
ELEVENLABS_STYLE = 0.5         # Style exaggeration
```

**Popular voices:** Browse at [elevenlabs.io/voice-library](https://elevenlabs.io/voice-library). Copy the voice ID from any voice page.

**Fallback chain:** ElevenLabs → Gemini → Piper → system TTS. If quota runs out, seamlessly falls back.

> _Premium quality — best option if you want the most natural, expressive speech. Free tier is enough for casual use._

### ☁️ Gemini TTS (cloud-based, high quality, multilingual)

Google's Gemini API offers cloud-based neural TTS with expressive, natural-sounding voices. Supports 24+ languages including Indonesian.

**1. Get a free API key:**
Visit [Google AI Studio](https://aistudio.google.com/apikey) and create an API key.

**2. Install the SDK:**

```bash
pip3 install --user google-genai
```

**3. Set your API key** (pick one):

```bash
# Option A: Environment variable (recommended)
export GEMINI_API_KEY="your-key-here"

# Option B: Edit directly in ~/.claude/cowork-listener.py
GEMINI_API_KEY = "your-key-here"

# Option C: Add to launchd plist for auto-start
# Add <key>GEMINI_API_KEY</key><string>your-key</string> in the Environment dict
```

**4. Edit `~/.claude/cowork-listener.py`:**

```python
TTS_BACKEND = "gemini"
GEMINI_VOICE = "Kore"        # Try: Aoede, Puck, Zephyr, Leda, Fenrir
GEMINI_LANGUAGE_CODE = "id-ID"
```

**Available voices:** Achernar, Achird, Algenib, Algieba, Alnilam, Aoede, Autonoe, Callirrhoe, Charon, Despina, Erinome, Fenrir, Gacrux, Iapetus, Kore, Leda, Orus, Puck, Pulcherrima, Rasalgethi, Sadachbia, Sadaltager, Schedar, Sulafat, Umbriel, Vindemiatrix, Zephyr

> _Cloud-based — requires internet. Falls back to system TTS if offline or API key missing._

### 🧠 Piper neural TTS (Indonesian, natural voice)

Clearer Indonesian than `say -v Damayanti` and more natural than VOICEVOX for Indonesian text.

**Install:**

```bash
pip3 install --user piper-tts
mkdir -p ~/.claude/piper-voices && cd ~/.claude/piper-voices
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/id/id_ID/news_tts/medium/id_ID-news_tts-medium.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/id/id_ID/news_tts/medium/id_ID-news_tts-medium.onnx.json
```

Then set `TTS_BACKEND = "piper"` in the daemon. ~60 MB model, ~300 MB RAM when speaking.

### 🎌 Hybrid TTS (Piper Indonesian + macOS Kyoko for Japanese)

Set `TTS_BACKEND = "hybrid"` and `TONE = "senpai"` to get the best of both worlds:
- **Indonesian sentences** spoken by Piper neural voice (clear pronunciation)
- **Japanese romaji sentences** spoken by macOS Kyoko (authentic Japanese)

The daemon splits each summary by sentence and routes based on language density.
The `senpai` tone prompt is tuned to produce **separate** Indonesian and Japanese
sentences (e.g., _"Hai senpai! Bug-nya auto fixed. Sugoi desu ne. Ganbatte kudasai!"_),
so the hybrid split works cleanly.

No extra install required — Kyoko is built into macOS.
| `TONE`           | `casual`       | summary tone — see table below            |
| `TTS_BACKEND`    | `system`       | `system` (OS TTS) or `voicevox` (JP)      |
| `VOICEVOX_SPEAKER` | `3`          | 3=Zundamon, 8=Tsumugi, 2=Shikoku Metan    |
| `VOICEVOX_SPEED` | `1.1`          | 0.5 – 2.0                                 |

### 🎭 Tone presets

| `TONE`     | Gaya bicara                           | Contoh                                                                           |
| ---------- | ------------------------------------- | -------------------------------------------------------------------------------- |
| `casual`   | Ngobrol santai kayak sama temen ✅    | "Bug-nya udah diperbaiki, coba restart ya."                                      |
| `formal`   | Profesional, formal, briefing rapat   | "Bug telah diperbaiki. Silakan restart."                                         |
| `cute`     | Imut dan menggemaskan~                | "Bug-nya udah beres dong, restart yuk hehe~"                                     |
| `anime`    | Anime sensei energik                  | "Yosh! Bug-nya sukses diperbaiki. Ganbatte!"                                     |
| `news`     | Presenter berita                      | "Bug telah berhasil diperbaiki dan siap diuji."                                  |
| `senpai`   | Kouhai imut ke senpai (romaji JP) ✨  | "Senpai, bug-nya udah aku perbaiki desu ne~, coba restart ya senpai, ganbatte!" |

### 🇯🇵 VOICEVOX (Japanese TTS)

Want a real anime-girl voice? Combine `TONE=senpai` with `TTS_BACKEND=voicevox`.

**1. Install VOICEVOX engine:**

```bash
# Option A: Docker (easiest, CPU version)
docker run -d --rm -p 50021:50021 voicevox/voicevox_engine:cpu-latest

# Option B: Native app
# Download from https://voicevox.hiroshiba.jp/
```

**2. Edit `~/.claude/cowork-listener.py`:**

```python
TTS_BACKEND = "voicevox"
VOICEVOX_SPEAKER = 3       # Zundamon — cutest
TONE = "senpai"            # summary sprinkled with desu ne~
```

**3. Restart the daemon** — now every Claude response becomes an anime kouhai cheering you on. 💮

> _Heads-up: VOICEVOX renders Japanese characters & romaji naturally, but pure Indonesian words get pronounced phonetically. That's the whole charm of the `senpai` tone — it deliberately mixes romaji Japanese phrases into the summary._

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
                                                    ┌──────────────┼──────────────┐
                                                    ▼              ▼              ▼
                                              ┌──────────┐  ┌──────────┐  ┌──────────┐
                                              │ Gemini   │  │  Piper   │  │ macOS    │
                                              │ TTS ☁️   │  │ (local)  │  │ say      │
                                              └──────────┘  └──────────┘  └──────────┘
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

**`launchctl load` fails with I/O error?**
- Validate the plist: `plutil -lint ~/Library/LaunchAgents/com.cowork-listener.plist`
- Re-run `install.sh` to regenerate a clean plist

---

## 🗺️ Roadmap / Wishlist

Things we want to add next — PRs welcome!

### 🎤 Voice & TTS engines
- [ ] **Japanese voice** support (kawaii mode!)
- [ ] [**VOICEVOX**](https://voicevox.hiroshiba.jp/) integration (high-quality JP TTS, free)
- [ ] [**Piper**](https://github.com/rhasspy/piper) integration (fast local neural TTS, multilingual)
- [ ] [**Coqui TTS**](https://github.com/coqui-ai/TTS) option
- [ ] ElevenLabs-style local alternative

### 🎭 Tone presets
- [ ] `professional-formal` — bahasa baku, to-the-point, cocok untuk meeting
- [ ] `casual-santai` — default, kayak ngobrol sama temen (sudah ada ✅)
- [ ] `cute-imut` — "UwU hai~ Claude barusan bikin sesuatu yang seru loh~"
- [ ] `anime-sensei` — energetic, campur sedikit bahasa Jepang ("Yosh!", "Ganbatte!")
- [ ] `news-anchor` — seperti presenter berita, pengucapan jelas

### 🧠 Summarization
- [ ] Multilingual prompts (English, Japanese, Indonesian, etc.)
- [ ] Configurable summary length (1 kalimat / 2-3 kalimat / paragraph)
- [ ] Skip tool-calls output option (only speak natural language responses)

### 🖥️ UX
- [ ] Menu-bar icon with mute toggle, model switcher, tone switcher
- [ ] Native notification when daemon starts/stops
- [ ] Desktop widget showing current status
- [ ] Web dashboard (localhost:xxxx) for live monitoring

### 📦 Packaging
- [ ] Homebrew formula (`brew install claude-bicara`)
- [ ] `.pkg` installer for non-technical users
- [ ] Windows auto-start (Scheduled Task installer)
- [ ] Docker image for Linux users
- [ ] Linux systemd unit file

---

## 🤝 Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<p align="center">
  Built with ☕ in Indonesia. Powered by <a href="https://ollama.com">Ollama</a> &amp; <a href="https://claude.ai">Claude</a>.
</p>
