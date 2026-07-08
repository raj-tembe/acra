"""Configuration and initialization commands for acra."""

import typer
from typing import Optional

from acra.config.profile_manager import ProfileManager
from acra.ui.components import render_message

app = typer.Typer(help="Configuration commands for acra.")


@app.command("init")
def init(profile: Optional[str] = typer.Option(None, help="Profile name to create")):
    """Run first-time setup and save a config profile."""
    manager = ProfileManager()
    profile_name = manager.run_wizard(profile_name=profile)
    render_message(f"Created profile: {profile_name}")


@app.command("show")
def show(profile: Optional[str] = typer.Option(None, help="Profile name to display")):
    """Show the active profile configuration."""
    manager = ProfileManager()
    config = manager.load_profile(profile)
    render_message(str(config))
