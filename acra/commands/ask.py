"""Agent task commands for acra."""

import uuid
from typing import Optional

import typer

from acra.graph.workflow import OmniAgentCallbacks, omniagent_graph
from acra.ui.components import render_panel

app = typer.Typer(help="Agent task commands for acra.")


def _run_task(
    task: str,
    task_label: str,
    profile: Optional[str] = None,
    use_memory: bool = True,
    interactive: bool = False,
):
    state = {
        "user_request": task,
        "task_label": task_label,
        "no_memory": not use_memory,
        "profile": profile,
        "interactive": interactive,
    }
    # The compiled graph always carries a checkpointer, which requires a
    # thread_id on every invoke call regardless of whether the caller wants
    # persistence. A fresh id is generated per invocation; when --no-memory
    # is set, nothing is done with it beyond satisfying the checkpointer, so
    # no state is meaningfully persisted or reused across runs.
    thread_id = str(uuid.uuid4())
    config = {
        "callbacks": [OmniAgentCallbacks()],
        "configurable": {"thread_id": thread_id},
    }
    result = omniagent_graph.invoke(state, config=config)
    render_panel(result, title=task_label)
    return result


@app.command()
def ask(
    task: str = typer.Argument(..., help="Task or question for the agent."),
    profile: Optional[str] = typer.Option(None, help="Profile to use."),
    use_memory: bool = typer.Option(True, "--memory/--no-memory", help="Use memory for this task."),
    interactive: bool = typer.Option(False, "--interactive", help="Route agent approval requests to the human node."),
):
    """Ask the assistant a question."""
    return _run_task(task, "ask", profile, use_memory, interactive)


@app.command()
def build(
    task: str = typer.Argument(..., help="Build task for the agent."),
    profile: Optional[str] = typer.Option(None, help="Profile to use."),
    use_memory: bool = typer.Option(True, "--memory/--no-memory", help="Use memory for this task."),
    interactive: bool = typer.Option(False, "--interactive", help="Route agent approval requests to the human node."),
):
    """Run a build workflow for a project task."""
    return _run_task(task, "build", profile, use_memory, interactive)


@app.command()
def fix(
    task: str = typer.Argument(..., help="Code issue or bug for the agent to fix."),
    profile: Optional[str] = typer.Option(None, help="Profile to use."),
    use_memory: bool = typer.Option(True, "--memory/--no-memory", help="Use memory for this task."),
    interactive: bool = typer.Option(False, "--interactive", help="Route agent approval requests to the human node."),
):
    """Run a fix workflow for a code issue."""
    return _run_task(task, "fix", profile, use_memory, interactive)


@app.command()
def review(
    task: str = typer.Argument(..., help="Code, design, or task to review."),
    profile: Optional[str] = typer.Option(None, help="Profile to use."),
    use_memory: bool = typer.Option(True, "--memory/--no-memory", help="Use memory for this task."),
    interactive: bool = typer.Option(False, "--interactive", help="Route agent approval requests to the human node."),
):
    """Review code or design with the critic pipeline."""
    return _run_task(task, "review", profile, use_memory, interactive)


@app.command()
def explain(
    task: str = typer.Argument(..., help="Concept or code path to explain."),
    profile: Optional[str] = typer.Option(None, help="Profile to use."),
    use_memory: bool = typer.Option(True, "--memory/--no-memory", help="Use memory for this task."),
    interactive: bool = typer.Option(False, "--interactive", help="Route agent approval requests to the human node."),
):
    """Explain a technical concept or code path."""
    return _run_task(task, "explain", profile, use_memory, interactive)


@app.command()
def run(
    task: str = typer.Argument(..., help="Task for the agent to execute."),
    profile: Optional[str] = typer.Option(None, help="Profile to use."),
    use_memory: bool = typer.Option(True, "--memory/--no-memory", help="Use memory for this task."),
    interactive: bool = typer.Option(False, "--interactive", help="Route agent approval requests to the human node."),
):
    """Execute a task using the executor agent."""
    return _run_task(task, "run", profile, use_memory, interactive)