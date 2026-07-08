"""Key management using OS keyring for acra."""

import os
from typing import Dict, List, Optional

try:
    import keyring
except ImportError:  # pragma: no cover
    keyring = None

SERVICE_MAIN = "acra"
SERVICE_RESEARCH = "acra-research"
KNOWN_RESEARCH_SOURCES = ["web", "github", "docs", "arxiv"]


def _service_and_username(name: str) -> (str, str):
    if name.startswith("research."):
        return SERVICE_RESEARCH, name.split("research.", 1)[1]
    return SERVICE_MAIN, name


def _mask_value(value: Optional[str]) -> str:
    if not value:
        return "not set"
    if len(value) <= 10:
        return value
    return f"{value[:6]}...{value[-4:]}"


def _env_key(name: str) -> Optional[str]:
    if name.startswith("research."):
        source = name.split("research.", 1)[1].upper()
        return os.getenv(f"ACRA_RESEARCH_{source}_KEY")
    if name == "provider":
        return os.getenv("ACRA_PROVIDER_KEY")
    return os.getenv(name.upper())


def set_key(name: str, value: str) -> None:
    if keyring is None:
        raise RuntimeError("keyring is required for storing secrets")
    service, username = _service_and_username(name)
    keyring.set_password(service, username, value)


def get_key(name: str) -> Optional[str]:
    if keyring is not None:
        service, username = _service_and_username(name)
        value = keyring.get_password(service, username)
        if value:
            return value
    return _env_key(name)


def list_keys() -> List[Dict[str, str]]:
    statuses = []
    names = ["provider"] + [f"research.{source}" for source in KNOWN_RESEARCH_SOURCES]
    for name in names:
        value = get_key(name)
        status = "configured" if value else "not set"
        statuses.append({"name": name, "status": status, "value": _mask_value(value)})
    return statuses


def delete_key(name: str) -> None:
    if keyring is None:
        raise RuntimeError("keyring is required for deleting secrets")
    service, username = _service_and_username(name)
    keyring.delete_password(service, username)


def get_key_status(name: str) -> Dict[str, str]:
    value = get_key(name)
    return {
        "name": name,
        "configured": bool(value),
        "masked": _mask_value(value),
    }


def get_research_key_status(name: str) -> Dict[str, str]:
    """Alias for research-specific key status lookup."""
    return get_key_status(name)
