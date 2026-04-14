#!/usr/bin/env python3
"""
Cowork Voice Listener
Monitors Claude Cowork session transcripts and speaks summarized responses
using local TTS (macOS `say`, Windows SAPI, or Linux espeak).

Summarization is powered by a local Ollama model so nothing leaves your machine.
"""

import os
import json
import time
import hashlib
import subprocess
import requests
import sys
import re
from pathlib import Path
from datetime import datetime

# =============================================================================
# Configuration — tweak these to taste
# =============================================================================
COWORK_BASE_PATH = os.path.expanduser(
    "~/Library/Application Support/Claude/local-agent-mode-sessions"
)
CLAUDE_DIR = os.path.expanduser("~/.claude")
TRACKING_FILE = os.path.join(CLAUDE_DIR, ".cowork_last_spoken")
LOG_FILE = os.path.join(CLAUDE_DIR, "cowork-listener.log")

CHECK_INTERVAL = 10      # seconds between polls
SPEECH_RATE = 200        # words per minute
VOICE_NAME = "Damayanti" # macOS Indonesian voice; change to your favorite

# Ollama configuration (local LLM for summarization)
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"  # fast, lightweight, good with Indonesian
OLLAMA_TIMEOUT = 20         # seconds

Path(CLAUDE_DIR).mkdir(parents=True, exist_ok=True)


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def find_latest_session_file():
    """Recursively find the newest conversation JSONL under the Cowork folder."""
    try:
        if not os.path.exists(COWORK_BASE_PATH):
            return None

        jsonl_files = []
        for root, _, files in os.walk(COWORK_BASE_PATH):
            for f in files:
                if f.endswith(".jsonl") and f != "audit.jsonl":
                    full_path = os.path.join(root, f)
                    jsonl_files.append((full_path, os.path.getmtime(full_path)))

        if not jsonl_files:
            return None
        jsonl_files.sort(key=lambda x: x[1], reverse=True)
        return jsonl_files[0][0]
    except Exception as e:
        log(f"Error finding session file: {e}")
        return None


