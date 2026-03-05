<div align="center">

# ⚡ InLine AI

**A ChatGPT-style AI chat interface that lives entirely in your terminal.**

Mouse-driven · Multi-provider · Streaming · Markdown rendering · Zero browser friction

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Built with Textual](https://img.shields.io/badge/built%20with-Textual-purple?style=flat-square)](https://textual.textualize.io/)

</div>

---

Stop switching to the browser. InLine AI brings a full, polished chat interface into your terminal — with real mouse support, live streaming responses, rich Markdown rendering, and one-click provider switching between ChatGPT, Claude, Gemini, Groq, and local Ollama models.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Option A — pip (recommended)](#option-a--pip-recommended)
  - [Option B — from source](#option-b--from-source)
- [Quick Start](#quick-start)
- [Providers](#providers)
  - [Ollama — local models (free, no key)](#ollama--local-models-free-no-key)
  - [OpenAI (ChatGPT)](#openai-chatgpt)
  - [Anthropic (Claude)](#anthropic-claude)
  - [Google (Gemini)](#google-gemini)
  - [Groq](#groq)
- [Configuration](#configuration)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [CLI Reference](#cli-reference)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| | |
|---|---|
| 🖱️ **Mouse-driven UI** | Click buttons, switch providers, scroll history — entirely mouse-friendly |
| ⚡ **5 AI providers** | OpenAI, Anthropic, Gemini, Groq, Ollama — switch with one click |
| 🏠 **Local-first** | Auto-detects Ollama and lists all pulled models on startup |
| 📡 **Real-time streaming** | Token-by-token streaming for every provider |
| 🎨 **Rich Markdown** | Code fences, headings, blockquotes, tables rendered inline |
| 🔑 **Flexible auth** | Env vars or the built-in ⚙ Settings panel — never stored in plain sight |
| ✏️ **Multi-line input** | Grow-as-you-type textarea — `Enter` to send, `Shift+Enter` for newlines |
| 🧪 **API key testing** | One-click "Test" button verifies each key before saving |
| 📋 **Copy / regen / delete** | Per-message action buttons on every chat bubble |
| ✨ **Onboarding wizard** | Guided first-run flow scans your system and walks through setup |

---

## Requirements

- **Python 3.10+** — check with `python3 --version`
- A terminal with **mouse support**: iTerm2, Kitty, WezTerm, Ghostty, Windows Terminal, or any modern emulator

> **Tip:** The default macOS Terminal.app has limited mouse support. [iTerm2](https://iterm2.com/) or [Kitty](https://sw.kovidgoyal.net/kitty/) give the best experience.

> **⚠️ macOS users:** The system Python (`/usr/bin/python3`) is often 3.9 and **will not work**.
> Install Python 3.10+ via [Homebrew](https://brew.sh/): `brew install python@3.13`
> Then use `python3.13 -m pip install ...` or create a venv with `python3.13 -m venv .venv`.

---

## Installation

### Option A — pip (recommended)

Install directly from GitHub — no manual cloning needed:

```bash
# Make sure you're using Python 3.10+
python3 --version   # must be 3.10 or higher

pip install git+https://github.com/deadhearth01/InLine.git
```

Then launch:

```bash
inline
```

> Add `--user` if you don't have system-wide write access, or use a virtual environment (see below).

---

### Option B — from source

Ideal for development or if you want to customise the code.

**1. Clone the repository**

```bash
git clone https://github.com/deadhearth01/InLine.git
cd InLine
```

**2. Create and activate a virtual environment**

```bash
# Use Python 3.10+ explicitly (important on macOS)
python3.13 -m venv .venv          # or python3.12, python3.11, python3.10
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows PowerShell
```

> **💡 Tip:** If `python3 --version` shows 3.9, your system Python is too old.
> Install a newer version first: `brew install python@3.13` (macOS)

**3. Install in editable mode**

```bash
pip install -e .
```

**4. Verify the install**

```bash
inline --version
# InLine AI v0.1.0
```

---

## Quick Start

```bash
# Launch the full TUI
inline

# Guided first-time setup (scans providers, configure keys)
inline --setup

# Start straight into a specific provider
inline --provider gemini

# Start with a specific provider and model
inline --provider ollama --model llama3.2
```

On first launch InLine AI automatically:
1. Scans for a running Ollama instance and lists all pulled models
2. Shows the onboarding wizard if no providers are configured yet
3. Remembers your last-used provider and model

---

## Providers

### Ollama — local models (free, no key)

Run powerful AI models entirely on your own machine — no API key, no cost, no data leaving your computer.

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Start the server (keep this running)
ollama serve

# Pull any model you want
ollama pull llama3.2          # fast, general-purpose (~2 GB)
ollama pull mistral           # great for coding
ollama pull phi4              # Microsoft's compact model
ollama pull deepseek-r1:8b   # reasoning-focused model
```

InLine AI **auto-detects Ollama** and lists all your pulled models in the sidebar's model selector.

---

### OpenAI (ChatGPT)

Get your API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

```bash
# Add to current session
export OPENAI_API_KEY="sk-proj-..."

# Persist across sessions (add to ~/.zshrc or ~/.bashrc)
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.zshrc && source ~/.zshrc
```

Or paste the key in **⚙ Settings → ChatGPT (OpenAI)** while the app is running. Use the **🧪 Test** button to verify it works before saving.

Default model: `gpt-4o`

---

### Anthropic (Claude)

Get your API key at [console.anthropic.com](https://console.anthropic.com/).

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Default model: `claude-sonnet-4-20250514`

---

### Google (Gemini)

Get your API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (free tier available).

```bash
export GEMINI_API_KEY="AIza..."
```

Default model: `gemini-2.0-flash`

---

### Groq

Get your API key at [console.groq.com/keys](https://console.groq.com/keys). Groq has a **free tier** with extremely fast inference.

```bash
export GROQ_API_KEY="gsk_..."
```

Default model: `llama-3.3-70b-versatile`

---

## Configuration

InLine AI stores its configuration at:

```
~/.config/inline-cli/config.toml
```

You can edit it manually or use the **⚙ Settings** panel inside the app. Environment variables always take precedence over values in the config file.

```toml
[general]
default_provider = "ollama"

[openai]
api_key = ""           # or set OPENAI_API_KEY env var
model   = "gpt-4o"

[anthropic]
api_key = ""           # or set ANTHROPIC_API_KEY env var
model   = "claude-sonnet-4-20250514"

[gemini]
api_key = ""           # or set GEMINI_API_KEY env var
model   = "gemini-2.0-flash"

[groq]
api_key = ""           # or set GROQ_API_KEY env var
model   = "llama-3.3-70b-versatile"

[ollama]
base_url = "http://localhost:11434"
model    = "llama3.2"
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift+Enter` | Insert newline in input |
| `Ctrl+N` | New chat |
| `Ctrl+P` | Toggle sidebar |
| `Ctrl+Q` | Quit |
| `Tab` / `Shift+Tab` | Navigate between UI elements |

---

## CLI Reference

```
Usage: inline [OPTIONS]

Options:
  --setup             Run the guided setup wizard
  --provider NAME     Start with a specific provider
                      Options: ollama, openai, anthropic, gemini, groq
  --model NAME        Start with a specific model
  --debug             Enable verbose debug logging for troubleshooting
  --diagnostics       Print system info and dependency versions, then exit
  --version           Print version and exit
  -h, --help          Show this help message and exit
```

---

## Troubleshooting

### ❌ "requires a different Python" error

```
ERROR: Package 'inline-cli' requires a different Python: 3.9.6 not in '>=3.10'
```

You're using the macOS system Python (3.9). InLine AI requires **Python 3.10+**.

**Fix (macOS):**
```bash
brew install python@3.13
python3.13 -m pip install git+https://github.com/deadhearth01/InLine.git
```

**Fix (Linux):**
```bash
sudo apt install python3.13 python3.13-venv   # Debian/Ubuntu
python3.13 -m pip install git+https://github.com/deadhearth01/InLine.git
```

**Fix (using a virtual environment):**
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/deadhearth01/InLine.git
```

### ❌ InLine crashes on launch

1. Run with debug logging:
   ```bash
   inline --debug
   ```
2. Print diagnostics (Python version, installed packages, config path):
   ```bash
   inline --diagnostics
   ```
3. Still stuck? [Open an issue](https://github.com/deadhearth01/InLine/issues) and paste the `--diagnostics` output.

### ❌ Missing dependency errors

If you see `ModuleNotFoundError` or `ImportError`:

```bash
pip install --force-reinstall git+https://github.com/deadhearth01/InLine.git
```

### ❌ Space key doesn't work / chat goes blank

Make sure you're on the latest version:

```bash
pip install --upgrade git+https://github.com/deadhearth01/InLine.git
```

### ❌ Ollama not detected

Make sure Ollama is running:
```bash
ollama serve          # start the server
ollama list           # verify models are pulled
inline                # InLine AI will auto-detect it
```

### ❌ API key not recognized

1. Check the key is set correctly:
   ```bash
   echo $OPENAI_API_KEY      # should print your key
   ```
2. Or paste it in **⚙ Settings** inside the app and click **🧪 Test** to verify.
3. Keys are saved at `~/.config/inline-cli/config.toml` — you can edit this file directly.

---

## Project Structure

```
InLine/
├── src/
│   └── inline_cli/
│       ├── __init__.py          # package version
│       ├── __main__.py          # CLI entry point (argparse)
│       ├── app.py               # Textual TUI application
│       ├── config.py            # TOML config load/save, env-var resolution
│       └── providers/
│           ├── base.py          # BaseProvider abstract class
│           ├── registry.py      # ProviderRegistry — scan, detect default
│           ├── openai_provider.py
│           ├── anthropic_provider.py
│           ├── gemini_provider.py
│           ├── groq_provider.py
│           └── ollama_provider.py
├── pyproject.toml               # package metadata & dependencies
├── LICENSE
└── README.md
```

---

## Contributing

Pull requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes, verify the app launches: `inline`
4. Open a PR against `main`

**Development setup:**

```bash
git clone https://github.com/deadhearth01/InLine.git
cd InLine
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
inline   # launch straight from source
```

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.

