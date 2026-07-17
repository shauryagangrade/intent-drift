"""Report rendering utilities for creating human-readable output."""

from .models import AlignmentReport


def render_report(report: AlignmentReport) -> str:
    """
    Render an AlignmentReport as a human-readable string.

    Args:
        report: The AlignmentReport to render

    Returns:
        Formatted multi-line string representation
    """
    lines = []

    lines.append("Intent Alignment Report")
    lines.append("=" * 50)
    lines.append("")
    lines.append("Overall Alignment")
    lines.append(f"{report.overall_alignment:.0f}%")
    lines.append("")
    lines.append("Status")
    lines.append(_format_status(report.status))
    lines.append("")
    lines.append("Confidence")
    lines.append(f"{report.confidence:.0f}%")
    lines.append("")
    lines.append("Summary")
    lines.append(report.summary)
    lines.append("")

    # Evidence section
    lines.append("Evidence")
    if report.evidence:
        for evidence in report.evidence:
            marker = _evidence_marker(evidence.value)
            lines.append(f"  {marker} [{evidence.source}] {evidence.details}")
    else:
        lines.append("  No evidence collected.")
    lines.append("")

    # Risk section
    lines.append("Risk")
    lines.append(report.risk)
    lines.append("")

    # Recommendation section
    lines.append("Recommendation")
    lines.append(report.recommendation)
    lines.append("")

    # Breakdown section
    lines.append("Breakdown")
    for name, component in report.breakdown.items():
        score = getattr(component, "score", 0.0)
        lines.append(f"  {name.replace('_', ' ').title()}: {score:.0f}%")
    lines.append("")

    # Timeline section
    if report.timeline:
        lines.append("Timeline")
        for entry in report.timeline:
            lines.append(f"  {entry.get('stage', 'Unknown')}: {entry.get('score', 0):.0f}%")
        lines.append("")

    return "\n".join(lines)


def _format_status(status: str) -> str:
    """Convert status code to human-readable format."""
    return status.replace("_", " ").title()


def _evidence_marker(value: float) -> str:
    """Return a marker symbol based on evidence value."""
    if value >= 0.7:
        return "✓"  # Good alignment
    elif value >= 0.4:
        return "⚠"  # Warning - moderate drift
    else:
        return "✗"  # Critical drift detected
