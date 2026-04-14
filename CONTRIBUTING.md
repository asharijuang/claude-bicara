# Contributing to Claude Bicara

Thanks for your interest! 🎉 This project is small and focused — we want it to stay simple, fast, and fun.

## Ways to contribute

- **Report bugs** via GitHub Issues — include OS, Python version, Ollama version, and a snippet from `~/.claude/cowork-listener.log`
- **Suggest features** — check the Roadmap in [README.md](README.md#🗺️-roadmap--wishlist) first
- **Submit PRs** — see the workflow below

## Dev setup

```bash
git clone https://github.com/asharijuang/claude-bicara.git
cd claude-bicara
python3 -m pip install -r requirements.txt
python3 src/cowork-listener.py    # run in foreground to see logs
```

## PR checklist

- [ ] The daemon still starts without errors (`python3 src/cowork-listener.py`)
- [ ] If you added a new dependency, update `requirements.txt`
- [ ] If you changed config defaults, update the README config table
- [ ] Keep changes small and focused — one feature per PR
- [ ] No cloud calls, no telemetry, no API keys — this stays 100% local

## Adding a new TTS backend

1. Create a `speak_<backend>(text)` function in `src/cowork-listener.py`
2. Route to it in `speak(text)` based on a `TTS_BACKEND` config variable
3. Document the backend (installation, config) in the README
4. Add its binary/service dependency to the install script if applicable

## Adding a new tone preset

1. Add a new prompt template in `summarize_with_ollama` (or refactor into a `TONES` dict)
2. Add a `TONE` config variable at the top of the daemon
3. Test with 2-3 sample responses to make sure it sounds right
4. Add the new tone to the README table

## Code style

- Plain Python, no framework bloat
- Keep the daemon under ~400 lines if possible
- Clear variable names over clever tricks
- Comments in English; user-facing strings can be in Indonesian

## License

By contributing, you agree that your code will be licensed under the MIT License.
