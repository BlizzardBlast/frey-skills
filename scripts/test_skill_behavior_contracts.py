#!/usr/bin/env python3
"""Regression tests for cross-skill behavior preserved during compression."""

from __future__ import annotations

import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class SkillBehaviorContractTests(unittest.TestCase):
    def test_debug_keeps_sensitive_evidence_guardrail(self) -> None:
        content = (REPOSITORY_ROOT / "debug" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(
            "Redact secrets and sensitive production, security, and privacy evidence "
            "from commands, logs, and output",
            content,
        )

    def test_iterative_review_resolves_compatible_conflicts(self) -> None:
        content = (REPOSITORY_ROOT / "iterative-self-review" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "When fixes conflict, choose or propose the safest requirement-preserving option",
            content,
        )
        self.assertIn(
            "Stop rather than churn when no safe compatible resolution exists or an issue toggles",
            content,
        )
        self.assertNotIn("Stop rather than churn when fixes conflict", content)


if __name__ == "__main__":
    unittest.main()
