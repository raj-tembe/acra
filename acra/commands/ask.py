"""Agent task commands for acra."""

import uuid
from typing import Optional

from acra.graph.workflow import OmniAgentCallbacks, omniagent_graph
from acra.ui.components import render_panel


def _run_task(task: str, task_label: str, profile: Optional[str] = None, no_memory: bool = False):
    state = {
        "user_request": task,
        "task_label": task_label,
        "no_memory": no_memory,
        "profile": profile,
    }
    result = omniagent_graph.invoke(state, config={"callbacks": [OmniAgentCallbacks()]})
    render_panel(result, title=task_label)
    return result


def ask(task: str, profile: Optional[str] = None, no_memory: bool = False):
    """Ask the assistant a question."""
    return _run_task(task, "ask", profile, no_memory)


def build(task: str, profile: Optional[str] = None, no_memory: bool = False):
    """Run a build workflow for a project task."""
    return _run_task(task, "build", profile, no_memory)


def fix(task: str, profile: Optional[str] = None, no_memory: bool = False):
    """Run a fix workflow for a code issue."""
    return _run_task(task, "fix", profile, no_memory)


def review(task: str, profile: Optional[str] = None, no_memory: bool = False):
    """Review code or design with the critic pipeline."""
    return _run_task(task, "review", profile, no_memory)


def explain(task: str, profile: Optional[str] = None, no_memory: bool = False):
    """Explain a technical concept or code path."""
    return _run_task(task, "explain", profile, no_memory)


def run(task: str, profile: Optional[str] = None, no_memory: bool = False):
    """Execute a task using the executor agent."""
    return _run_task(task, "run", profile, no_memory)
