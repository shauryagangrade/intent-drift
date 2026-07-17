from ...models import Evidence
from ..analysis import (
    get_list,
    is_empty,
    parse_git_diff,
)
from ..base import EvidenceProvider


class ArchitectureProvider(EvidenceProvider):
    """Detects architectural drift, unnecessary complexity, and hidden rewrites.

    Architectural integrity is assessed from the git diff shape: (a) a rewrite
    signature — large deletions paired with large additions in the same files —
    suggests a hidden rewrite rather than targeted change; (b) an explosion of
    new files/symbols suggests unnecessary complexity or overengineering; (c) a
    healthy, mostly-additive change tightly scoped to a few files indicates the
    structure is being respected.
    """

    @property
    def name(self) -> str:
        return "architecture_provider"

    @property
    def weight(self) -> float:
        # Architecture divergence is a major, often invisible, drift signal.
        return 0.25

    def collect(self, context: dict) -> list[Evidence]:
        if is_empty(context):
            return [
                Evidence(
                    source=self.name,
                    value=0.0,
                    confidence=0.0,
                    details="No architectural information available.",
                )
            ]

        exec_ctx = context.get("execution_context", {}) or {}
        diff = parse_git_diff(exec_ctx.get("git_diff"))
        edited_files = get_list(context, "edited_files")
        file_count = max(len(edited_files), diff["files"])

        added, removed = diff["added"], diff["removed"]
        total = max(1, diff["total"])

        # Rewrite signature: heavy simultaneous deletions + additions in few
        # files. A pure addition (no deletions) is normal incremental work and
        # is NOT treated as a rewrite.
        rewrite_signal = 0.0
        if removed > 0 and file_count <= 3:
            deletion_fraction = removed / total
            if deletion_fraction > 0.4:
                rewrite_signal = max(0.6, min(1.0, deletion_fraction))
            # Large net rewrite: many lines deleted relative to file count.
            elif removed > 50:
                rewrite_signal = 0.6

        # Complexity explosion: many new files for a small objective.
        new_file_signal = min(1.0, max(0, file_count - 6) / 10.0)

        penalty = 0.5 * rewrite_signal + 0.5 * new_file_signal
        value = max(0.0, 1.0 - penalty)

        reasons = []
        if rewrite_signal > 0.4:
            reasons.append("possible hidden rewrite (high add/delete churn in few files)")
        if new_file_signal > 0.4:
            reasons.append("large number of new files suggests overengineering")
        if not reasons:
            reasons.append("change appears structurally targeted")

        return [
            Evidence(
                source=self.name,
                value=round(value, 3),
                confidence=0.8 if diff["total"] > 0 else 0.5,
                details=f"Architecture: {'; '.join(reasons)} (files={file_count}, +{added}/-{removed})",
            )
        ]
