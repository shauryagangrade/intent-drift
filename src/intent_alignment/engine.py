from typing import Any

from .evidence import EvidenceProvider
from .models import AlignmentContext, AlignmentReport


class IntentAlignmentEngine:
    """Main engine for intent alignment analysis."""

    def __init__(self):
        """Initialize the engine with default evidence providers."""
        self.providers: list[EvidenceProvider] = []
        self._register_default_providers()

    def _register_default_providers(self) -> None:
        """Register the default set of evidence providers."""
        # Import providers here to avoid circular imports
        from .evidence.providers import (
            ArchitectureProvider,
            ConstraintProvider,
            DependencyProvider,
            ExecutionProvider,
            FileGraphProvider,
            GoalProvider,
            ProblematicFindingsProvider,
            RequirementCoverageProvider,
            ScopeProvider,
        )

        self.providers = [
            GoalProvider(),
            ConstraintProvider(),
            ScopeProvider(),
            ArchitectureProvider(),
            ExecutionProvider(),
            FileGraphProvider(),
            DependencyProvider(),
            RequirementCoverageProvider(),
            ProblematicFindingsProvider(),
        ]

    def add_provider(self, provider: EvidenceProvider) -> None:
        """Register an evidence provider to use during evaluation."""
        self.providers.append(provider)

    def evaluate(self, context: AlignmentContext) -> AlignmentReport:
        """
        Analyze the alignment between original goal and current implementation.

        Args:
            context: Alignment context containing goal, plan, and execution data.
                Accepts either an :class:`AlignmentContext` or a plain dict with
                the same three keys. Providers always receive a plain dict view.

        Returns:
            Alignment report with assessment results
        """
        # Accept a plain dict for convenience (e.g. example scripts and tests
        # that construct context inline) and normalize to AlignmentContext.
        context_dict: dict[str, Any]
        if isinstance(context, AlignmentContext):
            context_dict = {
                "original_goal": context.original_goal,
                "current_plan": context.current_plan,
                "execution_context": context.execution_context,
            }
        elif isinstance(context, dict):
            context_dict = {
                "original_goal": context.get("original_goal", {}),
                "current_plan": context.get("current_plan", {}),
                "execution_context": context.get("execution_context", {}),
            }
        else:
            raise TypeError(
                "evaluate() expects an AlignmentContext or a dict with "
                "'original_goal', 'current_plan', 'execution_context' keys."
            )

        # Collect evidence from all registered providers
        all_evidence = []
        for provider in self.providers:
            all_evidence.extend(provider.collect(context_dict))

        # Import scoring functions
        from .scoring import compute_weighted_score
        from .utils import (
            compute_confidence,
            determine_status,
            generate_recommendation,
            generate_risk_assessment,
            generate_summary,
        )

        # Compute weighted score and alignment breakdown
        weighted_score, component_scores = compute_weighted_score(all_evidence, self.providers)

        # Calculate confidence based on evidence consistency and confidence scores
        confidence = compute_confidence(all_evidence)

        # Determine status based on alignment score
        status = determine_status(weighted_score)

        # Generate report components
        summary = generate_summary(component_scores, weighted_score)
        risk = generate_risk_assessment(all_evidence, component_scores)
        recommendation = generate_recommendation(component_scores, weighted_score)

        # Create the alignment report
        report = AlignmentReport(
            overall_alignment=weighted_score,
            confidence=confidence,
            status=status,
            breakdown=component_scores,
            summary=summary,
            evidence=all_evidence,
            risk=risk,
            recommendation=recommendation,
            timeline=[],  # Timeline would be populated with historical data in a real implementation
        )

        return report
