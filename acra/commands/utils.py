"""General utility commands for acra."""

import typer
from acra.ui.components import render_panel

app = typer.Typer(help="Utility commands for acra.")


@app.command()
def workspace():
    """Show the current workspace path and status."""
    render_panel("Workspace utilities are not implemented yet.")
