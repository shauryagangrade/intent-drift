from ...models import Evidence
from ..analysis import (
    _token_matches,
    get_list,
    get_text,
    is_empty,
    salient_tokens,
    term_frequency,
    topic_alignment,
)
from ..base import EvidenceProvider


class ConstraintProvider(EvidenceProvider):
    """Checks whether stated constraints and boundaries are still honored.

    Constraints are hard limits (e.g. "stay under 100MB RAM", "maintain API
    compatibility"). Each constraint is checked as a phrase against the plan and
    execution language (fuzzy + alias match, so "RAM" aligns with "memory").
    A constraint that shares the goal's dominant topic and is on-topic in the
    work is treated as likely honored; an absent or contradicted constraint is a
    violation that lowers alignment.
    """

    @property
    def name(self) -> str:
        return "constraint_provider"

    @property
    def weight(self) -> float:
        # Constraint breaches are high-impact drift signals.
        return 0.25

    def collect(self, context: dict) -> list[Evidence]:
        if is_empty(context):
            return [
                Evidence(
                    source=self.name,
                    value=0.0,
                    confidence=0.0,
                    details="No constraints specified; nothing to verify.",
                )
            ]

        constraints = get_list(context, "constraints")
        if not constraints:
            return [
                Evidence(
                    source=self.name,
                    value=1.0,
                    confidence=0.4,
                    details="No explicit constraints declared; assuming no constraint violations.",
                )
            ]

        goal_text = get_text(context, "text") or get_text(context, "goal")
        plan = get_text(context, "summary") or get_text(context, "plan")
        reasoning = get_text(context, "reasoning_summary")
        recent = " ".join(str(m) for m in get_list(context, "recent_messages"))
        combined = f"{plan} {reasoning} {recent}"

        shift_markers = ["rather than", "instead of", "pivot", "scrap"]

        preserved_scores = []
        for constraint in constraints:
            # Fuzzy phrase coverage of the constraint in the work.
            coverage = term_frequency(combined, [str(constraint)])
            if coverage >= 0.5:
                preserved_scores.append(1.0)
            else:
                # Same-domain fallback: if the constraint is about the goal's
                # dominant topic and that topic is present in the work, assume
                # it is honored rather than violated. But if the objective was
                # explicitly negated ("rather than memory"), the constraint is
                # not being addressed.
                constraint_topics = salient_tokens(constraint)
                constraint_topic = topic_alignment(constraint, goal_text)
                work_topic = topic_alignment(constraint, combined)
                negated = any(
                    marker in combined
                    and any(_token_matches(ct, combined) for ct in constraint_topics)
                    for marker in shift_markers
                )
                if negated:
                    preserved_scores.append(0.2)
                elif constraint_topic >= 0.5 and work_topic >= 0.5:
                    preserved_scores.append(0.8)
                else:
                    preserved_scores.append(0.2)

        preserved = sum(preserved_scores) / len(preserved_scores)

        # Detect explicit contradiction markers in the execution language.
        contradiction_markers = ["break", "violate", "remove", "drop", "relax", "exceed"]
        if any(m in combined for m in contradiction_markers):
            preserved = max(0.0, preserved - 0.2)

        if preserved >= 0.8:
            verdict = "All stated constraints appear maintained."
        elif preserved >= 0.5:
            verdict = "Some constraints not clearly reflected in current work."
        else:
            verdict = "Multiple constraints absent or contradicted in current execution."

        return [
            Evidence(
                source=self.name,
                value=round(preserved, 3),
                confidence=0.85,
                details=f"{verdict} ({len(constraints)} constraints, {preserved:.0%} coverage)",
            )
        ]
