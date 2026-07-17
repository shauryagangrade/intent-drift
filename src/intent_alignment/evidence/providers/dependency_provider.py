from ...models import Evidence
from ..analysis import (
    get_list,
    get_text,
    is_empty,
    parse_git_diff,
)
from ..base import EvidenceProvider


class DependencyProvider(EvidenceProvider):
    """Detects dependency-related drift and unplanned scope expansion.

    New dependencies in a diff (``pip install``, ``requirements``/``pyproject``
    changes, ``import`` of new third-party packages) can indicate the work has
    grown beyond the original, dependency-light objective. We count new
    dependency signals in the git diff and recent commands and penalize for each,
    unless the goal's language already anticipated them.
    """

    @property
    def name(self) -> str:
        return "dependency_provider"

    @property
    def weight(self) -> float:
        # Dependency changes can indicate scope creep / hidden work.
        return 0.10

    def collect(self, context: dict) -> list[Evidence]:
        if is_empty(context):
            return [
                Evidence(
                    source=self.name,
                    value=0.0,
                    confidence=0.0,
                    details="No dependency information available.",
                )
            ]

        exec_ctx = context.get("execution_context", {}) or {}
        diff = parse_git_diff(exec_ctx.get("git_diff"))
        commands = " ".join(str(c) for c in get_list(context, "recent_commands")).lower()
        goal_text = get_text(context, "text") or get_text(context, "goal")

        # Signals of new/changed dependencies.
        signals = 0
        if "pip install" in commands or "npm install" in commands or "cargo add" in commands:
            signals += 1
        diff_lower = context.get("execution_context", {}).get("git_diff", "").lower()
        if (
            "requirements.txt" in diff_lower
            or "pyproject.toml" in diff_lower
            or "package.json" in diff_lower
        ):
            signals += 1

        # Did the goal anticipate external libraries?
        anticipated = any(
            kw in goal_text
            for kw in ["library", "framework", "sdk", "package", "dependency", "integrate", "api"]
        )

        penalty = 0.0
        if signals and not anticipated:
            penalty = min(0.6, 0.3 * signals)

        value = max(0.0, 1.0 - penalty)

        if signals == 0:
            verdict = "No new dependency signals detected."
        elif anticipated:
            verdict = "Dependency changes present but consistent with goal."
        elif value >= 0.6:
            verdict = "Minor unplanned dependency changes."
        else:
            verdict = "New dependencies suggest scope expansion beyond original intent."

        return [
            Evidence(
                source=self.name,
                value=round(value, 3),
                confidence=0.8 if diff["total"] or commands else 0.5,
                details=f"{verdict} (dependency signals={signals})",
            )
        ]
