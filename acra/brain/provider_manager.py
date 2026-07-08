"""Brain provider management utilities for acra."""

from __future__ import annotations

from typing import Any


class ProviderManager:
    """Stub provider manager for brain commands."""

    def __init__(self) -> None:
        self.providers: dict[str, dict[str, Any]] = {}

    def add_provider(self, name: str, config: dict[str, Any]) -> None:
        self.providers[name] = config

    def get_provider(self, name: str) -> dict[str, Any] | None:
        return self.providers.get(name)

    def list_providers(self) -> list[str]:
        return list(self.providers)
