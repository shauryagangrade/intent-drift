from ...models import Evidence
from ..analysis import (
    _token_matches,
    get_list,
    get_text,
    is_empty,
    salient_tokens,
    term_frequency,
)
from ..base import EvidenceProvider


class RequirementCoverageProvider(EvidenceProvider):
    """Measures coverage of success criteria and required requirements.

    This catches *requirement abandonment*, *success criteria divergence*, and
    *underimplementation*. For each success criterion, we check whether its
    keywords appear in the plan and execution language. A criterion that is
    never mentioned in the work is treated as unmet.
    """

    @property
    def name(self) -> str:
        return "requirement_coverage_provider"

    @property
    def weight(self) -> float:
        # Requirement coverage is a strong, objective drift signal.
        return 0.20

    def collect(self, context: dict) -> list[Evidence]:
        if is_empty(context):
            return [
                Evidence(
                    source=self.name,
                    value=0.0,
                    confidence=0.0,
                    details="No requirements to evaluate coverage against.",
                )
            ]

        criteria = get_list(context, "success_criteria")
        if not criteria:
            return [
                Evidence(
                    source=self.name,
                    value=0.8,
                    confidence=0.4,
                    details="No explicit success criteria declared; assuming partial coverage.",
                )
            ]

        plan = get_text(context, "summary") or get_text(context, "plan")
        reasoning = get_text(context, "reasoning_summary")
        recent = " ".join(str(m) for m in get_list(context, "recent_messages"))
        combined = f"{plan} {reasoning} {recent}"

        # Explicit negation of the objective ("rather than memory",
        # "instead of X") means a mentioned criterion is being REJECTED, not met.
        shift_markers = ["rather than", "instead of", "pivot", "scrap"]

        covered = 0
        for criterion in criteria:
            # Treat the whole criterion as a phrase; fuzzy coverage >= 0.5 means
            # at least half its tokens (e.g. "memory" in "Peak memory < 50MB")
            # appear in the work.
            base = term_frequency(combined, [str(criterion)])

            criterion_topics = salient_tokens(criterion)
            negation = any(
                marker in combined and any(_token_matches(ct, combined) for ct in criterion_topics)
                for marker in shift_markers
            )
            if negation:
                base *= 0.15

            if base >= 0.5:
                covered += 1

        coverage = covered / len(criteria)

        if coverage >= 0.8:
            verdict = "Most success criteria are actively addressed."
        elif coverage >= 0.5:
            verdict = "Some success criteria are not reflected in the work."
        else:
            verdict = "Most success criteria appear abandoned or unaddressed."

        return [
            Evidence(
                source=self.name,
                value=round(coverage, 3),
                confidence=0.85,
                details=f"{verdict} ({covered}/{len(criteria)} criteria covered)",
            )
        ]
