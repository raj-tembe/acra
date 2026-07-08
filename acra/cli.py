"""acra CLI entrypoint."""

import typer

from acra.commands import (
    serve_app,
    config_app,
    keys_app,
    research_app,
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
app.add_typer(research_app, name="research")
app.add_typer(memory_app, name="memory")
app.add_typer(session_app, name="session")
app.add_typer(graph_app, name="graph")
app.add_typer(utils_app, name="workspace")


def app_main() -> None:
    """Run the acra CLI."""
    app(prog_name="acra")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    profile: str = typer.Option(None, "--profile", help="Profile to use."),
    workspace: str = typer.Option(None, "--workspace", help="Override workspace path."),
    no_memory: bool = typer.Option(False, "--no-memory", help="Run without memory."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Display planned actions without executing."),
    json_output: bool = typer.Option(False, "--json", help="Output JSON-formatted results."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output."),
    timeout: int = typer.Option(0, "--timeout", help="Override execution timeout in seconds."),
):
    """acra: Agentic CLI for LLM powered task execution and research workflows."""
    if ctx.invoked_subcommand is None:
        launch_shell(profile=profile, workspace=workspace)


if __name__ == "__main__":
    app_main()
