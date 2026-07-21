"""Shared UI render components for acra."""

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import Any

console = Console()

_MAX_FIELD_LENGTH = 5000


def _stringify(value: Any) -> str:
    if isinstance(value, list) and value and all(isinstance(v, str) for v in value):
        return "\n".join(f"\u2022 {v}" for v in value)
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return "\n".join(f"{k}: {v}" for k, v in value.items())
    return str(value)


def _render_dict(data: dict) -> Group:
    """Render a dict as a lead answer (if present) plus a clean field table,
    instead of a raw Python repr. Built for the summaries produced by
    acra.utils.output_formatter, but degrades gracefully for any dict."""
    renderables = []

    answer = data.get("answer")
    if answer:
        renderables.append(Text(str(answer)))
        renderables.append(Text(""))

    table = Table(show_header=False, box=None, padding=(0, 1, 0, 0))
    table.add_column("Field", style="bold cyan", no_wrap=True)
    table.add_column("Value")
    for key, value in data.items():
        if key == "answer" or value in (None, "", [], {}):
            continue
        value_str = _stringify(value)
        if len(value_str) > _MAX_FIELD_LENGTH:
            value_str = value_str[:_MAX_FIELD_LENGTH] + "\u2026 (truncated)"
        table.add_row(key.replace("_", " ").title(), value_str)

    if table.rows:
        renderables.append(table)

    if not renderables:
        renderables.append(Text("(empty)"))

    return Group(*renderables)


def render_panel(content: Any, title: str = "acra") -> None:
    if isinstance(content, list):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Value")
        for item in content:
            if isinstance(item, dict):
                table.add_row(
                    str(item.get("name", "")),
                    str(item.get("status", "")),
                    str(item.get("value", "")),
                )
            else:
                table.add_row(str(item), "", "")
        console.print(Panel(table, title=title))
    elif isinstance(content, dict):
        console.print(Panel(_render_dict(content), title=title))
    else:
        console.print(Panel(str(content), title=title))


def render_message(message: str) -> None:
    console.print(message)