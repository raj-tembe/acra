"""Key management commands for acra."""

import typer
from typing import Optional

from acra.utils.keyring_manager import (
    set_key,
    get_key_status,
    delete_key,
    list_keys,
)
from acra.ui.components import render_panel

app = typer.Typer(help="Key management commands for acra.")


@app.command("set")
def set_key_cmd(
    name: str = typer.Argument(
        ...,
        help="Key name: GEMINI_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, HF_API_KEY, "
        "or research.<source> (web, github, docs, arxiv).",
    ),
    value: Optional[str] = typer.Argument(None, help="API key value. If omitted, you will be prompted."),
):
    """Set a provider or research API key."""
    if value is None:
        value = typer.prompt("Enter API key", hide_input=True)
    set_key(name, value)
    render_panel(f"Key set: {name}")


@app.command("list")
def list_key_cmd():
    """List configured API keys."""
    rows = list_keys()
    render_panel(rows, title="Configured Keys")


@app.command("delete")
def delete_key_cmd(name: str = typer.Argument(..., help="Key name to delete.")):
    """Delete a configured API key."""
    delete_key(name)
    render_panel(f"Deleted key: {name}")