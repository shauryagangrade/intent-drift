from intent_alignment import IntentAlignmentEngine


def main():
    """Example demonstrating intent alignment engine usage."""

    # Initialize the engine
    engine = IntentAlignmentEngine()

    # Define alignment context
    alignment_context = {
        "original_goal": {
            "text": "Reduce the application's memory usage.",
            "constraints": ["Stay under 100MB RAM", "Maintain API compatibility"],
            "success_criteria": ["Peak memory < 50MB", "Startup time < 2s"],
        },
        "current_plan": {
            "summary": "Optimizing startup initialization for faster application load.",
            "steps": [
                "Profile initialization bottlenecks",
                "Optimize startup sequence",
                "Add caching layer",
            ],
        },
        "execution_context": {
            "edited_files": ["main.py", "startup.py", "initialization.py"],
            "git_diff": "+ def optimize_startup():\n+     # Fast startup optimizations\n- def reduce_memory():\n-     # Commented out memory reducer\n",
            "recent_commands": [
                "pip install numpy",
                "python -m cProfile main.py",
                "python -m pytest startup",
            ],
            "recent_messages": [
                "We're making progress on startup optimization",
                "Those memory reductions aren't working as expected",
            ],
            "reasoning_summary": "Focusing on startup performance rather than memory optimization",
        },
    }

    # Add evidence providers (would normally be more comprehensive)
    # engine.add_provider(GoalProvider())
    # engine.add_provider(ConstraintProvider())
    # engine.add_provider(ScopeProvider())
    # engine.add_provider(ArchitectureProvider())
    # engine.add_provider(ExecutionProvider())

    # In a real implementation, these would be registered providers
    # For demonstration, we just use the engine
    report = engine.evaluate(alignment_context)

    # Print the report (in reality, agents would consume the structured data)
    print("Intent Alignment Report")
    print("=" * 50)
    print(f"Overall Alignment: {report.overall_alignment}%")
    print(f"Status: {report.status}")
    print(f"Confidence: {report.confidence}%")
    print()
    print("Summary:")
    print(report.summary)
    print()
    print("Evidence:")
    for i, evidence in enumerate(report.evidence, 1):
        print(f"  {i}. [{evidence.source}] {evidence.details}")
    print()
    print(f"Risk: {report.risk}")
    print(f"Recommendation: {report.recommendation}")


if __name__ == "__main__":
    main()
