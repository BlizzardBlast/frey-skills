#!/usr/bin/env python3
"""Regression tests for test-strategy structure and plugin discovery."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any

from scripts.documentation import inline_text, parse_visible, section_tokens


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "test-strategy"
SKILL_FILE = SKILL_ROOT / "SKILL.md"
AGENT_FILE = SKILL_ROOT / "agents" / "openai.yaml"
MANIFEST_PATH = REPOSITORY_ROOT / "plugin-template" / ".codex-plugin" / "plugin.json"
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_plugin_bundle.py"


EXPECTED_GIT_CASES = {
    "GIT-CASE-001": (
        "Changed behavior neither reads nor writes Git refs and does not rely on Git "
        "history as application state",
        "Use ordinary risk selection; do not add Git-specific scenarios",
    ),
    "GIT-CASE-002": (
        "Two agents target one ref",
        "A stale expected-OID update is rejected and earlier committed work survives",
    ),
    "GIT-CASE-003": (
        "Independent refs change during a multi-ref read",
        "Check documented consistency needs; do not assume a repository-wide snapshot",
    ),
    "GIT-CASE-004": (
        "Publication acknowledgment is lost",
        "Reconcile the intended ref/commit; an unresolved outcome must not prompt blind retry",
    ),
    "GIT-CASE-005": (
        "A new ref is acknowledged before a reader fetches",
        "Verify the intended tip and reachable objects from an independent reader",
    ),
    "GIT-CASE-006": (
        "A read-only consumer combines refs that can advance independently",
        "Test required cross-ref consistency and read-time interleavings even without "
        "writes by the consumer",
    ),
}


EXPECTED_AI_CASES = {
    "AI-CASE-001": (
        "Change has no runtime model or agent dependency",
        "Use ordinary risk selection; do not add AI-agent-specific scenarios",
    ),
    "AI-CASE-002": (
        "Agent claims success or passing tests",
        "Specify independent oracles for required artifacts and permitted effects",
    ),
    "AI-CASE-003": (
        "Agent can access protected evaluation answers prematurely or alter "
        "authoritative scoring without authorization",
        "Plan protection against premature disclosure and unauthorized scoring changes; "
        "mark affected correctness unverified if independence cannot be established",
    ),
    "AI-CASE-004": (
        "Model, tool or retrieved content is untrusted input",
        "Specify injection and unauthorized-action boundary scenarios",
    ),
    "AI-CASE-005": (
        "Provider or model returns an error or invalid response",
        "Specify conservative, observable failure and abstention scenarios",
    ),
    "AI-CASE-006": (
        "Comparing a model, adapter or agent harness",
        "Define varied configuration, fixed task controls, independent quality oracles, and measurable total work",
    ),
    "AI-CASE-007": (
        "Historical replay or forecasting depends on information available at a cutoff",
        "Specify temporal isolation, later-revision rejection and withheld outcomes; "
        "qualify results when leakage cannot be excluded",
    ),
    "AI-CASE-008": (
        "Agent reads authorized task inputs or an immutable public rubric",
        "Allow intended visibility; verify outcome independence without requiring "
        "unnecessary secrecy",
    ),
    "AI-CASE-009": (
        "Material outcome varies across model attempts or response times",
        "Plan independent repeated observations, report failures and uncertainty, "
        "and do not infer reliability from a single success",
    ),
}


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestStrategyContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_content = SKILL_FILE.read_text(encoding="utf-8")

    def test_skill_structure_and_intentional_no_evals_contract(self) -> None:
        self.assertTrue(SKILL_FILE.is_file())
        self.assertTrue(AGENT_FILE.is_file())
        for reference in (
            "repository-testing-profiles.md",
            "risk-and-scenario-rules.md",
            "strategy-quality-checklist.md",
        ):
            self.assertTrue((SKILL_ROOT / "references" / reference).is_file())
        self.assertFalse((SKILL_ROOT / "evals").exists())
        self.assertNotIn("evaluation-playbook", self.skill_content)

    def test_skill_keeps_modes_statuses_and_read_only_boundary(self) -> None:
        for mode in (
            "change test strategy",
            "regression test strategy",
            "migration test strategy",
            "release test strategy",
        ):
            self.assertIn(f"`{mode}`", self.skill_content)
        for value in (
            "COMPLETE",
            "PARTIAL",
            "BLOCKED",
            "READY",
            "READY_WITH_GAPS",
            "NOT_READY",
        ):
            self.assertIn(f"`{value}`", self.skill_content)
        self.assertIn("This skill is read-only", self.skill_content)
        self.assertIn("Never use `READY` with `PARTIAL` or `BLOCKED`", self.skill_content)

    def test_skill_keeps_activation_and_routing_boundaries(self) -> None:
        for boundary in (
            "Implementing tests or production code",
            "Running tests or verification commands as the primary task",
            "Debugging an unknown root cause",
            "Creating a general implementation plan",
            "Reviewing a diff or deciding merge readiness",
            "General release readiness beyond testing concerns",
        ):
            self.assertIn(boundary, self.skill_content)
        self.assertIn(
            "A test strategy alone does not satisfy the executable-plan gate",
            self.skill_content,
        )
        self.assertIn(
            "this skill does not decide merge readiness",
            self.skill_content,
        )

    def test_skill_keeps_risk_and_scenario_traceability_contracts(self) -> None:
        for field in (
            "Behavior or boundary",
            "Failure mode",
            "Impact",
            "Likelihood",
            "Change exposure",
            "Detectability",
            "Recovery",
            "Priority",
            "Evidence",
            "Planned coverage",
        ):
            self.assertIn(f"`{field}`", self.skill_content)
        for field in (
            "Covered risks",
            "Contract or behavior",
            "Preconditions",
            "Test data",
            "Action",
            "Expected result",
            "Test layer",
            "Environment",
            "Automation status",
            "Priority",
            "Evidence or gap",
        ):
            self.assertIn(f"`{field}`", self.skill_content)
        self.assertIn(
            "Material risks and observable contracts are traceable to prioritized scenarios",
            self.skill_content,
        )

    def test_skill_keeps_output_and_completion_contracts(self) -> None:
        for section in (
            "Scope mode",
            "Test objective and scope",
            "Risk matrix",
            "Behavior and contract inventory",
            "Test-layer allocation",
            "Scenario catalogue",
            "Test data and environment requirements",
            "Automation candidates",
            "Execution order",
            "Entry and exit criteria",
            "Residual risk",
            "Strategy completeness: COMPLETE|PARTIAL|BLOCKED",
            "Test readiness: READY|READY_WITH_GAPS|NOT_READY",
        ):
            self.assertIn(f"`{section}`", self.skill_content)
        self.assertIn("No repository or external-system mutation was performed", self.skill_content)
        self.assertIn("Missing context and blocked checks are honest", self.skill_content)

    def assert_git_case_contract(self, profile: str) -> None:
        marker = "## Git-backed published state and concurrent agents (conditional)\n"
        self.assertEqual(profile.count(marker), 1)
        section = profile.split(marker, 1)[1].split("\n## ", 1)[0]
        rows = [row for row in section.splitlines() if row.startswith("|")]
        self.assertEqual(
            rows[:2],
            [
                "| Case | Condition | Observable test-strategy decision |",
                "| --- | --- | --- |",
            ],
        )
        cases: dict[str, tuple[str, str]] = {}
        for row in rows[2:]:
            self.assertTrue(row.startswith("| ") and row.endswith(" |"), row)
            cells = [" ".join(cell.split()) for cell in row.strip("|").split("|")]
            self.assertEqual(len(cells), 3, row)
            case, condition, decision = cells
            self.assertRegex(case, r"^`GIT-CASE-\d{3}`$")
            case_id = case.strip("`")
            self.assertNotIn(case_id, cases)
            cases[case_id] = (condition, decision)
        self.assertEqual(cases, EXPECTED_GIT_CASES)

    def test_git_ref_consistency_profile_is_conditional_and_traceable(self) -> None:
        profile = (SKILL_ROOT / "references" / "repository-testing-profiles.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## Git-backed published state and concurrent agents (conditional)", profile)
        for boundary in (
            "only** when the changed system actually publishes",
            "Do not assume all Git servers provide Pando's consistency model",
            "This applies to read-only consumers as well as publishers",
            "a failed subprocess acknowledgment is not proof",
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary.casefold(), profile.casefold())
        self.assert_git_case_contract(profile)

    def test_git_case_contract_rejects_missing_duplicate_and_modified_cases(self) -> None:
        profile = (SKILL_ROOT / "references" / "repository-testing-profiles.md").read_text(
            encoding="utf-8"
        )
        rows = [row for row in profile.splitlines() if row.startswith("| `GIT-CASE-")]
        self.assertEqual(len(rows), len(EXPECTED_GIT_CASES))
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            for index in (1, 2):
                changed = cells.copy()
                changed[index] = "Different condition" if index == 1 else "Unsafe decision"
                replacement = "| " + " | ".join(changed) + " |"
                with self.subTest(case=cells[0], field=index), self.assertRaises(AssertionError):
                    self.assert_git_case_contract(profile.replace(row, replacement, 1))

            mutations = (
                profile.replace(row, "", 1),
                profile.replace(row, row + "\n" + row, 1),
                profile.replace(row, row[:-2] + " | extra |", 1),
                profile.replace(row, row.replace(cells[0], "`GIT-CASE-999`", 1), 1),
            )
            for index, mutated in enumerate(mutations):
                with self.subTest(case=cells[0], mutation=index), self.assertRaises(
                    AssertionError
                ):
                    self.assert_git_case_contract(mutated)

        same_ref = rows[1]
        contradictory = same_ref.replace(
            "is rejected and earlier committed work survives",
            "is allowed (not rejected) and earlier committed work survives",
        )
        self.assertNotEqual(contradictory, same_ref)
        with self.assertRaises(AssertionError):
            self.assert_git_case_contract(profile.replace(same_ref, contradictory, 1))

    def ai_profile_tokens(self, profile: str) -> list[Any]:
        """Return only the visible, top-level AI profile; exclude inert Markdown."""
        title = "AI model-mediated application behavior (conditional)"
        tokens, _ = parse_visible(profile)
        headings = [
            index
            for index, token in enumerate(tokens[:-1])
            if token.type == "heading_open"
            and token.tag == "h2"
            and token.level == 0
            and inline_text(tokens[index + 1].children or []) == title
        ]
        self.assertEqual(len(headings), 1, "Require exactly one visible AI profile heading")
        return section_tokens(profile, title)

    def assert_ai_case_contract(self, profile: str) -> None:
        section = self.ai_profile_tokens(profile)
        # CommonMark parses pipe tables as paragraphs; require a root-level
        # visible paragraph, not a comment, code fence, or quoted example.
        table_paragraphs = [
            section[index + 1].content
            for index, token in enumerate(section[:-1])
            if token.type == "paragraph_open"
            and token.level == 0
            and section[index + 1].type == "inline"
            and section[index + 1].content.startswith(
                "| Case | Condition | Observable test-strategy decision |"
            )
        ]
        self.assertEqual(len(table_paragraphs), 1, "Require one visible case table")
        rows = table_paragraphs[0].splitlines()
        self.assertEqual(
            rows[:2],
            [
                "| Case | Condition | Observable test-strategy decision |",
                "| --- | --- | --- |",
            ],
        )
        self.assertEqual(len(rows), len(EXPECTED_AI_CASES) + 2)
        cases: dict[str, tuple[str, str]] = {}
        for row in rows[2:]:
            self.assertTrue(row.startswith("| ") and row.endswith(" |"), row)
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertEqual(len(cells), 3, row)
            case, condition, decision = cells
            self.assertRegex(case, r"^`AI-CASE-\d{3}`$")
            case_id = case.strip("`")
            self.assertNotIn(case_id, cases)
            cases[case_id] = (condition, decision)
        self.assertEqual(cases, EXPECTED_AI_CASES)

    def active_ai_policy_paragraphs(self, profile: str) -> list[str]:
        """Extract active prose, excluding quoted examples and the case table."""
        section = self.ai_profile_tokens(profile)
        paragraphs = []
        quote_depth = 0
        for index, token in enumerate(section):
            if token.type == "blockquote_open":
                quote_depth += 1
            elif token.type == "blockquote_close":
                quote_depth -= 1
            elif (
                token.type == "inline"
                and not quote_depth
                and index > 0
                and section[index - 1].type == "paragraph_open"
                and not token.content.startswith(
                    "| Case | Condition | Observable test-strategy decision |"
                )
            ):
                prose = " ".join(
                    child.content for child in token.children or [] if child.type == "text"
                )
                paragraphs.append(" ".join(prose.split()).casefold())
        return paragraphs

    def assert_ai_policy_contract(self, profile: str) -> None:
        paragraphs = self.active_ai_policy_paragraphs(profile)
        for boundary in (
            "only when the system under test makes behavior-affecting model calls, "
            "delegates actions to an AI agent, or relies on model-selected tools.",
            "Using a coding assistant",
            "This is read-only test planning",
            "do not execute tests, change fixtures, or contact providers",
            "An agent's success claim",
            "if the agent can influence the only scorer, mark correctness unverified.",
            "authorized task inputs and immutable public scoring rubrics",
            "protected evaluation answers whose premature disclosure would invalidate the result",
            "unauthorized changes to authoritative graders, expected outputs, or scoring state",
            "public task information alone does not compromise independence",
            "do not probe live targets",
            "without logging prompts, credentials, or sensitive user material.",
            "multiple independent attempts per representative case",
            "justified sample size and budget",
            "first-attempt outcomes from retry-assisted outcomes",
            "record attempted, failed, timed-out and excluded runs with reasons",
            "observed outcome counts and latency distributions where measurable",
            "A single successful attempt does not establish repeatable reliability.",
            "plausible but unsupported claims and user-visible uncertainty",
            "critical-failure rule separately from aggregate scores",
            "record the residual uncertainty rather than claiming reliability",
            "only for historical replay or forecasting",
            "decision cutoff, including timezone and boundary semantics",
            "publication versus availability timestamps",
            "reveals outcomes only after a prediction is recorded",
            "an apparently old document contains a later revision",
            "Date-filtered search and a prompt telling a model to ignore future "
            "knowledge do not establish temporal isolation:",
            "model training, fine-tuning, retrieval, or task selection may still expose outcomes",
            "potentially contaminated, not as verified forecasting skill",
            "prefer prospective, sealed predictions",
            "not authorization to fetch archives, run models, or add forecasting infrastructure",
            "state exactly which model, adapter, prompt, or harness setting changes between arms",
            "bundled configuration comparison",
            "not proof of a single factor.",
            "record each arm's actual configuration",
            "not a fair comparison",
            "not permission to run model evaluations",
            "against requiring behavioral model evaluations as a merge gate",
        ):
            self.assertTrue(
                any(boundary.casefold() in paragraph for paragraph in paragraphs),
                f"Missing active AI policy: {boundary}",
            )

    def test_ai_model_mediated_profile_is_conditional_and_evidence_based(self) -> None:
        profile = (SKILL_ROOT / "references" / "repository-testing-profiles.md").read_text(
            encoding="utf-8"
        )
        self.assert_ai_case_contract(profile)
        self.assert_ai_policy_contract(profile)

    def test_ai_case_contract_rejects_hidden_markdown(self) -> None:
        profile = (SKILL_ROOT / "references" / "repository-testing-profiles.md").read_text(
            encoding="utf-8"
        )
        marker = "## AI model-mediated application behavior (conditional)\n"
        start = profile.index(marker)
        end = profile.index("\n## Performance and resilience", start)
        full_section = profile[start:end]
        table_start = profile.index("| Case | Condition | Observable test-strategy decision |", start)
        table_end = profile.index("\n\nThese are", table_start)
        table = profile[table_start:table_end]
        for label, content in (("section", full_section), ("table", table)):
            for wrapper in ("comment", "fence"):
                before, after = (
                    ("<!--\n", "\n-->")
                    if wrapper == "comment"
                    else ("```markdown\n", "\n```")
                )
                with self.subTest(location=label, wrapper=wrapper):
                    modified = profile.replace(content, before + content + after, 1)
                    with self.assertRaises(AssertionError):
                        self.assert_ai_case_contract(modified)

    def test_ai_policy_guardrails_cannot_be_hidden_as_examples(self) -> None:
        profile = (SKILL_ROOT / "references" / "repository-testing-profiles.md").read_text(
            encoding="utf-8"
        )
        for label in (
            "Independent outcome and grader integrity",
            "Repeated observations for variable behavior",
            "Point-in-time evaluation (only for historical replay or forecasting)",
            "Matched efficiency comparisons",
        ):
            policy = next(
                line for line in profile.splitlines() if line.startswith(f"- **{label}:**")
            )
            mutations = {
                "removed": "",
                "comment": f"\n<!--\n{policy}\n-->\n",
                "fence": f"\n```markdown\n{policy}\n```\n",
                "blockquote": f"\n> {policy}\n",
                "nested blockquote": f"\n- Example:\n\n  > {policy}\n",
            }
            for wrapper, replacement in mutations.items():
                with self.subTest(policy=label, wrapper=wrapper):
                    modified = profile.replace(policy, replacement, 1)
                    # The case table remains valid, but cannot substitute for prose.
                    self.assert_ai_case_contract(modified)
                    with self.assertRaises(AssertionError):
                        self.assert_ai_policy_contract(modified)

    def test_ai_policy_contract_rejects_reversed_safety_clauses(self) -> None:
        profile = (SKILL_ROOT / "references" / "repository-testing-profiles.md").read_text(
            encoding="utf-8"
        )
        self.assert_ai_policy_contract(profile)
        for label, original, contradictory in (
            (
                "applicability",
                "makes behavior-affecting model calls, delegates actions to an AI agent, "
                "or relies on model-selected tools.",
                "does not make behavior-affecting model calls, delegate actions to an AI agent, "
                "or rely on model-selected tools.",
            ),
            (
                "oracle independence",
                "if the agent can influence the only scorer, mark correctness unverified.",
                "if the agent can influence the only scorer, mark correctness verified.",
            ),
            (
                "sensitive logging",
                "without logging prompts, credentials, or sensitive user material.",
                "while logging prompts, credentials, or sensitive user material.",
            ),
            (
                "single-run reliability",
                "A single successful attempt does not establish repeatable reliability.",
                "A single successful attempt establishes repeatable reliability.",
            ),
            (
                "temporal isolation",
                "knowledge do not establish temporal isolation:",
                "knowledge establish temporal isolation:",
            ),
            (
                "comparison attribution",
                "not proof of a single factor.",
                "proof of a single factor.",
            ),
        ):
            with self.subTest(policy=label):
                self.assertEqual(profile.count(original), 1)
                modified = profile.replace(original, contradictory, 1)
                self.assertNotEqual(modified, profile)
                self.assert_ai_case_contract(modified)
                with self.assertRaises(AssertionError):
                    self.assert_ai_policy_contract(modified)

    def test_ai_case_contract_rejects_missing_duplicate_and_changed_cases(self) -> None:
        profile = (SKILL_ROOT / "references" / "repository-testing-profiles.md").read_text(
            encoding="utf-8"
        )
        rows = [row for row in profile.splitlines() if row.startswith("| `AI-CASE-")]
        self.assertEqual(len(rows), len(EXPECTED_AI_CASES))
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            mutations = [
                profile.replace(row, "", 1),
                profile.replace(row, row + "\n" + row, 1),
            ]
            for index in (1, 2):
                changed = cells.copy()
                changed[index] = "Changed condition" if index == 1 else "Unsafe decision"
                mutations.append(
                    profile.replace(row, "| " + " | ".join(changed) + " |", 1)
                )
            for index, mutated in enumerate(mutations):
                with self.subTest(case=cells[0], mutation=index), self.assertRaises(
                    AssertionError
                ):
                    self.assert_ai_case_contract(mutated)

    def test_agent_metadata_keeps_discovery_contract(self) -> None:
        content = AGENT_FILE.read_text(encoding="utf-8")
        self.assertRegex(content, r"(?m)^\s*display_name:\s*['\"]?Test Strategy['\"]?\s*$")
        self.assertIn("$test-strategy", content)
        self.assertRegex(content, r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        self.assertNotRegex(content, r"(?m)^\s*allow_implicit_invocation:\s*false\s*$")

    def test_manifest_keeps_test_strategy_discovery_contract(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        for keyword in ("test-strategy", "risk-based-testing", "testing"):
            self.assertIn(keyword, manifest["keywords"])
        self.assertTrue(
            any("$test-strategy" in prompt for prompt in manifest["interface"]["defaultPrompt"])
        )

    def test_validator_rejects_missing_test_strategy_keywords(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_plugin_bundle_test_strategy_contract")
        original = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        for keyword in ("test-strategy", "risk-based-testing", "testing"):
            with self.subTest(keyword=keyword):
                manifest = json.loads(json.dumps(original))
                manifest["keywords"].remove(keyword)
                errors: list[str] = []
                validator.validate_manifest(manifest, errors)
                self.assertTrue(
                    any(keyword in error and "missing discovery keywords" in error for error in errors),
                    errors,
                )


if __name__ == "__main__":
    unittest.main()
