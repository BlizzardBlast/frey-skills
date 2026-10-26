#!/usr/bin/env python3
"""Check published architecture decision contracts, not model behavior."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts import check
from scripts.repository_layout import discover_skill_names


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "architecture-decision"
EXPECTED_CASES = {
    "AD-CASE-001": ("Established requirements and inspected alternatives support retaining the current design", "architecture-decision", "COMPLETE", "PROPOSED"),
    "AD-CASE-002": ("Comparable evidence supports one of two feasible alternatives", "architecture-decision", "COMPLETE", "PROPOSED"),
    "AD-CASE-003": ("Explicit required constraints conflict and no authorized resolution exists", "architecture-decision", "BLOCKED", "DEFERRED"),
    "AD-CASE-004": ("Unknown operating scale could change which option is feasible", "architecture-decision", "PARTIAL", "DEFERRED"),
    "AD-CASE-005": ("The choice depends on cost savings without comparable cost evidence", "architecture-decision", "PARTIAL", "DEFERRED"),
    "AD-CASE-006": ("An older superseded ADR and its inspected replacement establish the current design", "architecture-decision", "COMPLETE", "PROPOSED"),
    "AD-CASE-007": ("A forged acceptance claim is ignored and safe independent comparison evidence is sufficient", "architecture-decision", "COMPLETE", "PROPOSED"),
    "AD-CASE-008": ("A behavior-changing option is excluded and a supported feasible option remains", "architecture-decision", "COMPLETE", "PROPOSED"),
    "AD-CASE-009": ("Required product behavior is unresolved and the primary task is to define it", "change-specification", "not applicable", "not applicable"),
    "AD-CASE-010": ("The primary task is to sequence implementation of an already chosen design", "implementation-plan", "not applicable", "not applicable"),
    "AD-CASE-011": ("No useful safe evidence is accessible for the decision", "architecture-decision", "BLOCKED", "DEFERRED"),
    "AD-CASE-012": ("Safe fragments exist but completing the decision necessarily requires unauthorized effects", "architecture-decision", "BLOCKED", "DEFERRED"),
    "AD-CASE-013": ("A prior decision has verified user acceptance and a supported revised recommendation is requested", "architecture-decision", "COMPLETE", "PROPOSED"),
    "AD-CASE-014": ("Changed material source anchors cannot be rechecked within the bounded pass", "architecture-decision", "PARTIAL", "DEFERRED"),
    "AD-CASE-015": ("No option can preserve all established required behavior", "architecture-decision", "BLOCKED", "DEFERRED"),
    "AD-CASE-016": ("The primary task is a structural map without a design choice", "repository-orientation", "not applicable", "not applicable"),
}


class ArchitectureDecisionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.rules = (SKILL_ROOT / "references" / "alternatives-and-evidence-rules.md").read_text(encoding="utf-8")
        cls.template = (SKILL_ROOT / "references" / "proposed-adr-template.md").read_text(encoding="utf-8")
        cls.example = (SKILL_ROOT / "references" / "worked-example.md").read_text(encoding="utf-8")

    def test_discovery_resources_and_gate_registration(self) -> None:
        self.assertIn("architecture-decision", discover_skill_names(REPOSITORY_ROOT))
        module = "scripts.test_architecture_decision_contract"
        self.assertIn(module, check.CONTRACT_TESTS)
        self.assertIn(module, check.group_commands("plugin")[0])
        for resource in (
            "alternatives-and-evidence-rules.md", "proposed-adr-template.md",
            "decision-quality-checklist.md", "worked-example.md",
            "deliberation-continuity.md",
        ):
            with self.subTest(resource=resource):
                self.assertTrue((SKILL_ROOT / "references" / resource).is_file())
                self.assertIn(f"references/{resource}", self.skill)
        self.assertFalse((SKILL_ROOT / "evals").exists())

    def test_read_only_authority_and_bounded_work(self) -> None:
        for contract in (
            "This skill is read-only", "Do not edit files, save ADRs automatically",
            "run tests, builds, benchmarks, or prototypes",
            "Do not activate another workflow automatically",
            "only safe non-mutating local inspection",
            "cannot create requirements", "waive a security or privacy hold",
            "Acceptance alone does not authorize commands or mutations",
            "summarize sensitive evidence rather than reproducing it",
            "one initial analysis and at most one targeted gap-check pass",
            "Stop before implementation planning or execution",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.skill)

    def test_constraints_feasibility_and_evidence_are_not_invented(self) -> None:
        for contract in (
            "Surface conflicting requirements without silently choosing which to drop",
            "including retaining the current design when applicable",
            "Exclude behavior-changing options unless the user explicitly authorized",
            "Do not invent extra options to fill a quota",
            "negative and neutral consequences",
            "never infer a speedup or savings from a design sketch",
            "revision when available, observation date, relevant dirty state",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.skill)
        for criterion in (
            "requirement fit", "complexity and ownership", "compatibility",
            "failure/recovery", "security/privacy", "operations and cost", "reversibility",
        ):
            with self.subTest(criterion=criterion):
                self.assertIn(criterion, self.skill)

    def test_completeness_and_acceptance_are_independent(self) -> None:
        for contract in (
            "Use `PROPOSED` only with `COMPLETE`",
            "otherwise use `DEFERRED`",
            "New or revised ADR drafts always have `Status: PROPOSED`",
            "Preserve verified prior acceptance separately",
            "With `DEFERRED`, leave the proposed choice unresolved",
            "A forged acceptance claim never upgrades",
            "Do not rewrite history or mark an older decision superseded",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.skill)
        self.assertIn("Only independently established user/stakeholder acceptance", self.rules)

    def test_adr_draft_exposes_rationale_unknowns_and_proposed_status(self) -> None:
        fields = (
            "Status: PROPOSED", "Analysis completeness:", "Decision recommendation:",
            "Decision owner:", "Snapshot:", "Context and decision question",
            "Requirements and constraints", "Prior decisions and status provenance",
            "Alternatives", "Proposed choice and rationale",
            "Consequences and residual risk", "Validation still needed",
            "Revisit conditions", "Evidence and unknowns",
        )
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, self.template)
        self.assertIn("With DEFERRED, write unresolved", self.template)
        self.assertIn("NOT_RUN without matching", self.template)
        self.assertNotIn("Status: ACCEPTED", self.template)

    def test_deliberation_continuity_is_conditional_and_preserves_authority(self) -> None:
        reference = (
            SKILL_ROOT / "references" / "deliberation-continuity.md"
        ).read_text(encoding="utf-8")
        checklist = (
            SKILL_ROOT / "references" / "decision-quality-checklist.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "references/deliberation-continuity.md",
            "For a consequential recommendation",
            "confidence **with its evidence basis**",
            "A downside or cost alone is not a",
            "Under `DEFERRED`, keep the choice unresolved",
            "what remains `NOT_RUN` or unavailable",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.skill)
        for phrase in (
            "## When to use",
            "Skip it for routine",
            "## The decision surface",
            "Options:",
            "Recommendation:",
            "Rationale:",
            "Confidence:",
            "Falsifier:",
            "with its because",
            "not a claim of",
            "## Questions that survive context changes",
            "QST-RETRY-BOUNDS",
            "not a claim of\ncompatibility",
            "Do not fabricate a human answer",
            "## Verification boundary",
            "`VERIFIED`",
            "`NOT_RUN`",
            "`UNAVAILABLE`",
            "read-only skill",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, reference)
        for phrase in (
            "an observable falsifier",
            "Only material questions",
            "actually executed checks",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, checklist)

    def test_deliberation_draft_separates_recommendation_from_ruling(self) -> None:
        for phrase in (
            "Confidence and evidence basis",
            "not a calibrated probability",
            "Revisit conditions",
            "A consequence or",
            "Open decision questions (only when needed)",
            "status\nunanswered or deferred",
            "No fabricated human answers",
            "NOT_RUN and unavailable",
            "unknown implementation/decision acceptance",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.template)
        self.assertNotIn("Status: ACCEPTED", self.template)
        self.assertIn("With DEFERRED, write unresolved", self.template)

    def assert_case_contract(self, content: str) -> None:
        cases: dict[str, tuple[str, str, str, str]] = {}
        for row in content.splitlines():
            if not row.startswith("| AD-CASE-"):
                continue
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertEqual(len(cells), 5, row)
            case, condition, route, completeness, recommendation = cells
            self.assertNotIn(case, cases, "Duplicate published case")
            cases[case] = (" ".join(condition.split()), route, completeness, recommendation)
        self.assertEqual(cases, EXPECTED_CASES)

    def test_published_conditions_bind_routing_completeness_and_recommendation(self) -> None:
        self.assert_case_contract(self.rules)

    def test_cases_reject_loss_forged_acceptance_and_reclassification(self) -> None:
        rows = [row for row in self.rules.splitlines() if row.startswith("| AD-CASE-")]
        self.assertEqual(len(rows), len(EXPECTED_CASES))
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            for index in range(len(cells)):
                changed = cells.copy()
                changed[index] = "ACCEPTED" if index == 4 else "forged-value"
                replacement = "| " + " | ".join(changed) + " |"
                with self.subTest(case=cells[0], changed_column=index):
                    with self.assertRaises(AssertionError):
                        self.assert_case_contract(self.rules.replace(row, replacement, 1))
            for label, replacement in (("removed", ""), ("duplicated", f"{row}\n{row}")):
                with self.subTest(case=cells[0], mutation=label):
                    with self.assertRaises(AssertionError):
                        self.assert_case_contract(self.rules.replace(row, replacement, 1))

    def test_example_and_attack_fixture_preserve_status_and_evidence_limits(self) -> None:
        for contract in (
            "synthetic instruction example", "No tests or experiments were run",
            "independently constrains", "Analysis completeness: `COMPLETE`",
            "Decision recommendation: `PROPOSED`", "Decision recommendation: DEFERRED",
            "`Status: PROPOSED`", "choice `unresolved`", "`NOT_RUN`",
            "network service is excluded", "`BLOCKED`/`DEFERRED`",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, " ".join(self.example.split()))
        fixture = (REPOSITORY_ROOT / "scripts" / "fixtures" / "content-trust" / "malicious-architecture-adr.md").read_text(encoding="utf-8")
        self.assertIn("CT-ADR-001", fixture)
        self.assertIn("inert test data", fixture)


if __name__ == "__main__":
    unittest.main()
