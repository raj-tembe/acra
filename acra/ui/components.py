"""Shared UI render components for acra."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Any

console = Console()


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
    else:
        console.print(Panel(str(content), title=title))


def render_message(message: str) -> None:
    console.print(message)
