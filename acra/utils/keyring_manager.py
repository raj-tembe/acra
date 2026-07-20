"""Key management for acra.

Secrets are stored using the OS-native credential store via the `keyring`
package (macOS Keychain, Windows Credential Locker, Linux Secret Service /
libsecret) — the same approach used by the AWS CLI, GitHub CLI, and most
other credential-handling CLIs, and why `keyring` is a declared dependency
of this package rather than something users configure separately.

Headless machines (servers, minimal containers, some CI and WSL setups)
often have no OS keyring backend available at all, which makes `keyring`
raise NoKeyringError on every call. Rather than crash `acra keys set` in
that situation, we fall back to a local credentials file under the same
user data directory acra already uses for memory/checkpoints
(USER_DATA_DIR/credentials.json), written with owner-only permissions
(chmod 600) — the same fallback pattern the GitHub CLI and AWS CLI use
when no OS keychain is present. The OS keyring is always tried first and
preferred when it works.
"""

import json
import os
import stat
from pathlib import Path
from typing import Dict, List, Optional

try:
    import keyring
    from keyring.errors import KeyringError
except ImportError:  # pragma: no cover
    keyring = None
    KeyringError = Exception

from acra.config import USER_DATA_DIR

SERVICE_MAIN = "acra"
SERVICE_RESEARCH = "acra-research"
KNOWN_RESEARCH_SOURCES = ["web", "github", "docs", "arxiv"]

# Provider credential names surfaced by `acra keys list`. These match what
# acra/agents/llm.py actually reads (see get_key() calls there), so a key
# you set here is guaranteed to be the one task commands pick up.
KNOWN_PROVIDER_KEYS = [
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "GROQ_API_KEY",
    "HF_API_KEY",
]

_CREDENTIALS_FILE = Path(USER_DATA_DIR) / "credentials.json"


def _service_and_username(name: str) -> "tuple[str, str]":
    """Normalize a key name to (service, username). Names are case-insensitive."""
    if name.startswith("research."):
        return SERVICE_RESEARCH, name.split("research.", 1)[1].lower()
    return SERVICE_MAIN, name.upper()


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
    return os.getenv(name.upper())


# --- local file fallback, used only when the OS keyring has no backend ---

def _load_file_store() -> Dict[str, str]:
    if not _CREDENTIALS_FILE.exists():
        return {}
    try:
        return json.loads(_CREDENTIALS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_file_store(store: Dict[str, str]) -> None:
    _CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CREDENTIALS_FILE.write_text(json.dumps(store, indent=2), encoding="utf-8")
    try:
        os.chmod(_CREDENTIALS_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 0o600, owner read/write only
    except OSError:
        pass  # best effort on platforms without POSIX permissions


def _file_key(service: str, username: str) -> str:
    return f"{service}:{username}"


def _set_password_with_fallback(service: str, username: str, value: str) -> None:
    if keyring is not None:
        try:
            keyring.set_password(service, username, value)
            return
        except KeyringError:
            pass  # no OS backend available on this machine; fall back below
    store = _load_file_store()
    store[_file_key(service, username)] = value
    _save_file_store(store)


def _get_password_with_fallback(service: str, username: str) -> Optional[str]:
    if keyring is not None:
        try:
            value = keyring.get_password(service, username)
            if value:
                return value
        except KeyringError:
            pass
    return _load_file_store().get(_file_key(service, username))


def _delete_password_with_fallback(service: str, username: str) -> None:
    deleted = False
    if keyring is not None:
        try:
            keyring.delete_password(service, username)
            deleted = True
        except KeyringError:
            pass
    store = _load_file_store()
    if _file_key(service, username) in store:
        del store[_file_key(service, username)]
        _save_file_store(store)
        deleted = True
    if not deleted:
        raise KeyError(f"No key found for {username}")


# --- public API (unchanged signatures) ---

def set_key(name: str, value: str) -> None:
    service, username = _service_and_username(name)
    _set_password_with_fallback(service, username, value)


def get_key(name: str) -> Optional[str]:
    service, username = _service_and_username(name)
    value = _get_password_with_fallback(service, username)
    if value:
        return value
    return _env_key(name)


def list_keys() -> List[Dict[str, str]]:
    statuses = []
    names = KNOWN_PROVIDER_KEYS + [f"research.{source}" for source in KNOWN_RESEARCH_SOURCES]
    for name in names:
        value = get_key(name)
        status = "configured" if value else "not set"
        statuses.append({"name": name, "status": status, "value": _mask_value(value)})
    return statuses


def delete_key(name: str) -> None:
    service, username = _service_and_username(name)
    _delete_password_with_fallback(service, username)


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