def extract_text_from_content(content):
    """Walk Cowork's nested content structure and pull out plain text."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                t = item.get("type")
                if t == "text" and "text" in item:
                    parts.append(item["text"])
                elif t == "tool_result" and "content" in item:
                    parts.append(extract_text_from_content(item["content"]))
            elif isinstance(item, str):
                parts.append(item)
        return " ".join(filter(None, parts))

    if isinstance(content, dict):
        if "text" in content:
            return content["text"]
        if "content" in content:
            return extract_text_from_content(content["content"])

    return str(content) if content else ""


def get_last_response():
    """Return the most recent assistant reply, or None."""
    session_file = find_latest_session_file()
    if not session_file:
        return None
    try:
        with open(session_file, "r") as f:
            lines = f.readlines()
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get("type") == "assistant":
                    content = entry.get("message", {}).get("content")
                    if content:
                        text = extract_text_from_content(content)
                        if text and text.strip():
                            return text
            except json.JSONDecodeError:
                continue
        return None
    except Exception as e:
        log(f"Error reading response: {e}")
        return None


def response_hash(text):
    return hashlib.md5(text.encode()).hexdigest()


def get_last_spoken_hash():
    try:
        if os.path.exists(TRACKING_FILE):
            with open(TRACKING_FILE, "r") as f:
                return f.read().strip()
    except Exception:
        pass
    return ""


def save_spoken_hash(hash_value):
    try:
        with open(TRACKING_FILE, "w") as f:
            f.write(hash_value)
    except Exception as e:
        log(f"Error saving hash: {e}")


def check_ollama_available():
    try:
        tags_url = OLLAMA_API_URL.replace("/api/generate", "/api/tags")
        response = requests.get(tags_url, timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            names = [m.get("name", "") for m in models]
            if any(OLLAMA_MODEL in n for n in names):
                return True
            log(f"Warning: Model {OLLAMA_MODEL} not found. Available: {names}")
        return False
    except Exception as e:
        log(f"Ollama not available: {e}")
        return False


def strip_emojis_and_code(text):
    """Remove emojis, code blocks, and markdown so TTS sounds natural."""
    text = re.sub(r'```[\s\S]*?```', ' ', text)
    text = re.sub(r'`[^`]+`', ' ', text)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U00002600-\U000026FF"  # misc symbols
        "\U0001FA70-\U0001FAFF"  # symbols & pictographs ext
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(' ', text)
    text = re.sub(r'[*#_~]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def summarize_with_ollama(text):
    """Ask local Ollama model for a short, phone-conversation-style summary."""
    try:
        text = strip_emojis_and_code(text)
        if len(text) > 3000:
            text = text[:3000] + "..."

        prompt = (
            "Ringkas teks ini seperti sedang ngobrol santai di telepon ke teman.\n"
            "Aturan:\n"
            "- Maksimal 1-2 kalimat pendek\n"
            "- Bahasa Indonesia casual, natural\n"
            "- Skip detail teknis, command, code, link\n"
            "- Fokus ke pesan inti saja\n"
            "- Tanpa emoji, tanpa markdown\n\n"
            f"Teks:\n{text}\n\n"
            "Ringkasan (1-2 kalimat casual):"
        )

        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,
            },
            timeout=OLLAMA_TIMEOUT,
        )
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            if result:
                return result
        log(f"Ollama API error: {response.status_code}")
        return text
    except requests.exceptions.Timeout:
        log("Ollama timeout - using original text")
        return text
    except Exception as e:
        log(f"Ollama error: {e} - using original text")
        return text


def speak_mac(text):
    try:
        text = strip_emojis_and_code(text)
        if not text.strip():
            return False
        subprocess.run(
            ["say", "-v", VOICE_NAME, "-r", str(SPEECH_RATE), text],
            check=True, timeout=300,
        )
        return True
    except Exception as e:
        log(f"Error speaking: {e}")
        return False


def speak_windows(text):
    try:
        text = strip_emojis_and_code(text)
        if not text.strip():
            return False
        ps_cmd = (
            "Add-Type -AssemblyName System.Speech;"
            "(New-Object System.Speech.Synthesis.SpeechSynthesizer)"
            f".Speak('{text.replace(chr(39), chr(39)*2)}')"
        )
        subprocess.run(["powershell", "-Command", ps_cmd], check=True, timeout=300)
        return True
    except Exception as e:
        log(f"Error speaking: {e}")
        return False


def speak_linux(text):
    try:
        text = strip_emojis_and_code(text)
        if not text.strip():
            return False
        subprocess.run(
            ["espeak", "-l", "id", "-s", str(SPEECH_RATE), text],
            check=True, timeout=300,
        )
        return True
    except Exception as e:
        log(f"Error speaking: {e}")
        return False


def speak(text):
    if sys.platform == "darwin":
        return speak_mac(text)
    if sys.platform == "win32":
        return speak_windows(text)
    return speak_linux(text)


def main():
    log("Cowork Voice Listener started")
    ollama_ok = check_ollama_available()
    if ollama_ok:
        log(f"Ollama available with model: {OLLAMA_MODEL}")
    else:
        log("Ollama not available - will speak raw text")

    iteration = 0
    try:
        while True:
            iteration += 1
            if iteration % 30 == 0:
                sf = find_latest_session_file()
                if sf:
                    log(f"Session file refreshed: {sf}")

            response_text = get_last_response()
            if response_text:
                h = response_hash(response_text)
                if h != get_last_spoken_hash():
                    log(f"New response detected ({len(response_text)} chars)")
                    summary = summarize_with_ollama(response_text) if ollama_ok else response_text
                    log(f"Summary: {summary}")
                    log(f"Speaking: {summary[:100]}...")
                    if speak(summary):
                        save_spoken_hash(h)
                        log("Spoken successfully")
                    else:
                        log("Failed to speak")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        log("Cowork Voice Listener stopped")
    except Exception as e:
        log(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
