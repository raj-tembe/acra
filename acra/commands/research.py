"""Research command module for acra."""

import json
import uuid
import typer
from typing import List, Optional

from acra.graph.workflow import OmniAgentCallbacks, create_workflow
from acra.config.profile_manager import ProfileManager
from acra.utils.output_formatter import format_research_report
from acra.utils.keyring_manager import get_research_key_status
from acra.ui.components import render_panel
from acra.ui.spinner import run_workflow_with_thoughts

app = typer.Typer(help="Research commands for acra.")


def _load_profile(profile: Optional[str]):
    manager = ProfileManager()
    return manager.load_profile(profile)


@app.command()
def research(
    query: str = typer.Argument(..., help="The research topic or question."),
    depth: str = typer.Option("standard", help="Research depth: shallow, standard, deep."),
    sources: str = typer.Option("all", help="Comma-separated sources to use."),
    format: str = typer.Option("citations", help="Output format: citations, summary, detailed."),
    output: Optional[str] = typer.Option(None, help="Write research output to a file."),
    save: bool = typer.Option(False, help="Persist research output into memory."),
    follow_up: bool = typer.Option(False, help="Keep the session open for follow-up questions."),
    use_memory: bool = typer.Option(
        True,
        "--memory/--no-memory",
        help="Use memory persistence for this research.",
    ),
    profile: Optional[str] = typer.Option(None, help="Profile to use."),
    json_output: bool = typer.Option(False, "--json", help="Output JSON instead of rich text."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed debug output."),
):
    """Run a standalone research workflow using the Researcher agent."""
    config = _load_profile(profile)
    source_list = [s.strip() for s in sources.split(",") if s.strip()]
    if not source_list:
        source_list = ["all"]

    # Minimal research subgraph under the researcher agent.
    workflow = create_workflow()
    state = {
        "user_request": query,
        "research_depth": depth,
        "research_sources": source_list,
        "follow_up": follow_up,
        "save_to_memory": save and use_memory,
        "profile": profile,
    }

    thread_id = str(uuid.uuid4())
    result = run_workflow_with_thoughts(
        workflow,
        state,
        config={
            "callbacks": [OmniAgentCallbacks()],
            "configurable": {"thread_id": thread_id},
        },
        task_label="Researching",
    )

    report = format_research_report(result, output_format=format)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            if output.endswith(".json"):
                json.dump(report, f, indent=2)
            else:
                f.write(str(report))

    render_panel(report, title="Research Results")
    if json_output:
        typer.echo(json.dumps(report, indent=2))