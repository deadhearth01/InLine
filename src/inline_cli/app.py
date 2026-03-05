"""Main Textual TUI application for InLine-CLI.

A ChatGPT/Claude-like chat interface in the terminal with full mouse support,
right-click context menus, guided onboarding, and multi-provider switching.
"""

from __future__ import annotations

import pyperclip
from typing import Any

from textual import events, on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import (
    Center,
    Horizontal,
    Vertical,
    VerticalScroll,
)
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.message import Message as TUIMessage
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Markdown,
    Select,
    Static,
    TextArea,
)

from .config import (
    PROVIDER_DISPLAY_NAMES,
    get_api_key,
    load_config,
    save_config,
)
from .providers.base import Message
from .providers.registry import ProviderRegistry

# ── Emoji icons for providers ──────────────────────────────────────────
PROVIDER_ICONS = {
    "ollama": "🏠",
    "openai": "🟢",
    "anthropic": "🟠",
    "gemini": "🔵",
    "groq": "⚡",
}

# ══════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════

APP_CSS = """
Screen {
    background: $background;
}

/* ── Sidebar ────────────────────────────────── */
#sidebar {
    width: 32;
    background: $surface;
    border-right: tall $primary-background;
    padding: 1 1;
}

#sidebar.hidden {
    display: none;
}

#sidebar-title {
    text-style: bold;
    color: $primary;
    text-align: center;
    padding: 1 0;
}

.sidebar-section-title {
    color: $text-muted;
    text-style: italic;
    padding: 1 0 0 0;
}

.provider-btn {
    width: 100%;
    margin: 0;
}

.provider-btn.active {
    background: $primary 25%;
    border: tall $primary;
    text-style: bold;
}

.provider-btn.unavailable {
    color: $text-muted;
    opacity: 70%;
}

#model-select {
    margin: 1 0;
}

.sidebar-divider {
    color: $text-muted;
    padding: 0;
}

#new-chat-btn {
    width: 100%;
    margin: 1 0 0 0;
}

#settings-btn {
    width: 100%;
    margin: 0;
}

#status-bar {
    color: $text-muted;
    padding: 1 0 0 0;
    text-align: center;
}

/* ── Main area ──────────────────────────────── */
#main-area {
    width: 1fr;
}

/* ── Chat messages scroll ───────────────────── */
#chat-scroll {
    height: 1fr;
    padding: 1 2;
}

/* ── Welcome Screen ─────────────────────────── */
#welcome-container {
    align: center middle;
    height: 1fr;
    padding: 2 4;
}

#welcome-logo {
    text-align: center;
    color: $primary;
    text-style: bold;
    padding: 1;
}

#welcome-subtitle {
    text-align: center;
    color: $text-muted;
    padding: 0 0 2 0;
}

#welcome-hints {
    text-align: center;
    color: $text;
    padding: 1 2;
    background: $panel;
    border: round $surface-lighten-2;
    max-width: 72;
    margin: 1 0;
}

/* ── Chat bubbles ───────────────────────────── */
.user-bubble {
    margin: 1 2 0 8;
    padding: 1 2;
    background: $primary 12%;
    border: round $primary 40%;
}

.assistant-bubble {
    margin: 1 8 0 2;
    padding: 1 2;
    background: $panel;
    border: round $surface-lighten-2;
}

.bubble-header {
    color: $text-muted;
    text-style: bold;
    padding: 0 0 1 0;
}

.bubble-content {
    padding: 0;
}

.bubble-actions {
    dock: bottom;
    height: 1;
    padding: 0;
}

.bubble-action-btn {
    min-width: 3;
    border: none;
    background: transparent;
    color: $text-muted;
    padding: 0 1;
}

.bubble-action-btn:hover {
    color: $primary;
    background: $primary 10%;
}

/* ── Streaming indicator ────────────────────── */
#streaming-bar {
    dock: bottom;
    height: 1;
    background: $primary 15%;
    color: $primary;
    text-align: center;
    display: none;
}

#streaming-bar.visible {
    display: block;
}

/* ── Input area ─────────────────────────────── */
#input-area {
    dock: bottom;
    height: auto;
    max-height: 12;
    padding: 0 2;
    background: $surface;
    border-top: tall $primary-background;
}

#input-context {
    height: 1;
    color: $text-muted;
    padding: 0 0;
}

#input-row {
    height: auto;
    padding: 1 0;
}

#chat-input {
    width: 1fr;
    height: 3;
    background: $panel;
    border: tall $surface-lighten-2;
    padding: 0 1;
}

#chat-input:focus {
    border: tall $primary;
}

#input-hint {
    height: 1;
    color: $text-muted;
    padding: 0 0 0 1;
}

#send-btn {
    min-width: 10;
    margin-left: 1;
}

#stop-btn {
    min-width: 10;
    margin-left: 1;
    display: none;
}

#stop-btn.visible {
    display: block;
}

/* when streaming, hide send and show stop */
#send-btn.streaming {
    display: none;
}

/* ── Onboarding modal ───────────────────────── */
#onboarding-dialog {
    width: 65;
    max-width: 80%;
    height: auto;
    max-height: 85%;
    background: $surface;
    border: round $primary;
    padding: 2 3;
}

OnboardingScreen {
    align: center middle;
}

#onboarding-title {
    text-style: bold;
    text-align: center;
    color: $primary;
    padding: 0 0 1 0;
}

.onboarding-step {
    padding: 1 0;
}

.step-number {
    color: $primary;
    text-style: bold;
}

.step-text {
    padding: 0 0 0 1;
}

.onboarding-provider-row {
    height: 3;
    padding: 0 1;
}

.onboarding-provider-name {
    width: 30;
}

.onboarding-provider-status {
    width: 1fr;
}

#onboarding-skip-btn {
    margin-top: 2;
    width: 100%;
}

#onboarding-done-btn {
    margin-top: 1;
    width: 100%;
}

/* ── Settings modal ─────────────────────────── */
#settings-dialog {
    width: 65;
    max-width: 80%;
    height: auto;
    max-height: 85%;
    background: $surface;
    border: round $primary;
    padding: 2 3;
}

SettingsScreen {
    align: center middle;
}

#settings-title {
    text-style: bold;
    text-align: center;
    color: $primary;
    padding: 0 0 1 0;
}

.settings-section-title {
    color: $text-muted;
    text-style: bold;
    padding: 0 0 1 0;
}

.setting-row {
    height: auto;
    padding: 0 0 1 0;
}

.setting-label {
    width: 24;
    padding: 1 1 0 0;
}

.setting-input {
    width: 1fr;
}

.key-row {
    height: auto;
}

.key-row Input {
    width: 1fr;
}

.test-btn {
    min-width: 8;
    margin-left: 1;
}

.test-result {
    color: $text-muted;
    padding: 0 0 0 1;
    height: auto;
}

.setting-help {
    color: $text-muted;
    padding: 0 0 0 1;
}

#settings-buttons {
    margin-top: 1;
    align: center middle;
}

#save-btn {
    margin-right: 2;
}

/* ── Markdown components (shadcn-like) ────────────────── */
MarkdownFence {
    background: $surface;
    border: round $primary-background;
    margin: 1 0;
    padding: 0 1;
}

MarkdownH1 {
    color: $primary;
    text-style: bold;
    padding: 1 0 0 0;
    border-bottom: solid $primary 35%;
}

MarkdownH2 {
    color: $text;
    text-style: bold;
    padding: 1 0 0 0;
    border-bottom: solid $surface-lighten-3 50%;
}

MarkdownH3 {
    color: $text;
    text-style: bold;
    padding: 1 0 0 0;
}

MarkdownH4 {
    text-style: bold italic;
    padding: 1 0 0 0;
}

MarkdownBlockQuote {
    border-left: thick $primary;
    background: $primary 8%;
    padding: 0 2;
    margin: 1 0;
    color: $text-muted;
}

MarkdownHorizontalRule {
    color: $surface-lighten-3;
    height: 1;
    margin: 1 0;
}
"""


