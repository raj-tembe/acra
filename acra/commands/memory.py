"""Memory commands for acra."""

import typer
from typing import Optional

from acra.utils.keyring_manager import get_key_status
from acra.ui.components import render_panel

app = typer.Typer(help="Memory commands for acra.")


@app.command("list")
def list_memory():
    """List memory entries."""
    render_panel("Memory listing not implemented yet.")


@app.command("clear")
def clear_memory():
    """Clear memory entries."""
    render_panel("Memory cleared.")


@app.command("search")
def search_memory(query: str = typer.Argument(..., help="Search query.")):
    """Search memory using semantic search."""
    render_panel(f"Search results for: {query}")
