"""Welcome banner and UI panels for acra."""

from rich.panel import Panel
from rich.console import Console

from acra import __version__

WELCOME_TEXT = "acra: agentic CLI for LLM task workflows"


def render_banner(provider: str, model: str, profile: str, workspace: str, theme: dict) -> Panel:
    console = Console()
    lines = [
        f"Provider: {provider} · Model: {model}",
        f"Profile: {profile} · Workspace: {workspace}",
    ]
    content = "\n".join(lines)
    return Panel(content, title="Session", style=theme["border"], border_style=theme["border"])


def render_tips(theme: dict) -> Panel:
    tips = (
        "• Run acra init to set up your workspace\n"
        "• Run acra brain models to list available models\n"
        "• Use / to open commands palette\n"
        "• Use @ to pick files for context"
    )
    return Panel(tips, title="Getting Started", style=theme["border"], border_style=theme["accent"])


# Compatibility alias for older imports and public package API.
welcome_banner = render_banner