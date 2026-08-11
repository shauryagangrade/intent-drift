from dataclasses import dataclass
from typing import Any

__all__ = [
    "AlignmentContext",
    "AlignmentReport",
    "Evidence",
    "ScoreComponent",
]


@dataclass
class AlignmentContext:
    original_goal: dict[str, Any]
    current_plan: dict[str, Any]
    execution_context: dict[str, Any]


@dataclass
class Evidence:
    source: str  # Which provider this evidence comes from
    value: float  # 0-1 scale of significance
    confidence: float  # 0-1 scale of confidence in this evidence
    details: str  # Human-readable explanation of evidence


@dataclass
class ScoreComponent:
    name: str
    weight: float  # Relative importance (sum to 1.0)
    score: float  # 0-1 scale


@dataclass
class AlignmentReport:
    overall_alignment: float
    confidence: float
    status: str  # 'Fully_Aligned', 'Minor_Drift', etc.
    breakdown: dict[str, "ScoreComponent"]
    summary: str
    evidence: list[Evidence]
    risk: str
    recommendation: str
    timeline: list[dict]
