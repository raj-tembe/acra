"""acra CLI entrypoint."""

import typer

import acra
from acra.commands.ask import ask, build, explain, fix, review, run
from acra.commands.research import research
from acra.commands import (
    serve_app,
    config_app,
    keys_app,
    brain_app,
    context_app,
    logs_app,
    plugin_app,
    memory_app,
    session_app,
    graph_app,
    utils_app,
)
from acra.ui.shell import launch_shell

app = typer.Typer(add_completion=True)

app.add_typer(serve_app, name="serve")
app.add_typer(config_app, name="config")
app.add_typer(keys_app, name="keys")
app.add_typer(memory_app, name="memory")
app.add_typer(session_app, name="session")
app.add_typer(graph_app, name="graph")
app.add_typer(utils_app, name="workspace")
app.add_typer(brain_app, name="brain", help="Brain management commands for acra.")
app.add_typer(context_app, name="context", help="Context management commands for acra.")
app.add_typer(logs_app, name="logs", help="Logging commands for acra.")
app.add_typer(plugin_app, name="plugin", help="Plugin commands for acra.")

app.command("ask")(ask)
app.command("build")(build)
app.command("fix")(fix)
app.command("review")(review)
app.command("explain")(explain)
app.command("run")(run)
app.command("research")(research)


def _version_callback(value: bool):
    if value:
        typer.echo(acra.__version__)
        raise typer.Exit()


def app_main() -> None:
    """Run the acra CLI."""
    app(prog_name="acra")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the installed acra version and exit.",
    ),
    profile: str = typer.Option(None, "--profile", help="Profile to use."),
    workspace: str = typer.Option(None, "--workspace", help="Override workspace path."),
    use_memory: bool = typer.Option(True, "--memory/--no-memory", help="Use memory."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Display planned actions without executing."),
    json_output: bool = typer.Option(False, "--json", help="Output JSON-formatted results."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output."),
    timeout: int = typer.Option(0, "--timeout", help="Override execution timeout in seconds."),
    party: bool = typer.Option(
        False,
        "--party",
        "--easter-egg",
        help="Show the rainbow party-mode startup banner.",
    ),
):
    """acra: Agentic CLI for LLM powered task execution and research workflows."""
    if ctx.invoked_subcommand is None:
        launch_shell(profile=profile, workspace=workspace, party=party)


if __name__ == "__main__":
    app_main()