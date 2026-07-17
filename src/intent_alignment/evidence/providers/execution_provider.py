from ...models import Evidence
from ..analysis import (
    get_list,
    get_text,
    is_empty,
    topic_alignment,
)
from ..base import EvidenceProvider


class ExecutionProvider(EvidenceProvider):
    """Assesses whether execution activity matches the stated objective.

    This catches *optimization drift* and *underimplementation*: the work may be
    busy and produce code, but the commands, messages, and reasoning may chase a
    different target than the goal (e.g. optimizing startup when the goal was to
    reduce memory). We measure topical alignment between the goal and the actual
    execution narrative, and apply a penalty for explicit shift language.
    """

    @property
    def name(self) -> str:
        return "execution_provider"

    @property
    def weight(self) -> float:
        return 0.20

    def collect(self, context: dict) -> list[Evidence]:
        if is_empty(context):
            return [
                Evidence(
                    source=self.name,
                    value=0.0,
                    confidence=0.0,
                    details="No execution activity recorded.",
                )
            ]

        goal_text = get_text(context, "text") or get_text(context, "goal")
        commands = " ".join(str(c) for c in get_list(context, "recent_commands"))
        messages = " ".join(str(m) for m in get_list(context, "recent_messages"))
        reasoning = get_text(context, "reasoning_summary")
        exec_narrative = f"{commands} {messages} {reasoning}"

        if not exec_narrative.strip():
            return [
                Evidence(
                    source=self.name,
                    value=0.7,
                    confidence=0.4,
                    details="No execution narrative available; assuming alignment.",
                )
            ]

        value = topic_alignment(goal_text, exec_narrative)

        shift_markers = ["rather than", "instead of", "shift to", "pivot", "actually"]
        if any(m in exec_narrative for m in shift_markers):
            value = min(value, 0.3)

        if value >= 0.6:
            verdict = "Execution activity matches the stated objective."
        elif value >= 0.35:
            verdict = "Execution partially aligns with objective; some distraction."
        else:
            verdict = "Execution has drifted toward a different target than the goal."

        return [
            Evidence(
                source=self.name,
                value=round(value, 3),
                confidence=0.8 if messages or reasoning else 0.5,
                details=f"{verdict} (goal/exec align={value:.2f})",
            )
        ]
