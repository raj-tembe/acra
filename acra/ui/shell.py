"""Interactive shell implementation for acra."""

import os
import shlex
import subprocess
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
from acra.ui.banner import render_banner, render_tips
from acra.ui.animated_banner import render_intro
from acra.ui.theme import get_theme
from acra.config.profile_manager import ProfileManager
from rich.console import Console
from rich.panel import Panel

console = Console()


def _slash_completions():
    commands = ["serve", "init", "config show", "keys list", "research", "memory list", "session list", "graph show", "brain models"]
    for command in commands:
        yield Completion(command, start_position=0)


class SlashCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("/"):
            for completion in _slash_completions():
                yield completion


def launch_shell(profile: str = None, workspace: str = None, party: bool = False):
    config = ProfileManager().load_profile(profile)
    theme = get_theme(config.get("theme", "dark-orange"))
    render_intro(theme, party=party)
    banner = render_banner(
        config.get("provider", "gemini"),
        config.get("model", "gemini-2.5-flash"),
        profile or "default",
        workspace or config.get("workspace", "."),
        theme,
    )
    console.print(banner)
    console.print(render_tips(theme))
    session = PromptSession(
        "> "
    )
    while True:
        try:
            user_input = session.prompt(
                "> ",
                completer=SlashCompleter(),
                complete_style=CompleteStyle.COLUMN,
            )
            if user_input in ("exit", "quit", "q", "Ctrl+C"):
                break
            if not user_input.strip():
                continue

            command_text = user_input.strip()
            if command_text.startswith("acra "):
                command_text = command_text[len("acra "):]

            if command_text in ("exit", "quit", "q"):
                break

            console.print(f"[dim]→[/dim] {user_input}")

            cmd = [sys.executable, "-m", "acra"] + shlex.split(command_text)
            # stdout/stderr are inherited (not captured) so the child process
            # sees a real tty and any live output -- the run_with_spinner
            # progress indicator, the animated banner, streamed agent output
            # -- renders in real time instead of being buffered up and
            # dumped all at once after the command finishes.
            completed = subprocess.run(
                cmd,
                cwd=os.getcwd(),
            )
            if completed.returncode != 0:
                console.print(f"[bold red]Command failed with exit code {completed.returncode}.[/bold red]")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

    console.print(Panel("Goodbye", title="acra"))