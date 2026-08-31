# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [0.1.2] - 2026-08-31

### Added

- Automatically released via the scheduled release workflow.


## [0.1.1] - 2026-08-16

### Added

- CI workflow (`.github/workflows/ci.yml`) with multi-version Python testing (3.10, 3.11, 3.12), linting (ruff), type checking (mypy), and build verification
- TestPyPI publishing workflow (`.github/workflows/publish-test.yml`) for pre-release testing
- Scheduled release workflow (`.github/workflows/release.yml`) with automatic version bumping, changelog generation, tagging, and GitHub release creation every 15 days
- PyPI publish workflow now skips pre-release tags (e.g., `v0.1.1-rc1`)
- `CHANGELOG.md` file with Keep a Changelog format
- Explicit `__all__` exports in all public modules (`models.py`, `utils.py`, `scoring.py`, `report.py`, `evidence/base.py`, `evidence/analysis.py`, `engine.py`)
- New unit tests verifying `__all__` exports (`tests/unit/test_module_exports.py`)
- Type hints for `IntentAlignmentEngine.__init__` return type
- Module-level constants for confidence weighting in `utils.py` (`_AVG_CONFIDENCE_WEIGHT`, `_CONSISTENCY_WEIGHT`, `_DIVERSITY_WEIGHT`, `_VARIANCE_SCALE`)
- `parse_git_diff` helper in `evidence/analysis.py`

### Changed

- **README.md**: Completely rewritten — concise project description, simplified quickstart with dict-based context, added badges, removed verbose architecture docs, added development setup instructions
- `pyproject.toml`: Fixed `target-version` and `python_version` config (were incorrectly set to version string)
- `AlignmentReport.breakdown` type: changed from `dict[str, dict]` to `dict[str, ScoreComponent]` for type safety
- Confidence calculation in `utils.py`: extracted weights as named constants, improved variance scaling
- Internal API cleanup: added `__all__` to all modules for explicit public interface

### Fixed

- PyPI publish workflow condition to exclude pre-release tags

### Infrastructure

- Complete CI/CD pipeline with test, lint, typecheck, build, TestPyPI, PyPI, and scheduled releases