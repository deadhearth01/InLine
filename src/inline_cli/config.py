"""Configuration management for InLine-CLI.

Stores API keys and preferences in ~/.config/inline-cli/config.toml
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w

CONFIG_DIR = Path.home() / ".config" / "inline-cli"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG: dict[str, Any] = {
    "general": {
        "default_provider": "ollama",
        "theme": "dark",
    },
    "openai": {
        "api_key": "",
        "model": "gpt-4o",
        "base_url": "https://api.openai.com/v1",
    },
    "anthropic": {
        "api_key": "",
        "model": "claude-sonnet-4-20250514",
    },
    "gemini": {
        "api_key": "",
        "model": "gemini-2.0-flash",
    },
    "groq": {
        "api_key": "",
        "model": "llama-3.3-70b-versatile",
    },
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "llama3.2",
    },
}

PROVIDER_DISPLAY_NAMES = {
    "openai": "ChatGPT (OpenAI)",
    "anthropic": "Claude (Anthropic)",
    "gemini": "Gemini (Google)",
    "groq": "Groq",
    "ollama": "Ollama (Local)",
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, preferring override values."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> dict[str, Any]:
    """Load config from disk, merging with defaults."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            user_config = tomllib.load(f)
        return _deep_merge(DEFAULT_CONFIG, user_config)
    return DEFAULT_CONFIG.copy()


def save_config(config: dict[str, Any]) -> None:
    """Save config to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(config, f)


def get_api_key(provider: str, config: dict[str, Any] | None = None) -> str:
    """Get API key for a provider, checking env vars first."""
    env_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
    }
    env_var = env_map.get(provider, "")
    if env_var and os.environ.get(env_var):
        return os.environ[env_var]

    if config is None:
        config = load_config()
    return config.get(provider, {}).get("api_key", "")
