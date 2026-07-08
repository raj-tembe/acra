"""Context management utilities for acra."""

from __future__ import annotations

from typing import List


class ContextManager:
    """Simple context storage for acra CLI commands."""

    _context_items: List[str] = []

    def add(self, item: str) -> None:
        self._context_items.append(item)

    def list(self) -> List[str]:
        return list(self._context_items)

    def clear(self) -> None:
        self._context_items.clear()
