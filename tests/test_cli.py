from typer.testing import CliRunner

from acra.cli import app
import acra.commands.serve as serve_module


def test_root_cli_exposes_brain_command():
    runner = CliRunner()

    result = runner.invoke(app, ["brain", "--help"])

    assert result.exit_code == 0
    assert "Brain management commands for acra." in result.output


def test_brain_models_command_renders_without_crashing():
    runner = CliRunner()

    result = runner.invoke(app, ["brain", "models"])

    assert result.exit_code == 0
    assert "Models for all providers" in result.output


def test_serve_command_launches_shell_without_subcommand(monkeypatch):
    runner = CliRunner()
    called = {"value": False}

    def fake_launch_shell(*args, **kwargs):
        called["value"] = True

    monkeypatch.setattr(serve_module, "launch_shell", fake_launch_shell)
    result = runner.invoke(app, ["serve"])

    assert result.exit_code == 0
    assert called["value"] is True
