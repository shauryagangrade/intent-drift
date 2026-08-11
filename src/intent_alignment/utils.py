"""Utility functions for generating report components."""

from .models import Evidence, ScoreComponent

__all__ = [
    "compute_confidence",
    "determine_status",
    "generate_summary",
    "generate_risk_assessment",
    "generate_recommendation",
]


def compute_confidence(evidence_list: list[Evidence]) -> float:
    """
    Compute overall confidence based on evidence consistency and confidence scores.

    Factors:
    - Average confidence of evidence items
    - Consistency of evidence (low variance increases confidence)
    - Coverage (more evidence sources increases confidence)

    Returns:
        Confidence percentage (0-100)
    """
    if not evidence_list:
        return 0.0

    # Factor 1: Average evidence confidence
    avg_confidence = sum(e.confidence for e in evidence_list) / len(evidence_list)

    # Factor 2: Evidence consistency (inverse of variance in values)
    values = [e.value for e in evidence_list]
    if len(values) > 1:
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        consistency = max(0.0, 1.0 - (variance * 2))  # Scale variance to 0-1
    else:
        consistency = 1.0

    # Factor 3: Source diversity
    unique_sources = len({e.source for e in evidence_list})
    diversity_factor = min(1.0, unique_sources / 9.0)  # Max 9 providers

    # Combine factors
    combined = (avg_confidence * 0.5) + (consistency * 0.3) + (diversity_factor * 0.2)

    return round(combined * 100, 1)


def determine_status(alignment_score: float) -> str:
    """
    Determine the alignment status based on the overall score.

    Returns:
        Status string: 'Fully_Aligned', 'Minor_Drift', 'Moderate_Drift',
                       'Major_Drift', or 'Critical_Drift'
    """
    if alignment_score >= 90:
        return "Fully_Aligned"
    elif alignment_score >= 75:
        return "Minor_Drift"
    elif alignment_score >= 50:
        return "Moderate_Drift"
    elif alignment_score >= 25:
        return "Major_Drift"
    else:
        return "Critical_Drift"


def generate_summary(component_scores: dict[str, ScoreComponent], overall_score: float) -> str:
    """
    Generate a human-readable summary of the alignment assessment.

    Args:
        component_scores: Dictionary of component scores
        overall_score: Overall alignment percentage

    Returns:
        Summary text
    """
    if not component_scores:
        return "No evidence collected for alignment assessment."

    # Find top and bottom performing components
    sorted_components = sorted(component_scores.items(), key=lambda x: x[1].score, reverse=True)

    top_component = sorted_components[0]
    bottom_component = sorted_components[-1] if len(sorted_components) > 1 else None

    if overall_score >= 90:
        summary = "Current work remains strongly aligned with the original goal."
    elif overall_score >= 75:
        summary = "Current work shows minor drift from the original goal."
    elif overall_score >= 50:
        summary = "Current work shows moderate drift from the original goal."
    elif overall_score >= 25:
        summary = "Current work shows major drift from the original goal."
    else:
        summary = "Current work has critically diverged from the original goal."

    # Add detail about strongest and weakest areas
    if bottom_component and top_component[1].score > bottom_component[1].score + 20:
        summary += f" Strongest alignment in {top_component[0].replace('_', ' ')} ({top_component[1].score:.0f}%); "
        summary += f"weakest in {bottom_component[0].replace('_', ' ')} ({bottom_component[1].score:.0f}%)."
    elif bottom_component:
        summary += " All areas show relatively consistent alignment levels."

    return summary


def generate_risk_assessment(
    evidence_list: list[Evidence], component_scores: dict[str, ScoreComponent]
) -> str:
    """
    Generate a risk assessment based on evidence and component scores.

    Returns:
        Risk description text
    """
    if not component_scores:
        return "Insufficient evidence to assess risk."

    low_scores = [(name, comp.score) for name, comp in component_scores.items() if comp.score < 60]

    if not low_scores:
        return "Low risk: All alignment dimensions show good compliance."

    if len(low_scores) == 1:
        name, score = low_scores[0]
        return (
            f"Moderate risk: {name.replace('_', ' ')} shows concerning divergence ({score:.0f}%)."
        )

    names = [name.replace("_", " ") for name, _ in low_scores]
    return f"High risk: Multiple areas show significant drift ({', '.join(names)})."


def generate_recommendation(
    component_scores: dict[str, ScoreComponent], overall_score: float
) -> str:
    """
    Generate a recommendation based on the alignment assessment.

    Returns:
        Recommendation text
    """
    if overall_score >= 90:
        return "Continue current approach. Alignment is strong across all dimensions."
    elif overall_score >= 75:
        return "Continue with minor monitoring. Review the lowest-scoring dimension for early drift indicators."
    elif overall_score >= 50:
        return "Pause and reassess. Significant drift detected; consider realigning current work with original objectives."
    elif overall_score >= 25:
        return "Strongly recommend reassessment. Major realignment needed before continuing."
    else:
        return "Immediate intervention required. Current direction has critically diverged from original intent."
