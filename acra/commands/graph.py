"""Graph utility commands for acra."""

import typer
from acra.ui.components import render_panel

app = typer.Typer(help="Graph commands for acra.")


@app.command("show")
def show_graph():
    """Show the workflow graph structure."""
    render_panel("Graph visualization is not implemented yet.")


@app.command("run")
def run_graph():
    """Run the workflow graph directly."""
    render_panel("Graph run not implemented yet.")
