"""Entry point for InLine-CLI: `inline` or `python -m inline_cli`."""

from __future__ import annotations

import argparse
import sys


def _run_setup() -> None:
    """Launch the TUI app with the onboarding screen for guided setup."""
    from .app import InlineApp

    app = InlineApp(force_onboarding=True)
    app.run()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="inline",
        description="InLine AI — Chat with AI right in your terminal.",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run interactive setup to configure providers and API keys.",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="Start with a specific provider (openai, anthropic, gemini, groq, ollama).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Start with a specific model.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit.",
    )

    args = parser.parse_args()

    if args.version:
        from . import __version__
        print(f"InLine AI v{__version__}")
        sys.exit(0)

    if args.setup:
        _run_setup()
        sys.exit(0)

    # Launch the TUI app
    from .app import InlineApp
    from .config import load_config

    app = InlineApp()

    if args.provider:
        app.current_provider = args.provider
    if args.model:
        app.current_model = args.model

    app.run()


if __name__ == "__main__":
    main()
