"""Animated startup banner and easter eggs for acra.

This module owns the ANSI-driven intro sequence shown when the interactive
shell starts (`acra` with no subcommand, or `acra serve`):

    1. The "ACRA" wordmark is revealed with a left-to-right glitch/scan
       animation (or, in --party mode, a rainbow cycle with an emoji burst).
    2. A subtitle is typed out character by character.
    3. A tagline fades in (swapped for a holiday-specific line on a handful
       of dates).
    4. The version number is shown with a short spinner that resolves to a
       "ready" checkmark, similar to Copilot CLI's startup indicator.

Everything here is pure ANSI escape codes + stdlib (no extra dependencies).

Two independent accessibility/scripting gates, matching conventions used
across the CLI ecosystem (see https://no-color.org, https://force-color.org,
and GitHub's writeup on building the Copilot CLI banner: fast-changing
terminal output is a real screen-reader and low-vision concern, not just a
cosmetic one):

  * Color (`_supports_color`) is disabled by NO_COLOR or TERM=dumb, and can
    be forced back on with FORCE_COLOR even when piped.
  * Timed motion (`_animations_enabled`) is disabled whenever stdout isn't a
    real interactive terminal, in CI, or when ACRA_NO_ANIMATION is set -
    falling back to an instant, fully-resolved static print so scripting,
    piping, and tests stay fast and deterministic.

These are independent: a NO_COLOR user on a real terminal still gets the
scan/typing motion, just monochrome; a CI run gets neither, instantly.
"""

from __future__ import annotations

import os
import random
import sys
import time
from datetime import date
from typing import Iterable, List, Optional

from acra import __version__
from acra.ui.banner import WELCOME_TEXT

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
}

# ANSI-Shadow-style block glyphs. Only the letters ACRA needs are defined;
# each glyph is a fixed 6-row x 8-column block so rows line up cleanly
# whichever letters are combined.
_GLYPHS = {
    "A": [
        " █████╗ ",
        "██╔══██╗",
        "███████║",
        "██╔══██║",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ],
    "C": [
        " ██████╗",
        "██╔════╝",
        "██║     ",
        "██║     ",
        "╚██████╗",
        " ╚═════╝",
    ],
    "R": [
        "██████╗ ",
        "██╔══██╗",
        "██████╔╝",
        "██╔══██╗",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ],
}

WORDMARK = "ACRA"
_GLYPH_HEIGHT = 6

# Vertical gradient applied to the wordmark, top row to bottom row.
_GRADIENT = ["bright_cyan", "bright_cyan", "cyan", "bright_magenta", "magenta", "bright_yellow"]

_RAINBOW_CYCLE = [
    "bright_red",
    "bright_yellow",
    "bright_green",
    "bright_cyan",
    "bright_blue",
    "bright_magenta",
]

_GLITCH_CHARS = "@#$%&*+=-/\\|<>?░▒▓"
_PARTY_EMOJIS = ["🎉", "✨", "🎊", "🚀", "🔥", "🥳", "⭐", "💥"]

# Same frame set as the "dots" spinner in the widely-used cli-spinners
# package (npm), the de facto standard braille spinner recognized across
# npm/yarn/ora-based tools.
_SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

_HOLIDAY_TAGLINES = {
    (1, 1): "New year, new agent runs. Let's build.",
    (4, 1): "ACRA: (mostly) not lying to you today.",
    (10, 31): "ACRA: coding like it's Halloween.",
    (12, 25): "Shipping code, not presents, today.",
}


def _supports_color() -> bool:
    """https://no-color.org / https://force-color.org, checked in that order."""
    if os.environ.get("FORCE_COLOR", "") != "":
        return True
    if os.environ.get("NO_COLOR", "") != "":
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return True


def _animations_enabled() -> bool:
    """Whether to run the timed ANSI animations, or fall back to a static print."""
    if os.environ.get("ACRA_NO_ANIMATION"):
        return False
    if os.environ.get("CI"):
        return False
    return sys.stdout.isatty()


def _style(text: str, color: Optional[str] = None, bold: bool = False, dim: bool = False) -> str:
    """Wrap text in ANSI codes, or return it unchanged when color is disabled."""
    if not _supports_color():
        return text
    codes = ""
    if bold:
        codes += BOLD
    if dim:
        codes += DIM
    if color:
        codes += COLORS.get(color, "")
    return f"{codes}{text}{RESET}" if codes else text


def _build_art(word: str = WORDMARK, spacing: str = " ") -> List[str]:
    return [spacing.join(_GLYPHS[letter][row] for letter in word) for row in range(_GLYPH_HEIGHT)]


