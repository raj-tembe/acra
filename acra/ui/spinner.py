"""Live 'running' spinner for long agent tasks.

`acra ask/build/fix/review/explain/run` can take anywhere from a few
seconds to a couple of minutes (planner -> researcher -> coder -> executor
-> critic, each an LLM call), and until now the terminal went completely
silent between hitting enter and the result panel appearing. This wraps a
blocking call with the same braille spinner used in the animated startup
banner (acra/ui/animated_banner.py), showing live progress and elapsed
time instead.

run_workflow_with_thoughts goes further: it streams the graph with
LangGraph's stream_mode="messages", which yields raw LLM token/tool-call
deltas *as the model generates them* -- real live "thinking" -- tagged
with which node emitted them (metadata["langgraph_node"]), via
LangChain's callback system. This works even though every node in this
codebase calls its chain with a plain synchronous .invoke(): LangGraph
intercepts the underlying chat model's token callbacks regardless of
whether the node code itself calls .stream(). Every agent chain in this
codebase (planner, researcher, coder, critic) is a with_structured_output
chain, so what streams is mostly incremental JSON (the fields of that
node's Pydantic schema being filled in), not prose -- still genuinely
live model output, just JSON-shaped; each node's raw stream is capped at
_MAX_LIVE_CHARS so a coder/critic response containing full generated
file contents doesn't flood the terminal. Once a node finishes, its
actual polished status message (the same "Planner Agent: ...", "Research
Agent: ..." text used in the final activity log; see
acra.utils.output_formatter) replaces the raw stream with one clean,
permanent line -- LangGraph also emits this as a plain (non-chunk)
AIMessage on the same "messages" stream, so no separate pass is needed
to fetch it.

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

from langchain_core.messages import AIMessageChunk

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

# Live raw token/tool-call text shown per node before it's cut off with an
# ellipsis. Structured-output chains (every agent in this codebase) stream
# JSON, and the coder/critic schemas can carry full generated file
# contents -- uncapped, that would flood the terminal rather than read as
# "thinking".
_MAX_LIVE_CHARS = 320

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


def _chunk_delta_text(chunk: Any) -> str:
    """Extract whatever new text a streamed AIMessageChunk carries: plain
    content if the model streamed prose, otherwise the incremental
    tool-call-argument JSON fragments structured-output chains stream
    instead (every chain in this codebase)."""
    content = getattr(chunk, "content", None)
    if isinstance(content, str) and content:
        return content
    if isinstance(content, list):  # some providers chunk content as parts
        text = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)
        if text:
            return text
    tool_chunks = getattr(chunk, "tool_call_chunks", None) or []
    return "".join(tc.get("args") or "" for tc in tool_chunks)


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
    """Stream a compiled LangGraph workflow's real token-level output live
    (acra's "thought process": what each agent is actually generating, as
    it generates it) via stream_mode="messages", resolving into a clean
    permanent status line once each node finishes. Returns the final
    accumulated state -- the same shape graph.invoke() would return --
    fetched from the checkpointer via graph.get_state() once the stream
    finishes.

    Falls back to a plain blocking .invoke() with a single static line
    when stdout isn't a real interactive terminal, so scripted/piped
    invocations and tests behave exactly as they did before this
    function existed.
    """
    if not _animations_enabled():
        print(f"{task_label}...")
        return graph.invoke(state, config=config)

    events: "queue.Queue" = queue.Queue()

    def _target():
        try:
            for chunk, metadata in graph.stream(state, config=config, stream_mode="messages"):
                events.put(("token", (chunk, metadata)))
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
    active_node: Optional[str] = None  # node currently mid-stream on the live line, if any
    active_chars = 0
    active_capped = False

    def _clear_line():
        sys.stdout.write("\r\033[K")

    while True:
        try:
            kind, payload = events.get(timeout=0.08)
        except queue.Empty:
            if active_node is None:
                frame = _SPINNER_FRAMES[frame_idx % len(_SPINNER_FRAMES)]
                elapsed = time.time() - start
                sys.stdout.write(f"\r{color}{frame}{reset} {dim}thinking\u2026 {elapsed:0.1f}s{reset}\033[K")
                sys.stdout.flush()
                frame_idx += 1
            continue

        if kind == "error":
            error = payload
            break
        if kind == "done":
            break

        # kind == "token"
        chunk, metadata = payload
        node_name = metadata.get("langgraph_node") if metadata else None

        if isinstance(chunk, AIMessageChunk):
            delta = _chunk_delta_text(chunk)
            if not delta:
                continue
            if active_node != node_name:
                # A new node started producing output. The live snippet below
                # may wrap across several terminal rows, which can't be
                # reliably cleared/overwritten without tracking terminal
                # width, so this is a plain scrolling transcript (like a
                # real streaming chat log) rather than an in-place redraw:
                # each node's snippet is written once, ending in a newline,
                # and stays in scrollback.
                if active_node is not None:
                    sys.stdout.write("\n")
                else:
                    _clear_line()  # clear the waiting spinner line first
                icon, node_color = _AGENT_STYLE.get(node_name, ("\u2022", CYAN))
                node_color = node_color if _supports_color() else ""
                sys.stdout.write(f"{node_color}{icon} {bold}{node_name}{reset}{dim} \u203a {reset}")
                active_node = node_name
                active_chars = 0
                active_capped = False
            if not active_capped:
                remaining = _MAX_LIVE_CHARS - active_chars
                if remaining <= 0:
                    active_capped = True
                    sys.stdout.write(f"{dim}\u2026{reset}")
                else:
                    shown = delta[:remaining]
                    sys.stdout.write(f"{dim}{shown}{reset}")
                    active_chars += len(shown)
                    if active_chars >= _MAX_LIVE_CHARS:
                        active_capped = True
                        sys.stdout.write(f"{dim}\u2026{reset}")
                sys.stdout.flush()
            continue

        # A plain (non-chunk) AIMessage: the node's finished, polished status
        # message -- close off the live snippet line (if any) and print one
        # clean, permanent status line.
        text = _message_text(chunk)
        if not text:
            continue
        icon, node_color = _AGENT_STYLE.get(node_name, ("\u2022", CYAN))
        node_color = node_color if _supports_color() else ""
        elapsed = time.time() - start
        first_line = text.split("\n", 1)[0]
        if active_node is not None:
            sys.stdout.write("\n")
        else:
            _clear_line()  # nothing streamed for this node; clear the waiting spinner line
        sys.stdout.write(
            f"{node_color}{icon} {bold}{node_name}{reset}{node_color} "
            f"{dim}[{elapsed:0.1f}s]{reset} {first_line}\n"
        )
        sys.stdout.flush()
        active_node = None
        step_count += 1

    thread.join()
    _clear_line()
    sys.stdout.flush()

    if error is not None:
        raise error

    elapsed = time.time() - start
    sys.stdout.write(f"{green}\u2713{reset} {task_label} complete ({elapsed:.1f}s, {step_count} step"
                      f"{'s' if step_count != 1 else ''}){' ' * 8}\n")
    sys.stdout.flush()

    return graph.get_state(config).values