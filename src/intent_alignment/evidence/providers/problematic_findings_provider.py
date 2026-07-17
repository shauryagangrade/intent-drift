from ...models import Evidence
from ..analysis import (
    get_text,
    is_empty,
    parse_git_diff,
)
from ..base import EvidenceProvider


class ProblematicFindingsProvider(EvidenceProvider):
    """Surfaces risk patterns: hidden rewrites, complexity, and rework loops.

    This provider scans the execution narrative and diff for language and shapes
    that indicate trouble: full rewrites, repeated rework, massive deletions, or
    contradictory direction. It acts as a catch-all risk detector that lowers
    alignment when such patterns appear, even if other providers look healthy.
    """

    @property
    def name(self) -> str:
        return "problematic_findings_provider"

    @property
    def weight(self) -> float:
        # Early risk detection helps intervention before drift compounds.
        return 0.15

    def collect(self, context: dict) -> list[Evidence]:
        if is_empty(context):
            return [
                Evidence(
                    source=self.name,
                    value=0.0,
                    confidence=0.0,
                    details="No information available to assess risk patterns.",
                )
            ]

        reasoning = get_text(context, "reasoning_summary")
        messages = " ".join(
            str(m) for m in context.get("execution_context", {}).get("recent_messages", [])
        )
        exec_text = f"{reasoning} {messages}".lower()

        risk_markers = {
            "rewrite": "full rewrite detected",
            "rework": "rework loop detected",
            "redesign": "redesign in progress",
            "scrap": "scrapping prior work",
            "start over": "restarting from scratch",
            "complicated": "rising complexity",
            "overcomplicated": "overcomplicated solution",
            "boilerplate": "excess boilerplate introduced",
        }
        detected = [label for marker, label in risk_markers.items() if marker in exec_text]

        diff = parse_git_diff(context.get("execution_context", {}).get("git_diff"))
        # Massive deletion is itself a risk signal (throwing work away).
        if diff["removed"] > 100:
            detected.append("large deletion of existing code")

        penalty = min(1.0, 0.25 * len(detected))
        value = max(0.0, 1.0 - penalty)

        if not detected:
            verdict = "No problematic patterns detected in execution."
        elif value >= 0.6:
            verdict = f"Minor risk patterns: {', '.join(detected)}."
        else:
            verdict = f"Multiple risk patterns: {', '.join(detected)}."

        return [
            Evidence(
                source=self.name,
                value=round(value, 3),
                confidence=0.8 if exec_text.strip() or diff["total"] else 0.5,
                details=verdict,
            )
        ]
