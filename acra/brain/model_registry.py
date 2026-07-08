"""Brain model registry utilities for acra."""

from __future__ import annotations

from typing import Dict, List, Optional


class ModelRegistry:
    """Stub model registry for brain provider commands."""

    DEFAULT_MODELS: Dict[str, List[str]] = {
        "gemini": ["gemini-2.5-flash", "gemini-2.5-pro"],
        "openai": ["gpt-4o", "gpt-4.1"],
    }

    def list_models(self, provider: Optional[str] = None) -> List[str]:
        if provider:
            return self.DEFAULT_MODELS.get(provider, [])
        return [model for models in self.DEFAULT_MODELS.values() for model in models]
