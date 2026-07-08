"""Brain management commands for acra."""

import typer
from typing import Optional

from acra.brain.provider_manager import ProviderManager
from acra.brain.model_registry import ModelRegistry
from acra.config.profile_manager import ProfileManager
from acra.ui.components import render_panel

app = typer.Typer(help="Brain management commands for acra.")


@app.command("add")
def add_brain(name: str = typer.Argument(..., help="Brain name to add."), provider: str = typer.Option(..., help="LLM provider to associate.")):
    """Add a new brain profile."""
    manager = ProfileManager()
    profile = manager.load_profile()
    profile.setdefault("brains", {})[name] = {"provider": provider}
    manager.save_profile(profile_name=profile.get("name", "default"), profile_data=profile)
    render_panel(f"Added brain '{name}' using provider {provider}.")


@app.command("use")
def use_brain(name: str = typer.Argument(..., help="Brain name to activate.")):
    """Switch to a saved brain."""
    profile = ProfileManager().load_profile()
    if name not in profile.get("brains", {}):
        raise typer.BadParameter(f"Brain not found: {name}")
    profile["active_brain"] = name
    ProfileManager().save_profile(profile_name=profile.get("name", "default"), profile_data=profile)
    render_panel(f"Using brain '{name}'.")


@app.command("list")
def list_brains():
    """List configured brains."""
    profile = ProfileManager().load_profile()
    brains = profile.get("brains", {})
    if not brains:
        render_panel("No brains configured.")
        return
    rows = [{"name": name, "status": "active" if name == profile.get("active_brain") else "inactive", "value": brain["provider"]} for name, brain in brains.items()]
    render_panel(rows, title="Brains")


@app.command("test")
def test_brain(name: str = typer.Argument(..., help="Brain name to test.")):
    """Test a brain configuration."""
    render_panel(f"Tested brain '{name}'. (stubbed)")


@app.command("models")
def list_models(provider: Optional[str] = typer.Option(None, help="Provider to list models for.")):
    """List available models for a provider."""
    registry = ModelRegistry()
    choices = registry.list_models(provider)
    render_panel(choices, title=f"Models for {provider or 'all providers'}")
