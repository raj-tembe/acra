"""Logging commands for acra."""

import typer

from acra.ui.components import render_panel

app = typer.Typer(help="Logging commands for acra.")


@app.command("show")
def show_logs(limit: int = typer.Option(10, help="Number of log entries to show.")):
    """Show recent log entries."""
    render_panel([{"timestamp": "2024-01-01T00:00:00Z", "message": "Placeholder log entry."}], title=f"Last {limit} logs")
