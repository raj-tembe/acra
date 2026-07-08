"""acra theme registry."""

from typing import Dict

THEMES: Dict[str, Dict[str, str]] = {
    "dark-orange": {
        "accent": "bright_yellow",
        "border": "dark_orange",
        "text": "white",
        "info": "bright_blue",
    },
    "dark-blue": {
        "accent": "bright_cyan",
        "border": "blue",
        "text": "white",
        "info": "bright_white",
    },
    "dark-green": {
        "accent": "green",
        "border": "bright_green",
        "text": "white",
        "info": "bright_white",
    },
}


def get_theme(name: str) -> Dict[str, str]:
    return THEMES.get(name, THEMES["dark-orange"])
