from intent_alignment.models import Evidence
from intent_alignment.scoring import aggregate_scores, compute_weighted_score


class TestScoring:
    """Unit tests for scoring functions."""

    def test_compute_weighted_score_basic(self):
        """Test basic weighted score computation."""
        evidence = [
            Evidence(source="goal_provider", value=0.9, confidence=0.9, details="Good"),
            Evidence(source="scope_provider", value=0.7, confidence=0.8, details="Okay"),
        ]

        class MockProvider:
            def __init__(self, name, weight):
                self.name = name
                self.weight = weight

        providers = [
            MockProvider("goal_provider", 0.5),
            MockProvider("scope_provider", 0.5),
        ]

        overall, components = compute_weighted_score(evidence, providers)
        assert 0 <= overall <= 100
        assert len(components) == 2
        assert "goal_provider" in components
        assert "scope_provider" in components

    def test_empty_evidence(self):
        """Test behavior with no evidence."""
        overall, components = compute_weighted_score([], [])
        assert overall == 0.0
        assert components == {}

    def test_high_confidence_evidence(self):
        """Test that high confidence evidence dominates."""
        evidence = [
            Evidence(source="p1", value=0.2, confidence=0.2, details="Low confidence"),
            Evidence(source="p2", value=0.9, confidence=0.95, details="High confidence"),
        ]

        class MockProvider:
            def __init__(self, name, weight):
                self.name = name
                self.weight = weight

        providers = [MockProvider("p1", 0.5), MockProvider("p2", 0.5)]
        overall, _ = compute_weighted_score(evidence, providers)
        # Should be closer to 0.9 than 0.2
        assert overall > 0.5

    def test_aggregate_scores(self):
        """Test the legacy aggregate_scores function."""
        evidence = [
            Evidence(source="p1", value=0.8, confidence=0.9, details="Good"),
            Evidence(source="p1", value=0.6, confidence=0.7, details="Okay"),
        ]
        components = aggregate_scores(evidence)
        assert "p1" in components
        # Weighted by confidence: (0.8*0.9 + 0.6*0.7) / (0.9+0.7) = 1.14/1.6 = 0.7125
        expected = (0.8 * 0.9 + 0.6 * 0.7) / (0.9 + 0.7) * 100
        assert abs(components["p1"].score - expected) < 0.01
