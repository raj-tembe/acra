"""Interactive shell command for acra."""

import typer
from acra.ui.shell import launch_shell

app = typer.Typer(help="Interactive shell for acra.", invoke_without_command=True)


@app.callback()
def serve(
    ctx: typer.Context,
    party: bool = typer.Option(
        False,
        "--party",
        "--easter-egg",
        help="Show the rainbow party-mode startup banner.",
    ),
):
    """Launch the interactive acra shell."""
    if ctx.invoked_subcommand is None:
        launch_shell(party=party)