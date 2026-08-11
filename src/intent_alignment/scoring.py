"""Scoring functions for aggregating evidence into alignment scores."""

from collections import defaultdict

from .evidence import EvidenceProvider
from .models import Evidence, ScoreComponent

__all__ = [
    "compute_weighted_score",
    "aggregate_scores",
]


def compute_weighted_score(
    evidence_list: list[Evidence], providers: list[EvidenceProvider]
) -> tuple[float, dict[str, ScoreComponent]]:
    """
    Compute the overall weighted alignment score from evidence.

    Args:
        evidence_list: List of Evidence objects from all providers
        providers: List of EvidenceProvider instances with weight attributes

    Returns:
        Tuple of (overall_score, component_scores_dict)
    """
    # Group evidence by provider/source
    evidence_by_source = defaultdict(list)
    for evidence in evidence_list:
        evidence_by_source[evidence.source].append(evidence)

    # Build a lookup for provider weights
    provider_weights = {provider.name: provider.weight for provider in providers}
    total_weight = sum(provider_weights.values()) if provider_weights else 1.0

    # Calculate scores for each provider
    component_scores = {}
    weighted_sum = 0.0
    total_weight_used = 0.0

    for source, evidences in evidence_by_source.items():
        if not evidences:
            continue

        # Compute weighted average of evidence values (weighted by confidence)
        total_weighted_value = sum(e.value * e.confidence for e in evidences)
        total_confidence_weight = sum(e.confidence for e in evidences)

        if total_confidence_weight > 0:
            normalized_score = total_weighted_value / total_confidence_weight
        else:
            normalized_score = 0.0

        # Get provider weight
        weight = provider_weights.get(
            source, 1.0 / len(evidence_by_source) if evidence_by_source else 1.0
        )

        # Convert to percentage
        score_percentage = normalized_score * 100

        component_scores[source] = ScoreComponent(
            name=source,
            weight=weight / total_weight if total_weight > 0 else 1.0,
            score=score_percentage,
        )

        # Accumulate for overall score
        weighted_sum += score_percentage * weight
        total_weight_used += weight

    # Compute overall score
    if total_weight_used > 0:
        overall_score = weighted_sum / total_weight_used
    else:
        overall_score = 0.0

    return overall_score, component_scores


def aggregate_scores(evidence_list: list[Evidence]) -> dict[str, ScoreComponent]:
    """
    Legacy function for simple equal-weight aggregation.
    Kept for backward compatibility.
    """
    evidence_by_source = defaultdict(list)
    for evidence in evidence_list:
        evidence_by_source[evidence.source].append(evidence)

    components = {}
    for source, evidences in evidence_by_source.items():
        if not evidences:
            continue

        total_weighted_value = sum(e.value * e.confidence for e in evidences)
        total_confidence_weight = sum(e.confidence for e in evidences)

        if total_confidence_weight > 0:
            normalized_score = total_weighted_value / total_confidence_weight
        else:
            normalized_score = 0.0

        components[source] = ScoreComponent(
            name=source, weight=1.0 / max(1, len(evidence_by_source)), score=normalized_score * 100
        )

    return components