# ══════════════════════════════════════════════════════════════════════
#  Chat Message Widget (with action buttons: copy, regen, delete)
# ══════════════════════════════════════════════════════════════════════

class ChatMessage(Vertical):
    """A single chat message bubble with action buttons.

    During streaming, content is displayed in a lightweight Static widget
    (no DOM rebuilds). After streaming completes, finalize_content() swaps
    it for a full Markdown widget so code fences, headings, etc. render.
    """

    can_focus = False

    def __init__(
        self,
        role: str,
        content: str,
        msg_index: int,
        streaming: bool = False,
        **kwargs: Any,
    ) -> None:
        self.role = role
        self.content = content
        self.msg_index = msg_index
        self._streaming = streaming
        classes = "user-bubble" if role == "user" else "assistant-bubble"
        super().__init__(classes=classes, **kwargs)

    def compose(self) -> ComposeResult:
        icon = "👤  You" if self.role == "user" else "🤖  Assistant"
        yield Label(icon, classes="bubble-header")
        if self._streaming:
            # Use Static during streaming — .update() is a fast text swap,
            # no DOM tree rebuild, so it won't corrupt surrounding widgets.
            yield Static(self.content, classes="bubble-content")
        else:
            yield Markdown(self.content, classes="bubble-content")
        with Horizontal(classes="bubble-actions"):
            yield Button("📋", classes="bubble-action-btn", id=f"copy-{self.msg_index}")
            if self.role == "assistant":
                yield Button("🔄", classes="bubble-action-btn", id=f"regen-{self.msg_index}")
            yield Button("🗑", classes="bubble-action-btn", id=f"del-{self.msg_index}")

    def update_content(self, text: str) -> None:
        """Fast content update for streaming — Static.update(), no DOM rebuild."""
        self.content = text
        try:
            widget = self.query_one(".bubble-content", Static)
            widget.update(text)
        except NoMatches:
            pass

    async def finalize_content(self, text: str) -> None:
        """Swap the streaming Static for a Markdown widget (one-time DOM build)."""
        self.content = text
        self._streaming = False
        try:
            old = self.query_one(".bubble-content", Static)
            actions = self.query_one(".bubble-actions", Horizontal)
            md = Markdown(text, classes="bubble-content")
            await self.mount(md, before=actions)
            old.remove()
        except NoMatches:
            pass


