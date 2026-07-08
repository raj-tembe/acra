"""Context management commands for acra."""

import typer
from typing import List

from acra.utils.context_manager import ContextManager
from acra.ui.components import render_panel

app = typer.Typer(help="Context management commands for acra.")


@app.command("add")
def add_context(item: str = typer.Argument(..., help="Context item to add.")):
    """Add a context item."""
    ContextManager().add(item)
    render_panel(f"Added context: {item}")


@app.command("list")
def list_context():
    """List stored context items."""
    items = ContextManager().list()
    render_panel(items, title="Context")


@app.command("clear")
def clear_context():
    """Clear all stored context."""
    ContextManager().clear()
    render_panel("Context cleared.")
