"""Profile management for acra."""

import json
import os
from getpass import getpass
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_DIR = Path.home() / ".acra"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_PROFILE_NAME = "default"

# Maps provider names to the credential name acra/agents/llm.py actually
# reads via keyring_manager.get_key(). Ollama is local and needs no key.
_PROVIDER_KEY_NAMES = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "groq": "GROQ_API_KEY",
    "huggingface_cloud": "HF_API_KEY",
    "huggingface_local": "HF_API_KEY",
}


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _safe_load_config() -> Dict[str, Any]:
    _ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {"profiles": {DEFAULT_PROFILE_NAME: {}}, "active": DEFAULT_PROFILE_NAME}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"profiles": {DEFAULT_PROFILE_NAME: {}}, "active": DEFAULT_PROFILE_NAME}


def _save_config(data: Dict[str, Any]) -> None:
    _ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class ProfileManager:
    """Manage named acra configuration profiles."""

    def __init__(self) -> None:
        self._data = _safe_load_config()

    def list_profiles(self) -> Dict[str, Any]:
        return self._data.get("profiles", {})

    def load_profile(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        if profile_name is None:
            profile_name = self._data.get("active", DEFAULT_PROFILE_NAME)
        profiles = self._data.get("profiles", {})
        return profiles.get(profile_name, profiles.get(DEFAULT_PROFILE_NAME, {}))

    def save_profile(self, profile_name: str, profile_data: Dict[str, Any]) -> None:
        profiles = self._data.setdefault("profiles", {})
        profiles[profile_name] = profile_data
        self._data["active"] = profile_name
        _save_config(self._data)

    def set_active(self, profile_name: str) -> None:
        profiles = self._data.setdefault("profiles", {})
        if profile_name in profiles:
            self._data["active"] = profile_name
            _save_config(self._data)
        else:
            raise ValueError(f"Profile not found: {profile_name}")

    def run_wizard(self, profile_name: Optional[str] = None) -> str:
        profile_name = profile_name or DEFAULT_PROFILE_NAME
        print("Welcome to acra setup wizard")
        provider = input("Choose provider (gemini/openai/groq/ollama/huggingface_cloud/huggingface_local): ").strip() or "gemini"
        model = input("Model name: ").strip() or "gemini-2.5-flash"
        api_key = getpass("Provider API key (hidden): ")
        theme = input("Theme (dark-orange/dark-blue/dark-green): ").strip() or "dark-orange"
        workspace = input("Workspace path (default=current directory): ").strip() or os.getcwd()
        print("Configure research keys. Press enter to skip a source.")
        research_key_values = {}
        for source in ["web", "github", "docs", "arxiv"]:
            prompt = f"Research {source} API key (if required): "
            value = getpass(prompt) if source != "arxiv" else input(prompt).strip()
            if value:
                research_key_values[source] = value

        # Secrets are stored via the OS keyring (falling back to a
        # permission-locked local file when no OS backend is available),
        # never written into the plaintext profile JSON. See
        # acra/utils/keyring_manager.py.
        from acra.utils.keyring_manager import set_key

        provider_key_name = _PROVIDER_KEY_NAMES.get(provider)
        if api_key and provider_key_name:
            set_key(provider_key_name, api_key)
        for source, value in research_key_values.items():
            set_key(f"research.{source}", value)

        profile = {
            "provider": provider,
            "model": model,
            "theme": theme,
            "workspace": workspace,
        }
        self.save_profile(profile_name, profile)
        return profile_name