# ══════════════════════════════════════════════════════════════════════
#  Chat Input Widget (reliable space-key handling)
# ══════════════════════════════════════════════════════════════════════

class ChatTextArea(TextArea):
    """Multi-line, auto-growing chat input.

    • Enter          — submit the message
    • Shift+Enter    — insert a newline (for multi-line prompts)
    • Height grows automatically (3–10 rows) as you type.
    """

    class Submit(TUIMessage):
        """Posted when the user presses Enter to send."""

        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    async def _on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            event.prevent_default()
            event.stop()
            text = self.text.strip()
            if text:
                self.clear()
                self.post_message(self.Submit(text))
            return
        # Textual marks space as non-printable in some builds;
        # handle it explicitly so typing spaces always works.
        if event.key == "space":
            event.prevent_default()
            event.stop()
            self.insert(" ")
            return
        await super()._on_key(event)


# ══════════════════════════════════════════════════════════════════════
#  Onboarding Screen (guided first-run)
# ══════════════════════════════════════════════════════════════════════

class OnboardingScreen(ModalScreen[str | None]):
    """Step-by-step guided setup for first-time users."""

    BINDINGS = [Binding("escape", "skip", "Skip")]

    def __init__(self, config: dict, provider_infos: list) -> None:
        super().__init__()
        self.config = config
        self.provider_infos = provider_infos

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="onboarding-dialog"):
            yield Label("⚡ Welcome to InLine AI!", id="onboarding-title")

            yield Static(
                "Let's get you set up in 30 seconds.\n"
                "InLine AI lets you chat with AI models right here in your terminal —\n"
                "no browser needed!\n",
                classes="onboarding-step",
            )

            # Step 1: Show detected providers
            yield Label("━━━ Step 1: Your AI Providers ━━━", classes="step-number")
            yield Static(
                "We scanned your system. Here's what we found:\n",
                classes="step-text",
            )

            for info in self.provider_infos:
                icon_mark = "✅" if info.available else "⬚ "
                if info.is_local and not info.available:
                    status = "Not running — start with: ollama serve"
                elif info.is_local and info.available:
                    model_count = len(info.models) if info.models else 0
                    status = f"Running ({model_count} models)" if model_count else "Running (pull a model: ollama pull llama3.2)"
                elif info.available:
                    status = "Ready!"
                else:
                    status = "Needs API key"

                with Horizontal(classes="onboarding-provider-row"):
                    yield Label(
                        f"  {icon_mark} {PROVIDER_ICONS.get(info.name, '•')}  {info.display_name}",
                        classes="onboarding-provider-name",
                    )
                    yield Label(f"  {status}", classes="onboarding-provider-status")

            # Step 2: Configure missing keys
            cloud_missing = [i for i in self.provider_infos if not i.is_local and not i.available]
            if cloud_missing:
                yield Static("")
                yield Label("━━━ Step 2: Add API Keys (optional) ━━━", classes="step-number")
                yield Static(
                    "Enter keys for providers you want to use.\n"
                    "Leave blank to skip — you can add them later in ⚙ Settings.\n",
                    classes="step-text",
                )
                for info in cloud_missing:
                    env_var = {
                        "openai": "OPENAI_API_KEY",
                        "anthropic": "ANTHROPIC_API_KEY",
                        "gemini": "GEMINI_API_KEY",
                        "groq": "GROQ_API_KEY",
                    }.get(info.name, "")
                    with Vertical(classes="setting-row"):
                        yield Label(
                            f"{PROVIDER_ICONS.get(info.name, '')}  {info.display_name}:",
                            classes="setting-label",
                        )
                        yield Input(
                            placeholder=f"Paste API key (or set {env_var} env var)",
                            password=True,
                            id=f"onboard-key-{info.name}",
                            classes="setting-input",
                        )

            # Buttons
            yield Button(
                "✅  Save & Start Chatting",
                id="onboarding-done-btn",
                variant="primary",
            )
            yield Button(
                "⏭  Skip — I'll set up later",
                id="onboarding-skip-btn",
                variant="default",
            )

    @on(Button.Pressed, "#onboarding-done-btn")
    def on_done(self) -> None:
        for name in ("openai", "anthropic", "gemini", "groq"):
            try:
                inp = self.query_one(f"#onboard-key-{name}", Input)
                key_val = inp.value.strip()
                if key_val:
                    if name not in self.config:
                        self.config[name] = {}
                    self.config[name]["api_key"] = key_val
            except NoMatches:
                pass
        save_config(self.config)
        self.dismiss("done")

    @on(Button.Pressed, "#onboarding-skip-btn")
    def on_skip(self) -> None:
        self.dismiss("skip")

    def action_skip(self) -> None:
        self.dismiss("skip")

    def on_mount(self) -> None:
        """Focus the first input or button for keyboard navigation."""
        try:
            self.query("Input").first().focus()
        except NoMatches:
            try:
                self.query_one("#onboarding-done-btn", Button).focus()
            except NoMatches:
                pass


