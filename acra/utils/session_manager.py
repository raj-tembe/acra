"""Session persistence for acra."""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SESSION_DIR = Path.home() / ".acra" / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)


def _session_path(session_id: str) -> Path:
    return SESSION_DIR / f"{session_id}.json"


def create_session(data: Dict[str, Any], name: Optional[str] = None) -> str:
    session_id = uuid.uuid4().hex[:8]
    now = datetime.utcnow().isoformat() + "Z"
    payload = {
        "id": session_id,
        "name": name or f"session-{session_id}",
        "created_at": now,
        "updated_at": now,
        "data": data,
    }
    with open(_session_path(session_id), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return session_id


def list_sessions() -> List[Dict[str, Any]]:
    sessions = []
    for path in sorted(SESSION_DIR.glob("*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                sessions.append(json.load(f))
        except Exception:
            continue
    return sessions


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    path = _session_path(session_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_session(session_id: str, data: Dict[str, Any]) -> None:
    payload = load_session(session_id)
    if not payload:
        raise FileNotFoundError(f"Session not found: {session_id}")
    payload["data"] = data
    payload["updated_at"] = datetime.utcnow().isoformat() + "Z"
    with open(_session_path(session_id), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
