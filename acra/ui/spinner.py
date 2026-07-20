"""Live 'running' spinner for long agent tasks.

`acra ask/build/fix/review/explain/run` can take anywhere from a few
seconds to a couple of minutes (planner -> researcher -> coder -> executor
-> critic, each an LLM call), and until now the terminal went completely
silent between hitting enter and the result panel appearing. This wraps a
blocking call with the same braille spinner used in the animated startup
banner (acra/ui/animated_banner.py), showing live progress and elapsed
time instead.

Kept as a small, self-contained module (rather than importing the
startup-banner internals) so a bug here can't affect the startup banner
and vice versa; the animation/color gating logic is intentionally
duplicated in miniature from animated_banner.py, honoring the same
conventions (NO_COLOR, FORCE_COLOR, TERM=dumb, CI, ACRA_NO_ANIMATION).
"""

import os
import sys
import threading
import time
from typing import Any, Callable

RESET = "\033[0m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[92m"

_SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def _animations_enabled() -> bool:
    if os.environ.get("ACRA_NO_ANIMATION"):
        return False
    if os.environ.get("CI"):
        return False
    return sys.stdout.isatty()


def _supports_color() -> bool:
    if os.environ.get("FORCE_COLOR", "") != "":
        return True
    if os.environ.get("NO_COLOR", "") != "":
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return True


def run_with_spinner(fn: Callable[..., Any], *args, message: str = "Working", **kwargs) -> Any:
    """Run fn(*args, **kwargs) on a background thread, showing a live spinner
    with elapsed time until it finishes. Returns fn's return value, or
    re-raises whatever exception fn raised.

    Falls back to a single static line and a plain blocking call when
    stdout isn't a real interactive terminal (piped, CI, ACRA_NO_ANIMATION),
    so scripted/piped invocations pay no animation cost and never see
    raw escape codes leaking into logs.
    """
    if not _animations_enabled():
        print(f"{message}...")
        return fn(*args, **kwargs)

    outcome: dict = {}

    def _target():
        try:
            outcome["value"] = fn(*args, **kwargs)
        except BaseException as exc:  # re-raised on the main thread below
            outcome["error"] = exc

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()

    color = CYAN if _supports_color() else ""
    reset = RESET if _supports_color() else ""
    dim = DIM if _supports_color() else ""
    green = GREEN if _supports_color() else ""

    start = time.time()
    frame_idx = 0
    while thread.is_alive():
        frame = _SPINNER_FRAMES[frame_idx % len(_SPINNER_FRAMES)]
        elapsed = time.time() - start
        sys.stdout.write(f"\r{color}{frame}{reset} {dim}{message}\u2026 {elapsed:0.1f}s{reset}\033[K")
        sys.stdout.flush()
        time.sleep(0.08)
        frame_idx += 1
    thread.join()

    elapsed = time.time() - start
    sys.stdout.write(f"\r{green}\u2713{reset} {message} ({elapsed:.1f}s){' ' * 12}\n")
    sys.stdout.flush()

    if "error" in outcome:
        raise outcome["error"]
    return outcome.get("value")