def _print_art_static(art_lines: Iterable[str], gradient: List[str]) -> None:
    for row_idx, line in enumerate(art_lines):
        print(_style(line, color=gradient[row_idx % len(gradient)], bold=True))


def _glitch_scan_reveal(art_lines: List[str], gradient: List[str], steps: int = 10, delay: float = 0.025) -> None:
    """Reveal the wordmark left-to-right, resolving glitch characters into the real ones."""
    if not _animations_enabled():
        _print_art_static(art_lines, gradient)
        return

    width = max(len(line) for line in art_lines)
    height = len(art_lines)

    sys.stdout.write("\n" * height)
    for step in range(1, steps + 1):
        threshold = int(width * step / steps)
        sys.stdout.write(f"\033[{height}A")
        for row_idx, line in enumerate(art_lines):
            rendered = [
                " " if ch == " " else (ch if col < threshold else random.choice(_GLITCH_CHARS))
                for col, ch in enumerate(line)
            ]
            styled = _style("".join(rendered), color=gradient[row_idx % len(gradient)], bold=True)
            sys.stdout.write(f"\033[K{styled}\n")
        sys.stdout.flush()
        time.sleep(delay)


def _party_reveal(art_lines: List[str], frames: int = 10, delay: float = 0.09) -> None:
    """Rainbow-cycling wordmark with a burst of flying emojis, for --party / --easter-egg."""
    if not _animations_enabled():
        print(_style("PARTY MODE \U0001f389", color="bright_magenta", bold=True))
        _print_art_static(art_lines, _RAINBOW_CYCLE)
        return

    width = max(len(line) for line in art_lines)
    height = len(art_lines)

    sys.stdout.write("\n" * (height + 1))
    for frame in range(frames):
        sys.stdout.write(f"\033[{height + 1}A")
        for row_idx, line in enumerate(art_lines):
            color = _RAINBOW_CYCLE[(row_idx + frame) % len(_RAINBOW_CYCLE)]
            sys.stdout.write(f"\033[K{_style(line, color=color, bold=True)}\n")
        emoji_row = "".join(
            random.choice(_PARTY_EMOJIS) if random.random() < 0.3 else " " for _ in range(width // 2)
        )
        sys.stdout.write(f"\033[K{emoji_row}\n")
        sys.stdout.flush()
        time.sleep(delay)

    print(_style("\U0001f389 PARTY MODE ACTIVATED \U0001f389", color="bright_magenta", bold=True))


def _type_line(text: str, color: Optional[str] = None, delay: float = 0.012) -> None:
    if not _animations_enabled():
        print(_style(text, color=color))
        return
    for ch in text:
        sys.stdout.write(_style(ch, color=color))
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")


def _fade_in_lines(lines: Iterable[str], dim: bool = False, delay: float = 0.12) -> None:
    for line in lines:
        if _animations_enabled():
            time.sleep(delay)
        print(_style(line, dim=dim))


def _spinner_version_line(accent: str, frames: int = 14, delay: float = 0.035) -> None:
    """Show 'acra vX.Y.Z' with a small spinner that resolves into a ready check."""
    label = _style(f"acra v{__version__}", color=accent, bold=True)
    ready = _style("\u2713 ready", color="bright_green")

    if not _animations_enabled():
        print(f"{label}  {ready}")
        return

    for i in range(frames):
        frame = _SPINNER_FRAMES[i % len(_SPINNER_FRAMES)]
        status = _style(f"{frame} initializing\u2026", dim=True)
        sys.stdout.write(f"\r{label}  {status}\033[K")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(f"\r{label}  {ready}\033[K\n")
    sys.stdout.flush()


def _holiday_tagline(today: Optional[date] = None) -> Optional[str]:
    today = today or date.today()
    return _HOLIDAY_TAGLINES.get((today.month, today.day))


def render_intro(theme: Optional[dict] = None, party: bool = False) -> None:
    """Print the full animated acra startup banner.

    `theme` is one of the dicts from acra.ui.theme (must contain "accent").
    `party` triggers the rainbow/emoji easter egg instead of the normal
    glitch-scan reveal; wired up to `acra --party` / `acra --easter-egg`.
    """
    theme = theme or {}
    accent = theme.get("accent", "bright_cyan")
    if accent not in COLORS:
        accent = "bright_cyan"

    art = _build_art()

    if party:
        _party_reveal(art)
    else:
        _glitch_scan_reveal(art, _GRADIENT)

    _type_line("Autonomous Coding & Research Agent", color=accent)

    tagline = _holiday_tagline() or WELCOME_TEXT
    _fade_in_lines([tagline], dim=True)

    _spinner_version_line(accent)