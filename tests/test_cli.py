from typer.testing import CliRunner

from acra.cli import app
import acra.commands.ask as ask_module
import acra.commands.serve as serve_module


def test_root_cli_exposes_ask_commands():
    runner = CliRunner()

    result = runner.invoke(app, ["build", "--help"])

    assert result.exit_code == 0
    assert "Run a build workflow for a project task." in result.output


def test_root_cli_exposes_brain_command():
    runner = CliRunner()

    result = runner.invoke(app, ["brain", "--help"])

    assert result.exit_code == 0
    assert "Brain management commands for acra." in result.output


def test_root_cli_exposes_context_command():
    runner = CliRunner()

    result = runner.invoke(app, ["context", "--help"])

    assert result.exit_code == 0
    assert "Context management commands for acra." in result.output


def test_root_cli_exposes_logs_command():
    runner = CliRunner()

    result = runner.invoke(app, ["logs", "--help"])

    assert result.exit_code == 0
    assert "Logging commands for acra." in result.output


def test_root_cli_exposes_plugin_command():
    runner = CliRunner()

    result = runner.invoke(app, ["plugin", "--help"])

    assert result.exit_code == 0
    assert "Plugin commands for acra." in result.output


def test_brain_models_command_renders_without_crashing():
    runner = CliRunner()

    result = runner.invoke(app, ["brain", "models"])

    assert result.exit_code == 0
    assert "Models for all providers" in result.output


def test_build_command_sets_interactive_and_memory_flags(monkeypatch):
    runner = CliRunner()
    captured = {}

    class FakeGraph:
        def invoke(self, state, config=None):
            captured["state"] = state
            return {"ok": True}

    monkeypatch.setattr(ask_module, "omniagent_graph", FakeGraph())
    result = runner.invoke(app, ["build", "create a hello world script", "--interactive", "--no-memory"])

    assert result.exit_code == 0
    assert captured["state"]["task_label"] == "build"
    assert captured["state"]["interactive"] is True
    assert captured["state"]["no_memory"] is True


def test_serve_command_launches_shell_without_subcommand(monkeypatch):
    runner = CliRunner()
    called = {"value": False}

    def fake_launch_shell(*args, **kwargs):
        called["value"] = True

    monkeypatch.setattr(serve_module, "launch_shell", fake_launch_shell)
    result = runner.invoke(app, ["serve"])

    assert result.exit_code == 0
    assert called["value"] is True
