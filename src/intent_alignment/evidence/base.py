from abc import ABC, abstractmethod
from typing import Any

from ..models import Evidence

__all__ = [
    "EvidenceProvider",
]


class EvidenceProvider(ABC):
    """Abstract base class for all evidence providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this provider."""
        pass

    @property
    @abstractmethod
    def weight(self) -> float:
        """Relative weight of this provider's evidence (will be normalized)."""
        pass

    @abstractmethod
    def collect(self, context: dict[str, Any]) -> list[Evidence]:
        """
        Collect evidence from the given context.

        Args:
            context: The alignment context containing original_goal, current_plan,
                    and execution_context

        Returns:
            List of Evidence objects representing findings
        """
        pass
