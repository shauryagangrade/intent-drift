from ...models import Evidence
from ..analysis import (
    get_list,
    get_text,
    is_empty,
    parse_git_diff,
)
from ..base import EvidenceProvider


class ScopeProvider(EvidenceProvider):
    """Detects scope creep, feature creep, and overengineering.

    Scope discipline is judged by: (a) how many new "features"/"add"/"support"
    markers appear in the execution language relative to the goal, (b) the size
    and breadth of the git diff (many files + net additions suggest expansion),
    and (c) whether the plan steps stay within the original objective's
    vocabulary. A large, additive, multi-file change with no corresponding goal
    language is strong evidence of drift.
    """

    @property
    def name(self) -> str:
        return "scope_provider"

    @property
    def weight(self) -> float:
        # Scope discipline is critical for detecting drift early.
        return 0.20

    def collect(self, context: dict) -> list[Evidence]:
        if is_empty(context):
            return [
                Evidence(
                    source=self.name,
                    value=0.0,
                    confidence=0.0,
                    details="No scope information available to evaluate.",
                )
            ]

        goal_text = get_text(context, "text") or get_text(context, "goal")
        plan_summary = get_text(context, "summary") or get_text(context, "plan")
        reasoning = get_text(context, "reasoning_summary")
        recent = " ".join(str(m) for m in get_list(context, "recent_messages"))
        exec_text = f"{plan_summary} {reasoning} {recent}"

        # Expansion signals in execution language (genuine scope-creep phrasing;
        # routine refactoring/optimization is NOT treated as creep).
        expansion_markers = [
            "new feature",
            "add feature",
            "additional feature",
            "extra feature",
            "also support",
            "scope expansion",
            "new module",
            "extra capability",
            "gold plate",
            "nice to have",
        ]
        expansion_hits = sum(1 for m in expansion_markers if m in exec_text)
        goal_terms = set(goal_text.split())
        exec_terms = set(exec_text.split())
        # How much of the execution vocabulary is NOT in the goal vocabulary.
        novelty_ratio = (
            len(exec_terms - goal_terms) / max(1, len(exec_terms)) if exec_terms else 0.0
        )

        # Git diff breadth.
        diff = parse_git_diff(context.get("execution_context", {}).get("git_diff"))
        edited_files = get_list(context, "edited_files")
        file_count = max(len(edited_files), diff["files"])
        net_added = diff["added"] - diff["removed"]

        # Heuristic penalties. More expansion markers and novelty lower score.
        penalty = 0.0
        penalty += min(0.5, 0.15 * expansion_hits)
        penalty += min(0.3, 0.3 * novelty_ratio)
        penalty += min(0.2, max(0, file_count - 5) * 0.03)
        penalty += min(0.15, max(0, net_added - 30) * 0.005)

        value = max(0.0, 1.0 - penalty)

        if value >= 0.8:
            verdict = "Work stays within the original scope."
        elif value >= 0.55:
            verdict = "Minor scope expansion detected beyond original objective."
        else:
            verdict = "Significant scope creep or feature expansion beyond intent."

        return [
            Evidence(
                source=self.name,
                value=round(value, 3),
                confidence=0.8,
                details=f"{verdict} (expansion markers={expansion_hits}, files={file_count}, net +{net_added})",
            )
        ]
