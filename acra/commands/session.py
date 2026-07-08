"""Session commands for acra."""

import typer
from typing import Optional

from acra.ui.components import render_panel

app = typer.Typer(help="Session commands for acra.")


@app.command("list")
def list_sessions():
    """List saved sessions."""
    render_panel("No sessions found.")


@app.command("resume")
def resume_session(session_id: str = typer.Argument(..., help="Session ID to resume.")):
    """Resume a saved session."""
    render_panel(f"Resuming session {session_id}")
