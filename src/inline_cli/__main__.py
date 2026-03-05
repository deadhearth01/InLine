"""Entry point for InLine-CLI: `inline` or `python -m inline_cli`."""

from __future__ import annotations

import argparse
import logging
import os
import sys
import traceback

# ── Minimum Python version gate ───────────────────────────────────────
_MIN_PYTHON = (3, 10)


def _check_python_version() -> None:
    """Exit early with a helpful message when Python is too old."""
    if sys.version_info < _MIN_PYTHON:
        major, minor = _MIN_PYTHON
        print(
            f"\n❌  InLine AI requires Python {major}.{minor}+, "
            f"but you are running Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}.\n"
        )
        print("How to fix:\n")
        if sys.platform == "darwin":
            print("  # Install latest Python with Homebrew:")
            print("  brew install python@3.13\n")
            print("  # Then reinstall InLine AI:")
            print("  python3.13 -m pip install git+https://github.com/deadhearth01/InLine.git\n")
            print("  # Or create a venv with the right Python:")
            print("  python3.13 -m venv .venv && source .venv/bin/activate")
            print("  pip install git+https://github.com/deadhearth01/InLine.git\n")
        else:
            print("  # Install Python 3.10+ from https://www.python.org/downloads/")
            print("  # Or use your package manager (apt, dnf, etc.):\n")
            print("  sudo apt install python3.13 python3.13-venv   # Debian/Ubuntu")
            print("  sudo dnf install python3.13                    # Fedora\n")
            print("  # Then reinstall InLine AI:")
            print("  python3.13 -m pip install git+https://github.com/deadhearth01/InLine.git\n")
        print(f"  ℹ️  Your current Python: {sys.executable}")
        print(f"  ℹ️  Version: {sys.version.split(chr(10))[0]}")
        sys.exit(1)


# ── Debug / logging helpers ───────────────────────────────────────────

def _setup_debug_logging() -> None:
    """Enable verbose logging for troubleshooting."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )
    # Lower noise from third-party HTTP libraries
    for noisy in ("httpx", "httpcore", "urllib3", "openai._base_client"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    logging.getLogger("inline_cli").setLevel(logging.DEBUG)


def _print_diagnostics() -> None:
    """Print system and dependency info for bug reports."""
    from . import __version__

    print("\n── InLine AI diagnostics ──────────────────────────")
    print(f"  InLine AI version : {__version__}")
    print(f"  Python            : {sys.version.split(chr(10))[0]}")
    print(f"  Executable        : {sys.executable}")
    print(f"  Platform          : {sys.platform}")
    print(f"  Terminal          : {os.environ.get('TERM', 'unknown')}")
    print(f"  TERM_PROGRAM      : {os.environ.get('TERM_PROGRAM', 'unknown')}")

    deps = [
        "textual", "httpx", "openai", "anthropic",
        "google-genai", "groq", "pyperclip", "tomli-w",
    ]
    print("  ─── Installed packages ───")
    import importlib.metadata
    for dep in deps:
        try:
            ver = importlib.metadata.version(dep)
            print(f"    {dep:20s} {ver}")
        except importlib.metadata.PackageNotFoundError:
            print(f"    {dep:20s} ⚠ NOT INSTALLED")

    # Check config file
    from .config import CONFIG_FILE
    print(f"\n  Config file       : {CONFIG_FILE}")
    print(f"  Config exists     : {CONFIG_FILE.exists()}")
    print("──────────────────────────────────────────────────\n")


# ── Entry-point helpers ───────────────────────────────────────────────

def _run_setup() -> None:
    """Launch the TUI app with the onboarding screen for guided setup."""
    from .app import InlineApp

    app = InlineApp(force_onboarding=True)
    app.run()


def main() -> None:
    _check_python_version()

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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging to help troubleshoot issues.",
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Print system info and dependency versions, then exit.",
    )

    args = parser.parse_args()

    if args.version:
        from . import __version__
        print(f"InLine AI v{__version__}")
        sys.exit(0)

    if args.diagnostics:
        _print_diagnostics()
        sys.exit(0)

    if args.debug:
        _setup_debug_logging()

    logger = logging.getLogger("inline_cli")

    if args.setup:
        _run_setup()
        sys.exit(0)

    # Launch the TUI app
    try:
        from .app import InlineApp

        app = InlineApp()

        if args.provider:
            app.current_provider = args.provider
        if args.model:
            app.current_model = args.model

        app.run()
    except ImportError as exc:
        print(f"\n❌  Missing dependency: {exc}\n")
        print("Try reinstalling with:")
        print("  pip install --force-reinstall git+https://github.com/deadhearth01/InLine.git\n")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)
    except Exception as exc:
        logger.debug("Fatal error", exc_info=True)
        print(f"\n❌  InLine AI crashed: {exc}\n")
        print("Troubleshooting:")
        print("  1. Run with --debug for verbose output:  inline --debug")
        print("  2. Run --diagnostics to check your setup: inline --diagnostics")
        print("  3. Report a bug: https://github.com/deadhearth01/InLine/issues\n")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
