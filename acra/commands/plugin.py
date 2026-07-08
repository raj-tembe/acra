"""Plugin commands for acra."""

import typer
from acra.ui.components import render_panel

app = typer.Typer(help="Plugin commands for acra.")


@app.command("list")
def list_plugins():
    """List installed plugins."""
    render_panel("No plugins installed.")


@app.command("add")
def add_plugin(name: str = typer.Argument(..., help="Plugin name to add.")):
    """Add a plugin."""
    render_panel(f"Plugin {name} added. (stubbed)")
