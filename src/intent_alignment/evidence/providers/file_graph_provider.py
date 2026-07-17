from ...models import Evidence
from ..analysis import (
    get_list,
    get_text,
    is_empty,
    parse_git_diff,
)
from ..base import EvidenceProvider


class FileGraphProvider(EvidenceProvider):
    """Analyzes which files are touched and whether the focus area drifted.

    The set of edited files should map to the area the goal implied. We infer
    the intended area from the goal/plan vocabulary and check how many edited
    files' names contain those keywords. Editing many files unrelated to the
    goal is a signal of focus drift or a broad refactor that may not advance the
    objective.
    """

    @property
    def name(self) -> str:
        return "file_graph_provider"

    @property
    def weight(self) -> float:
        # Editing patterns are a useful secondary drift signal.
        return 0.15

    def collect(self, context: dict) -> list[Evidence]:
        if is_empty(context):
            return [
                Evidence(
                    source=self.name,
                    value=0.0,
                    confidence=0.0,
                    details="No file editing information available.",
                )
            ]

        goal_text = get_text(context, "text") or get_text(context, "goal")
        plan_summary = get_text(context, "summary") or get_text(context, "plan")
        intent_text = f"{goal_text} {plan_summary}"

        edited_files = get_list(context, "edited_files")
        diff = parse_git_diff(context.get("execution_context", {}).get("git_diff"))
        file_count = max(len(edited_files), diff["files"])

        # If nothing was edited, fall back to a neutral-but-present signal.
        if not edited_files and diff["total"] == 0:
            return [
                Evidence(
                    source=self.name,
                    value=0.7,
                    confidence=0.4,
                    details="No edited files recorded; assuming neutral focus.",
                )
            ]

        # Relevant files: filename shares a keyword with the stated intent.
        relevant = 0
        for f in edited_files:
            fname = str(f).lower()
            base = fname.split("/")[-1].replace(".py", "").replace(".", " ")
            if any(kw in base for kw in intent_text.split() if len(kw) > 3):
                relevant += 1

        if edited_files:
            relevance = relevant / len(edited_files)
        else:
            relevance = 1.0 if file_count <= 3 else 0.5

        # Broad, scattered edits (many unrelated files) reduce focus confidence.
        scatter_penalty = min(0.3, max(0, file_count - 5) * 0.04)
        value = max(0.0, relevance - scatter_penalty)

        if value >= 0.7:
            verdict = "Edited files map well to the intended focus area."
        elif value >= 0.45:
            verdict = "Some edited files fall outside the intended focus area."
        else:
            verdict = "Editing activity has scattered away from the intended area."

        return [
            Evidence(
                source=self.name,
                value=round(value, 3),
                confidence=0.75,
                details=f"{verdict} ({relevant}/{len(edited_files) if edited_files else file_count} files relevant)",
            )
        ]
