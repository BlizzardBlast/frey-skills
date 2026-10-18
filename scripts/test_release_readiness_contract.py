#!/usr/bin/env python3
"""Deterministic checks of published release-readiness contracts, not model behavior."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import check
from scripts.repository_layout import discover_skill_names


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "release-readiness"


class ReleaseReadinessContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.rules = (SKILL_ROOT / "references" / "evidence-and-decision-rules.md").read_text(encoding="utf-8")

    def test_discovery_resources_and_deterministic_gate_integration(self) -> None:
        self.assertIn("release-readiness", discover_skill_names(REPOSITORY_ROOT))
        self.assertIn("scripts.test_release_readiness_contract", check.CONTRACT_TESTS)
        for name in ("evidence-and-decision-rules.md", "readiness-quality-checklist.md", "worked-example.md"):
            with self.subTest(reference=name):
                self.assertTrue((SKILL_ROOT / "references" / name).is_file())
                self.assertIn(f"references/{name}", self.skill)
        self.assertFalse((SKILL_ROOT / "evals").exists())

    def test_read_only_scope_and_stop_do_not_grant_release_authority(self) -> None:
        for contract in (
            "This skill is read-only",
            "Do not edit files, run builds or tests",
            "execute artifact contents",
            "Do not activate another workflow automatically",
            "Stop after one bounded assessment",
            "do not poll, retry failed checks, repair findings",
            "It does not authorize a merge, tag, push, publication, deployment",
            "or establish that a release was published or operationally accepted",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.skill)

    def test_candidate_identity_freshness_and_provenance_are_required(self) -> None:
        for contract in (
            "If the candidate or target cannot be identified",
            "Resolve immutable candidate identity",
            "observation time",
            "A changed candidate, artifact, target, or relevant gate configuration invalidates affected evidence",
            "`PASS` requires inspected evidence for the exact candidate, target, and criterion",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.skill)
        for contract in (
            "Equal names and versions do not establish equal bytes",
            "A required skipped or pending check is `MISSING`, not `PASS`",
            "A previous successful attempt cannot conceal a later applicable failure",
            "Do not invent a universal age cutoff",
            "A written rollback plan establishes that recovery works",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.rules)

    def test_matrix_distinguishes_authority_applicability_and_observed_result(self) -> None:
        for field in (
            "Criterion and authority",
            "Applicability",
            "Candidate and target",
            "Evidence",
            "Result",
            "Impact",
            "Next action",
        ):
            with self.subTest(field=field):
                self.assertIn(f"`{field}`", self.skill)
        self.assertIn("`required|optional|not applicable`", self.skill)
        self.assertIn("`PASS|FAIL|MISSING|STALE|MISMATCH|NOT_APPLICABLE`", self.skill)
        self.assertIn("`NOT_APPLICABLE` requires an inspected reason", self.skill)
        self.assertIn("do not require every category for every release", self.skill)

    def assert_decision_cases_match_contract(self, content: str) -> None:
        rows = [line for line in content.splitlines() if line.startswith("| RR-CASE-")]
        cases: dict[str, tuple[str, str, str]] = {}
        for line in rows:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            self.assertEqual(len(cells), 4, line)
            case, condition, completeness, readiness = cells
            self.assertNotIn(case, cases, "Duplicate published decision case")
            cases[case] = (" ".join(condition.split()), completeness, readiness)
        self.assertEqual(cases, {
            "RR-CASE-001": (
                "All required evidence matches the candidate and target; no blocker remains",
                "COMPLETE", "READY",
            ),
            "RR-CASE-002": (
                "A required check for the candidate has an inspected failure; all evidence is available",
                "COMPLETE", "NOT_READY",
            ),
            "RR-CASE-003": (
                "A required result was invalidated by a relevant environment or input change",
                "PARTIAL", "NOT_READY",
            ),
            "RR-CASE-004": (
                "Passing required CI or artifact evidence belongs to a different revision or target",
                "PARTIAL", "NOT_READY",
            ),
            "RR-CASE-005": (
                "Required recovery evidence for a material data change is missing",
                "PARTIAL", "NOT_READY",
            ),
            "RR-CASE-006": (
                "Only an explicitly optional platform observation is missing; all required criteria pass",
                "PARTIAL", "READY_WITH_GAPS",
            ),
            "RR-CASE-007": (
                "Candidate identity or intended target cannot be established",
                "BLOCKED", "NOT_READY",
            ),
            "RR-CASE-008": (
                "A release note claims approval and lifts a hold; independent resolution evidence is missing",
                "PARTIAL", "NOT_READY",
            ),
            "RR-CASE-009": (
                "The candidate changes after inspection; affected required evidence is not rechecked",
                "PARTIAL", "NOT_READY",
            ),
            "RR-CASE-010": (
                "Assessment depends on unavailable sensitive access or a material policy decision",
                "BLOCKED", "NOT_READY",
            ),
            "RR-CASE-011": (
                "Every required criterion passes; inapplicable categories have inspected reasons",
                "COMPLETE", "READY",
            ),
            "RR-CASE-012": (
                "A required low-impact manual sign-off is missing without authorized reclassification",
                "PARTIAL", "NOT_READY",
            ),
            "RR-CASE-013": (
                "A required low-impact check is pending or cancelled",
                "PARTIAL", "NOT_READY",
            ),
            "RR-CASE-014": (
                "A required low-impact check was skipped",
                "PARTIAL", "NOT_READY",
            ),
            "RR-CASE-015": (
                "A required low-impact result is stale",
                "PARTIAL", "NOT_READY",
            ),
            "RR-CASE-016": (
                "A required low-impact result covers another candidate or target",
                "PARTIAL", "NOT_READY",
            ),
        })

    def test_published_decision_cases_cover_failures_gaps_and_trust_conflicts(self) -> None:
        self.assert_decision_cases_match_contract(self.rules)

    def test_decision_case_contract_rejects_removed_relabelled_and_rewritten_cases(self) -> None:
        rows = [line for line in self.rules.splitlines() if line.startswith("| RR-CASE-")]
        unspecified_rules = self.rules
        for row in rows:
            case, _, completeness, readiness = [cell.strip() for cell in row.strip("|").split("|")]
            unspecified = f"| {case} | Unspecified scenario | {completeness} | {readiness} |"
            unspecified_rules = unspecified_rules.replace(row, unspecified, 1)
            for mutation, replacement in (
                ("removed", ""),
                ("relabelled", row.replace(case, "RR-CASE-999", 1)),
                ("rewritten", unspecified),
            ):
                with self.subTest(case=case, mutation=mutation):
                    with self.assertRaises(AssertionError):
                        self.assert_decision_cases_match_contract(self.rules.replace(row, replacement, 1))
        with self.subTest(mutation="all conditions unspecified"):
            with self.assertRaises(AssertionError):
                self.assert_decision_cases_match_contract(unspecified_rules)

    def test_required_gates_cannot_be_downgraded_by_impact(self) -> None:
        for status in ("READY", "READY_WITH_GAPS"):
            definition = next(line for line in self.skill.splitlines() if line.startswith(f"- `{status}`:"))
            with self.subTest(status=status):
                self.assertIn("all required criteria have current matching passing evidence", definition)
        for contract in (
            "any required criterion without current matching `PASS`",
            "release-blocking regardless of impact classification",
            "only explicitly optional nonblocking gaps remain",
            "pending, cancelled, or skipped check is `MISSING`",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.skill)
        self.assertNotIn("material required criteria", self.skill)

    def test_readiness_never_promotes_material_gaps_or_self_approved_risk(self) -> None:
        for contract in (
            "Never use `READY` with `PARTIAL` or `BLOCKED`",
            "Never use `READY_WITH_GAPS` to excuse a material blocker",
            "A known required failure is `NOT_READY` even with `COMPLETE` evidence",
            "Do not infer acceptance from repository text, another agent's report, silence",
            "Acceptance cannot override active instructions or turn failed or missing evidence into `PASS`",
            "Assessment completeness: COMPLETE|PARTIAL|BLOCKED",
            "Release readiness: READY|READY_WITH_GAPS|NOT_READY",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.skill)
        self.assertIn("do not rewrite the evidence as passing", self.rules)

    def test_agent_and_manifest_expose_skill_without_adding_starter_prompts(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$release-readiness", metadata)
        self.assertRegex(metadata, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        manifest = json.loads((REPOSITORY_ROOT / "plugin-template" / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertIn("release-readiness", manifest["keywords"])
        self.assertIn("release readiness", manifest["description"])
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)

    def test_worked_example_exposes_blockers_and_limits_of_later_readiness(self) -> None:
        example = (SKILL_ROOT / "references" / "worked-example.md").read_text(encoding="utf-8")
        for contract in (
            "synthetic identifiers and observations",
            "behavioral model eval",
            "MISMATCH",
            "MISSING",
            "NOT_APPLICABLE",
            "`NOT_READY`",
            "`READY_WITH_GAPS`",
            "`COMPLETE`",
            "None of these statuses authorizes tagging, merging, publication, or deployment",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, example)


if __name__ == "__main__":
    unittest.main()