# ══════════════════════════════════════════════════════════════════════
#  Settings Screen
# ══════════════════════════════════════════════════════════════════════

class SettingsScreen(ModalScreen[bool]):
    """Settings modal with clear guidance for each provider."""

    BINDINGS = [Binding("escape", "dismiss_settings", "Close")]

    def __init__(self, config: dict) -> None:
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="settings-dialog"):
            yield Label("⚙  Settings", id="settings-title")

            yield Label("━━━ Cloud API Keys ━━━", classes="settings-section-title")
            yield Static(
                "Paste your API keys below. They're saved locally at\n"
                "~/.config/inline-cli/config.toml and never sent anywhere.\n",
                classes="setting-help",
            )

            providers = [
                ("openai", "ChatGPT (OpenAI)", "OPENAI_API_KEY"),
                ("anthropic", "Claude (Anthropic)", "ANTHROPIC_API_KEY"),
                ("gemini", "Gemini (Google)", "GEMINI_API_KEY"),
                ("groq", "Groq", "GROQ_API_KEY"),
            ]

            for key, display_name, env_var in providers:
                with Vertical(classes="setting-row"):
                    yield Label(
                        f"{PROVIDER_ICONS.get(key, '')}  {display_name}:",
                        classes="setting-label",
                    )
                    current = self.config.get(key, {}).get("api_key", "")
                    with Horizontal(classes="key-row"):
                        yield Input(
                            value=current,
                            placeholder=f"Paste key (or export {env_var})",
                            password=True,
                            id=f"key-{key}",
                        )
                        yield Button(
                            "🧪 Test",
                            id=f"test-{key}",
                            classes="test-btn",
                            variant="default",
                        )
                    yield Static("", id=f"test-result-{key}", classes="test-result")

            yield Static("")
            yield Label("━━━ Local Models ━━━", classes="settings-section-title")
            yield Static(
                "Ollama runs models on your machine — no API key needed.\n"
                "Install: brew install ollama && ollama serve\n",
                classes="setting-help",
            )
            with Vertical(classes="setting-row"):
                yield Label("🏠  Ollama URL:", classes="setting-label")
                yield Input(
                    value=self.config.get("ollama", {}).get("base_url", "http://localhost:11434"),
                    placeholder="http://localhost:11434",
                    id="ollama-url",
                    classes="setting-input",
                )

            with Horizontal(id="settings-buttons"):
                yield Button("💾  Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    @on(Button.Pressed, ".test-btn")
    async def on_test_key(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if not btn_id.startswith("test-"):
            return
        provider_name = btn_id.replace("test-", "")
        try:
            inp = self.query_one(f"#key-{provider_name}", Input)
            result_label = self.query_one(f"#test-result-{provider_name}", Static)
        except NoMatches:
            return

        api_key = inp.value.strip()
        if not api_key:
            result_label.update("  ⚠️  Paste an API key first.")
            return

        result_label.update("  ⏳ Testing...")
        event.button.disabled = True
        try:
            ok = await self._test_api_key(provider_name, api_key)
            if ok:
                result_label.update("  ✅ Key works! Connection successful.")
            else:
                result_label.update("  ❌ Key failed — check it and try again.")
        except Exception as e:
            result_label.update(f"  ❌ Error: {e}")
        finally:
            event.button.disabled = False

    async def _test_api_key(self, provider_name: str, api_key: str) -> bool:
        """Make a minimal API call to verify the key works."""
        if provider_name == "openai":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
            await client.models.list()
            return True
        elif provider_name == "anthropic":
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=api_key)
            await client.models.list(limit=1)
            return True
        elif provider_name == "gemini":
            from google import genai
            client = genai.Client(api_key=api_key)
            pager = await client.aio.models.list()
            models = []
            async for m in pager:
                models.append(m)
                if len(models) >= 1:
                    break
            return True
        elif provider_name == "groq":
            from groq import AsyncGroq
            client = AsyncGroq(api_key=api_key)
            await client.models.list()
            return True
        return False

    @on(Button.Pressed, "#save-btn")
    def on_save(self) -> None:
        for key in ("openai", "anthropic", "gemini", "groq"):
            try:
                inp = self.query_one(f"#key-{key}", Input)
                if key not in self.config:
                    self.config[key] = {}
                self.config[key]["api_key"] = inp.value.strip()
            except NoMatches:
                pass
        try:
            ollama_url = self.query_one("#ollama-url", Input)
            if "ollama" not in self.config:
                self.config["ollama"] = {}
            self.config["ollama"]["base_url"] = ollama_url.value.strip()
        except NoMatches:
            pass

        save_config(self.config)
        self.notify("✅ Settings saved! Providers will be re-scanned.", severity="information")
        self.dismiss(True)

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel(self) -> None:
        self.dismiss(False)

    def action_dismiss_settings(self) -> None:
        self.dismiss(False)

    def on_mount(self) -> None:
        """Focus the first input for keyboard navigation."""
        try:
            self.query("Input").first().focus()
        except NoMatches:
            pass


# ══════════════════════════════════════════════════════════════════════
#  Main Application
# ══════════════════════════════════════════════════════════════════════

class InlineApp(App):
    """InLine AI — ChatGPT-like experience in your terminal."""

    TITLE = "InLine AI"
    CSS = APP_CSS

    BINDINGS = [
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+p", "toggle_sidebar", "Sidebar"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    current_provider: reactive[str] = reactive("ollama")
    current_model: reactive[str] = reactive("")
    is_streaming: reactive[bool] = reactive(False)

    def __init__(self, force_onboarding: bool = False) -> None:
        super().__init__()
        self.config = load_config()
        self.registry = ProviderRegistry(self.config)
        self.chat_history: list[Message] = []
        self.msg_counter = 0
        self._available_models: list[str] = []
        self._cancel_streaming = False
        self._force_onboarding = force_onboarding

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal():
            # ── Sidebar ──
            with Vertical(id="sidebar"):
                yield Label("⚡ InLine AI", id="sidebar-title")
                yield Button("✨  New Chat", id="new-chat-btn", variant="primary")

                yield Label("─── Providers ───", classes="sidebar-section-title")

                for name in self.registry.names():
                    icon = PROVIDER_ICONS.get(name, "•")
                    display = PROVIDER_DISPLAY_NAMES.get(name, name)
                    btn_classes = "provider-btn"
                    if name == self.current_provider:
                        btn_classes += " active"
                    yield Button(
                        f"{icon}  {display}",
                        id=f"provider-{name}",
                        classes=btn_classes,
                        variant="default",
                    )

                yield Label("─── Model ───", classes="sidebar-section-title")
                yield Select(
                    [("Loading...", "__loading__")],
                    id="model-select",
                    allow_blank=True,
                    prompt="Select model",
                )

                yield Static("Scanning...", id="status-bar")
                yield Label("───────────", classes="sidebar-divider")
                yield Button("⚙  Settings", id="settings-btn", variant="default")

            # ── Main Chat Area ──
            with Vertical(id="main-area"):
                with VerticalScroll(id="chat-scroll"):
                    with Center(id="welcome-container"):
                        yield Static("⚡ InLine AI", id="welcome-logo")
                        yield Static(
                            "Chat with AI right in your terminal.\n"
                            "No browser. No tabs. No friction.\n",
                            id="welcome-subtitle",
                        )
                        yield Static(
                            "①  Pick a provider in the sidebar\n"
                            "②  Type your message below\n"
                            "③  Press  Enter ↵  or click  Send ➤\n\n"
                            "📋 Copy  ·  🔄 Regen  ·  🗑 Delete  on any message\n\n"
                            "Ctrl+N  New chat     Ctrl+P  Sidebar     Ctrl+Q  Quit",
                            id="welcome-hints",
                        )

                yield Static("", id="streaming-bar")

                with Vertical(id="input-area"):
                    yield Static("", id="input-context")
                    with Horizontal(id="input-row"):
                        yield ChatTextArea(
                            "",
                            id="chat-input",
                            show_line_numbers=False,
                            soft_wrap=True,
                        )
                        yield Button("Send ➤", id="send-btn", variant="primary")
                        yield Button("■ Stop", id="stop-btn", variant="error")
                    yield Static(
                        "Enter ↵  send  ·  Shift+Enter  newline",
                        id="input-hint",
                    )

        yield Footer()

    # ── Lifecycle ──────────────────────────────────────────────────────

    async def on_mount(self) -> None:
        self.query_one("#chat-input", ChatTextArea).focus()
        self.run_worker(self._startup_scan())

    def on_key(self, event: events.Key) -> None:
        """When user types while chat scroll has focus, redirect to input."""
        if isinstance(self.screen, ModalScreen):
            return
        if not isinstance(self.focused, (Input, TextArea)):
            try:
                self.query_one("#chat-input", ChatTextArea).focus()
            except (NoMatches, AttributeError):
                pass

    async def _startup_scan(self) -> None:
        status = self.query_one("#status-bar", Static)
        status.update("⏳ Scanning providers...")

        infos = await self.registry.scan_availability()
        available_count = sum(1 for i in infos if i.available)
        status.update(f"✅ {available_count}/{len(infos)} providers ready")

        # Update provider buttons with status
        for info in infos:
            try:
                btn = self.query_one(f"#provider-{info.name}", Button)
                icon = PROVIDER_ICONS.get(info.name, "•")
                display = PROVIDER_DISPLAY_NAMES.get(info.name, info.name)
                mark = "✓" if info.available else "✗"
                btn.label = f"{icon}  {display}  {mark}"
                if info.available:
                    btn.remove_class("unavailable")
                else:
                    btn.add_class("unavailable")
            except NoMatches:
                pass

        best = await self.registry.detect_default()
        self.current_provider = best
        self._highlight_provider_btn(best)
        await self._refresh_models()

        # Show onboarding if first run, forced via --setup, or nothing configured
        from .config import CONFIG_FILE
        cloud_ready = any(i.available and not i.is_local for i in infos)
        if self._force_onboarding or not CONFIG_FILE.exists() or (not cloud_ready and available_count == 0):
            self.push_screen(
                OnboardingScreen(self.config, infos),
                callback=self._on_onboarding_done,
            )

    def _on_onboarding_done(self, result: str | None) -> None:
        if result == "done":
            self.config = load_config()
            self.registry = ProviderRegistry(self.config)
            self.run_worker(self._startup_scan())
            self.notify("🎉 Setup complete! Start chatting.", severity="information")

    # ── Provider switching ─────────────────────────────────────────────

    def _highlight_provider_btn(self, active_name: str) -> None:
        for name in self.registry.names():
            try:
                btn = self.query_one(f"#provider-{name}", Button)
                if name == active_name:
                    btn.add_class("active")
                else:
                    btn.remove_class("active")
            except NoMatches:
                pass

    @on(Button.Pressed, ".provider-btn")
    async def on_provider_btn(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if not btn_id.startswith("provider-"):
            return

        name = btn_id.replace("provider-", "")
        provider = self.registry.get(name)
        if not provider:
            return

        available = await provider.check_available()
        if not available:
            if getattr(provider, "is_local", False):
                self.notify(
                    f"⚠️  {PROVIDER_DISPLAY_NAMES.get(name, name)} is not running.\n"
                    "👉 Start it with: ollama serve\n"
                    "👉 Then pull a model: ollama pull llama3.2",
                    severity="warning",
                    timeout=6,
                )
            else:
                api_key = get_api_key(name, self.config)
                if not api_key:
                    self.notify(
                        f"🔑 No API key for {PROVIDER_DISPLAY_NAMES.get(name, name)}.\n"
                        "👉 Click ⚙ Settings in the sidebar to add your key.",
                        severity="warning",
                        timeout=6,
                    )
                else:
                    self.notify(
                        f"⚠️  Can't reach {PROVIDER_DISPLAY_NAMES.get(name, name)}.\n"
                        "👉 Check your internet or API key in Settings.",
                        severity="warning",
                        timeout=6,
                    )
            return

        self.current_provider = name
        self._highlight_provider_btn(name)
        await self._refresh_models()
        self.notify(
            f"Switched to {PROVIDER_ICONS.get(name, '')} {PROVIDER_DISPLAY_NAMES.get(name, name)}",
            severity="information",
            timeout=2,
        )
        try:
            self.query_one("#chat-input", ChatTextArea).focus()
        except NoMatches:
            pass

    async def _refresh_models(self) -> None:
        model_select = self.query_one("#model-select", Select)
        provider = self.registry.get(self.current_provider)
        if not provider:
            model_select.set_options([("No provider", "__none__")])
            return

        try:
            available = await provider.check_available()
            models = await provider.list_models() if available else []
        except Exception:
            models = []

        if not models:
            default_model = self.config.get(self.current_provider, {}).get("model", "")
            if default_model:
                models = [default_model]

        self._available_models = models

        if models:
            options = [(m, m) for m in models]
            model_select.set_options(options)
            default = self.config.get(self.current_provider, {}).get("model", models[0])
            if default in models:
                model_select.value = default
                self.current_model = default
            else:
                model_select.value = models[0]
                self.current_model = models[0]
        else:
            model_select.set_options([("No models available", "__none__")])

        self._update_input_context()

    @on(Select.Changed, "#model-select")
    def on_model_changed(self, event: Select.Changed) -> None:
        val = event.value
        if val and val != Select.BLANK and val != "__none__" and val != "__loading__":
            self.current_model = str(val)

    # ── Sending messages ───────────────────────────────────────────────

    @on(Button.Pressed, "#send-btn")
    async def on_send_click(self) -> None:
        try:
            ta = self.query_one("#chat-input", ChatTextArea)
            text = ta.text.strip()
            if text:
                ta.clear()
                await self._send_message(text)
        except NoMatches:
            pass

    @on(ChatTextArea.Submit)
    async def on_chat_input_submit(self, event: ChatTextArea.Submit) -> None:
        await self._send_message(event.text)

    @on(Button.Pressed, "#stop-btn")
    def on_stop_click(self) -> None:
        self._cancel_streaming = True

    @on(TextArea.Changed, "#chat-input")
    def on_chat_input_changed(self, event: TextArea.Changed) -> None:
        """Auto-grow the input area as the user types (3–10 rows)."""
        if isinstance(event.control, TextArea):
            lines = event.control.document.line_count
            event.control.styles.height = max(3, min(lines + 2, 10))

    async def _send_message(self, text: str) -> None:
        if self.is_streaming:
            self.notify("⏳ Please wait for the current response to finish.", severity="warning")
            return

        if not text:
            return

        # Remove welcome screen
        try:
            self.query_one("#welcome-container").remove()
        except NoMatches:
            pass

        # Validate provider
        provider = self.registry.get(self.current_provider)
        if not provider:
            self.notify(
                "❌ No provider selected.\n"
                "👉 Click a provider button in the sidebar.",
                severity="error",
            )
            return

        # Check API key for cloud providers
        if not getattr(provider, "is_local", False):
            api_key = get_api_key(self.current_provider, self.config)
            if not api_key:
                self.notify(
                    f"🔑 API key needed for {PROVIDER_DISPLAY_NAMES.get(self.current_provider, '')}.\n"
                    "👉 Click ⚙ Settings in the sidebar to add it.\n"
                    "👉 Or switch to 🏠 Ollama (local, free, no key needed).",
                    severity="error",
                    timeout=8,
                )
                return

        # Check reachability
        try:
            reachable = await provider.check_available()
        except Exception:
            reachable = False

        if not reachable:
            if getattr(provider, "is_local", False):
                self.notify(
                    "⚠️  Ollama is not running.\n"
                    "👉 Open a new terminal and run: ollama serve\n"
                    "👉 Then pull a model: ollama pull llama3.2\n"
                    "👉 Come back here and try again!",
                    severity="error",
                    timeout=8,
                )
            else:
                self.notify(
                    f"⚠️  Can't reach {PROVIDER_DISPLAY_NAMES.get(self.current_provider, '')}.\n"
                    "👉 Check your internet connection.\n"
                    "👉 Verify your API key in ⚙ Settings.",
                    severity="error",
                    timeout=8,
                )
            return

        # Mount user message
        self.chat_history.append(Message(role="user", content=text))
        self.msg_counter += 1
        user_bubble = ChatMessage("user", text, self.msg_counter, id=f"msg-{self.msg_counter}")
        chat_scroll = self.query_one("#chat-scroll", VerticalScroll)
        await chat_scroll.mount(user_bubble)
        chat_scroll.scroll_end(animate=False)

        # Stream AI response
        self.is_streaming = True
        self._cancel_streaming = False
        self._show_streaming(True)
        self.run_worker(self._stream_response(provider))

    async def _stream_response(self, provider: Any) -> None:
        self.msg_counter += 1
        msg_idx = self.msg_counter

        chat_scroll = self.query_one("#chat-scroll", VerticalScroll)

        # streaming=True → uses Static (fast text swap, no DOM rebuilds)
        assistant_bubble = ChatMessage("assistant", "▍", msg_idx, streaming=True, id=f"msg-{msg_idx}")
        await chat_scroll.mount(assistant_bubble)
        chat_scroll.scroll_end(animate=False)

        full_text = ""
        try:
            async for chunk in provider.stream_chat(
                self.chat_history,
                model=self.current_model or None,
            ):
                if self._cancel_streaming:
                    full_text += "\n\n*[Generation stopped]*"
                    break
                full_text += chunk
                assistant_bubble.update_content(full_text + " ▍")
                chat_scroll.scroll_end(animate=False)

            # One-time swap: Static → Markdown for proper rendering
            final_text = full_text or "*[Empty response]*"
            await assistant_bubble.finalize_content(final_text)
            if full_text:
                self.chat_history.append(Message(role="assistant", content=full_text))

        except Exception as e:
            error_text = (
                f"**❌ Error:** {e}\n\n"
                "*💡 Tip: Check your API key in ⚙ Settings, or try a different provider.*"
            )
            await assistant_bubble.finalize_content(error_text)
            self.notify(f"Error: {e}", severity="error", timeout=5)
        finally:
            self.is_streaming = False
            self._cancel_streaming = False
            self._show_streaming(False)
            chat_scroll.scroll_end(animate=False)
            self.query_one("#chat-input", ChatTextArea).focus()

    def _update_input_context(self, streaming: bool = False) -> None:
        """Refresh the provider/model strip above the chat input."""
        try:
            ctx = self.query_one("#input-context", Static)
            icon = PROVIDER_ICONS.get(self.current_provider, "•")
            name = PROVIDER_DISPLAY_NAMES.get(self.current_provider, self.current_provider)
            if streaming:
                ctx.update(f"  ◉  {icon} {name}  is generating…")
            else:
                model = self.current_model or "—"
                ctx.update(f"  {icon}  {name}  ·  {model}")
        except NoMatches:
            pass

    def _show_streaming(self, show: bool) -> None:
        bar = self.query_one("#streaming-bar", Static)
        send_btn = self.query_one("#send-btn", Button)
        stop_btn = self.query_one("#stop-btn", Button)
        if show:
            provider_name = PROVIDER_DISPLAY_NAMES.get(self.current_provider, "AI")
            bar.update(f"  ◉  {provider_name} is generating a response…   ■ Stop to cancel")
            bar.add_class("visible")
            send_btn.add_class("streaming")
            stop_btn.add_class("visible")
            self._update_input_context(streaming=True)
        else:
            bar.update("")
            bar.remove_class("visible")
            send_btn.remove_class("streaming")
            stop_btn.remove_class("visible")
            self._update_input_context(streaming=False)

    # ── Message action buttons ─────────────────────────────────────────

    @on(Button.Pressed)
    async def on_any_button(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""

        if btn_id.startswith("copy-"):
            idx = int(btn_id.replace("copy-", ""))
            bubble = self._find_bubble(idx)
            if bubble:
                try:
                    pyperclip.copy(bubble.content)
                    self.notify("📋 Copied to clipboard!", severity="information", timeout=2)
                except Exception:
                    self.notify(
                        "📋 Copy not available.\n"
                        "👉 Install xclip (Linux) or it should work on macOS automatically.",
                        severity="warning",
                    )
            try:
                self.query_one("#chat-input", ChatTextArea).focus()
            except NoMatches:
                pass

        elif btn_id.startswith("del-"):
            idx = int(btn_id.replace("del-", ""))
            bubble = self._find_bubble(idx)
            if bubble:
                bubble.remove()
                self.notify("🗑 Message removed", severity="information", timeout=2)
            try:
                self.query_one("#chat-input", ChatTextArea).focus()
            except NoMatches:
                pass

        elif btn_id.startswith("regen-"):
            if self.is_streaming:
                self.notify("⏳ Wait for the current response to finish.", severity="warning")
                return
            idx = int(btn_id.replace("regen-", ""))
            bubble = self._find_bubble(idx)
            if bubble:
                if self.chat_history and self.chat_history[-1].role == "assistant":
                    self.chat_history.pop()
                bubble.remove()
                provider = self.registry.get(self.current_provider)
                if provider:
                    self.is_streaming = True
                    self._cancel_streaming = False
                    self._show_streaming(True)
                    self.run_worker(self._stream_response(provider))

    def _find_bubble(self, msg_index: int) -> ChatMessage | None:
        try:
            return self.query_one(f"#msg-{msg_index}", ChatMessage)
        except NoMatches:
            return None

    # ── Sidebar buttons ────────────────────────────────────────────────

    @on(Button.Pressed, "#new-chat-btn")
    async def on_new_chat_btn(self) -> None:
        await self.action_new_chat()

    @on(Button.Pressed, "#settings-btn")
    def on_settings_btn(self) -> None:
        self.push_screen(
            SettingsScreen(self.config),
            callback=self._on_settings_done,
        )

    def _on_settings_done(self, saved: bool | None) -> None:
        if saved:
            self.config = load_config()
            self.registry = ProviderRegistry(self.config)
            self.run_worker(self._startup_scan())

    # ── Actions ────────────────────────────────────────────────────────

    async def action_new_chat(self) -> None:
        if self.is_streaming:
            self._cancel_streaming = True
            self.is_streaming = False
            self._show_streaming(False)
        self.chat_history.clear()
        self.msg_counter = 0
        chat_scroll = self.query_one("#chat-scroll", VerticalScroll)
        await chat_scroll.remove_children()

        welcome = Center(id="welcome-container")
        await chat_scroll.mount(welcome)
        await welcome.mount(
            Static("⚡ InLine AI", id="welcome-logo"),
            Static(
                "New chat started! Type your message below.\n",
                id="welcome-subtitle",
            ),
        )
        self.notify("✨ New chat started!", severity="information", timeout=2)
        self.query_one("#chat-input", ChatTextArea).focus()

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar")
        sidebar.toggle_class("hidden")