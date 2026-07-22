"""Live 'running' spinner for long agent tasks.

`acra ask/build/fix/review/explain/run` can take anywhere from a few
seconds to a couple of minutes (planner -> researcher -> coder -> executor
-> critic, each an LLM call), and until now the terminal went completely
silent between hitting enter and the result panel appearing. This wraps a
blocking call with the same braille spinner used in the animated startup
banner (acra/ui/animated_banner.py), showing live progress and elapsed
time instead.

run_workflow_with_thoughts goes further: rather than a single opaque
spinner for the whole run, it streams the graph node by node
(LangGraph's stream_mode="updates") and prints each agent's own status
message -- the same "Planner Agent: ...", "Research Agent: ...",
"Coding Agent: ..." text each node already builds for its part of the
final activity log (see acra.utils.output_formatter) -- the moment that
node finishes, with a live spinner covering the gap while the next node
is still running. This is acra's "thought process": what it's doing and
why, surfaced as it happens instead of only appearing, already finished,
inside the result panel 30-40 seconds later.

Kept as a small, self-contained module (rather than importing the
startup-banner internals) so a bug here can't affect the startup banner
and vice versa; the animation/color gating logic is intentionally
duplicated in miniature from animated_banner.py, honoring the same
conventions (NO_COLOR, FORCE_COLOR, TERM=dumb, CI, ACRA_NO_ANIMATION).
"""

import os
import queue
import sys
import threading
import time
from typing import Any, Callable, Dict, Optional

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"

_SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

# One accent color and a short label per graph node, purely cosmetic --
# matches the node names in acra.graph.nodes.NODE_REGISTRY.
_AGENT_STYLE = {
    "planner": ("\U0001f4cb", CYAN),
    "researcher": ("\U0001f50d", BLUE),
    "coder": ("\U0001f4bb", MAGENTA),
    "executor": ("\u2699\ufe0f", YELLOW),
    "critic": ("\U0001f9d0", GREEN),
    "memory": ("\U0001f9e0", DIM),
    "human": ("\U0001f64b", BOLD),
}


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


def _message_text(msg: Any) -> str:
    content = getattr(msg, "content", None)
    if content is None and isinstance(msg, dict):
        content = msg.get("content")
    return str(content) if content else ""


def run_workflow_with_thoughts(
    graph: Any,
    state: Dict[str, Any],
    config: Dict[str, Any],
    task_label: str = "Working",
) -> Dict[str, Any]:
    """Stream a compiled LangGraph workflow node by node, printing each
    agent's status message live as it completes (acra's "thought
    process"), with a spinner covering the gap while the next node runs.
    Returns the final accumulated state -- the same shape graph.invoke()
    would return -- fetched from the checkpointer via graph.get_state()
    once the stream finishes.

    Falls back to a plain blocking .invoke() with a single static line
    when stdout isn't a real interactive terminal, so scripted/piped
    invocations and tests behave exactly as they did before this
    function existed.
    """
    if not _animations_enabled():
        print(f"{task_label}...")
        result = graph.invoke(state, config=config)
        return result

    events: "queue.Queue" = queue.Queue()
    _DONE = object()

    def _target():
        try:
            for chunk in graph.stream(state, config=config, stream_mode="updates"):
                events.put(("step", chunk))
            events.put(("done", None))
        except BaseException as exc:  # re-raised on the main thread below
            events.put(("error", exc))

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()

    color = CYAN if _supports_color() else ""
    reset = RESET if _supports_color() else ""
    dim = DIM if _supports_color() else ""
    green = GREEN if _supports_color() else ""
    bold = BOLD if _supports_color() else ""

    start = time.time()
    frame_idx = 0
    error: Optional[BaseException] = None
    step_count = 0

    while True:
        try:
            kind, payload = events.get(timeout=0.08)
        except queue.Empty:
            frame = _SPINNER_FRAMES[frame_idx % len(_SPINNER_FRAMES)]
            elapsed = time.time() - start
            sys.stdout.write(f"\r{color}{frame}{reset} {dim}thinking\u2026 {elapsed:0.1f}s{reset}\033[K")
            sys.stdout.flush()
            frame_idx += 1
            continue

        if kind == "step":
            for node_name, update in payload.items():
                msgs = (update or {}).get("messages", [])
                text = _message_text(msgs[-1]) if msgs else ""
                if not text:
                    continue
                icon, node_color = _AGENT_STYLE.get(node_name, ("\u2022", CYAN))
                node_color = node_color if _supports_color() else ""
                elapsed = time.time() - start
                first_line = text.split("\n", 1)[0]
                sys.stdout.write(
                    f"\r\033[K{node_color}{icon} {bold}{node_name}{reset}{node_color} "
                    f"{dim}[{elapsed:0.1f}s]{reset} {first_line}\n"
                )
                sys.stdout.flush()
                step_count += 1
            continue

        if kind == "error":
            error = payload
            break

        # kind == "done"
        break

    thread.join()
    sys.stdout.write(f"\r\033[K")
    sys.stdout.flush()

    if error is not None:
        raise error

    elapsed = time.time() - start
    sys.stdout.write(f"{green}\u2713{reset} {task_label} complete ({elapsed:.1f}s, {step_count} step"
                      f"{'s' if step_count != 1 else ''}){' ' * 8}\n")
    sys.stdout.flush()

    return graph.get_state(config).values