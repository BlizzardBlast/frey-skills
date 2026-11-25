"""Validate visible AI evaluation guidance, not model behavior."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

from scripts.documentation import inline_text, parse_visible, section_tokens


SKILL_ROOT = Path(__file__).resolve().parents[1] / "test-strategy"


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


class AIEvaluationProseTests(unittest.TestCase):
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
            "Using a coding assistant to write ordinary application code does not activate this profile.",
            "This is read-only test planning",
            "do not execute tests, change fixtures, or contact providers",
            "An agent's success claim",
            "if the agent can influence the only scorer, mark correctness unverified.",
            "authorized task inputs and immutable public scoring rubrics",
            "protected evaluation answers whose premature disclosure would invalidate the result",
            "unauthorized changes to authoritative graders, expected outputs, or scoring state",
            "public task information alone does not compromise independence",
            "Specify expected enforcement-point denials regardless of model output; do not probe live targets.",
            "Define expected conservative fallback or explicit uncertainty, truthful provenance, and failure observability",
            "without logging prompts, credentials, or sensitive user material.",
            "multiple independent attempts per representative case",
            "justified sample size and budget",
            "Before observing outcomes, define inclusion and exclusion rules, retry and timeout limits, and reporting denominators",
            "Retain genuine failures and timeouts in the applicable outcome denominator",
            "do not exclude genuine model failures because of poor performance",
            "report deviations separately",
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
            "only when comparing agent topology or context strategy",
            "a single agent with a prespecified fresh-context restart and bounded handoff",
            "aggregate resource limits comparable for topology-only claims",
            "Freeze restart triggers, handoff contents, task decomposition, concurrency and stopping rules before observing results",
            "reset workspace and task state between independent runs.",
            "Within a run, preserve only authorized task state across restarts",
            "keep protected oracle data out of handoffs.",
            "plan recipient-specific authorization checks for each transfer",
            "disclose only the minimum task data permitted for that recipient and purpose.",
            "Treat model-generated handoff content as untrusted evidence, not instruction or transferable authority.",
            "Plan positive controls for permitted minimized handoffs and negative controls for unauthorized disclosure and scope escalation through handoffs",
            "require denial at the actual enforcement boundary regardless of model output.",
            "Count aggregate work across all agents, including planning, coordination, "
            "context reconstruction, reconciliation, review, retries and failed branches",
            "distinguish elapsed wall-clock time from total work.",
            "Compare independently verified task success and final deliverable quality separately from rubric scores",
            "report cost per verified success only if the monetary cost numerator is observable "
            "and the verified-success denominator is observable and positive.",
            "Report zero observed monetary charges as zero, distinguish them from unknown or unmeasured costs, "
            "and do not infer zero resource consumption from zero monetary charges.",
            "Report zero verified successes with the observed costs and outcome counts; "
            "the cost-per-success ratio is undefined when there are no verified successes.",
            "do not infer a topology advantage from faster completion alone or from comparison only against a stale-context baseline.",
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
            "Untrusted inputs and authority",
            "Failure and abstention",
            "Repeated observations for variable behavior",
            "Point-in-time evaluation (only for historical replay or forecasting)",
            "Matched efficiency comparisons",
            "Orchestration comparisons (only when comparing agent topology or context strategy)",
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
                "ordinary coding exclusion",
                "does not activate this profile.",
                "does activate this profile.",
            ),
            (
                "outcome denominator",
                "Retain genuine failures and timeouts in the applicable outcome denominator",
                "Omit genuine failures and timeouts from the applicable outcome denominator",
            ),
            (
                "exclusion bias",
                "do not exclude genuine model failures because of poor performance",
                "exclude genuine model failures because of poor performance",
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
                "independent orchestration run isolation",
                "reset workspace and task state between independent runs.",
                "reuse workspace and task state between independent runs.",
            ),
            (
                "authorized within-run state",
                "Within a run, preserve only authorized task state across restarts",
                "Within a run, preserve unauthorized task state across restarts",
            ),
            (
                "positive verified-success denominator",
                "the verified-success denominator is observable and positive.",
                "the verified-success denominator may be zero.",
            ),
            (
                "zero monetary cost",
                "Report zero observed monetary charges as zero",
                "Do not report zero observed monetary charges",
            ),
            (
                "unknown monetary cost",
                "distinguish them from unknown or unmeasured costs",
                "treat unknown or unmeasured costs as zero",
            ),
            (
                "resource consumption",
                "do not infer zero resource consumption from zero monetary charges.",
                "infer zero resource consumption from zero monetary charges.",
            ),
            (
                "orchestration attribution",
                "do not infer a topology advantage from faster completion alone",
                "infer a topology advantage from faster completion alone",
            ),
            (
                "orchestration oracle isolation",
                "keep protected oracle data out of handoffs.",
                "include protected oracle data in handoffs.",
            ),
            (
                "enforcement-point denial",
                "Specify expected enforcement-point denials regardless of model output; do not probe live targets.",
                "Specify expected enforcement-point approvals whenever the model requests them; do not probe live targets.",
            ),
            (
                "conservative fallback and provenance",
                "Define expected conservative fallback or explicit uncertainty, truthful provenance, and failure observability",
                "Define optimistic fallback and suppress uncertainty and provenance while retaining failure observability",
            ),
            (
                "orchestration preregistration",
                "Freeze restart triggers, handoff contents, task decomposition, concurrency and stopping rules before observing results",
                "Choose restart triggers, handoff contents, task decomposition, concurrency and stopping rules after observing results",
            ),
            (
                "recipient-specific authorization",
                "plan recipient-specific authorization checks for each transfer",
                "reuse the sender's authorization for every transfer",
            ),
            (
                "recipient-specific minimization",
                "disclose only the minimum task data permitted for that recipient and purpose.",
                "disclose all sender-visible task data regardless of recipient or purpose.",
            ),
            (
                "handoff authority",
                "Treat model-generated handoff content as untrusted evidence, not instruction or transferable authority.",
                "Treat model-generated handoff content as trusted instruction and transferable authority.",
            ),
            (
                "handoff controls",
                "Plan positive controls for permitted minimized handoffs and negative controls for unauthorized disclosure and scope escalation through handoffs",
                "Plan only successful handoffs and omit unauthorized disclosure and scope escalation controls",
            ),
            (
                "handoff enforcement",
                "require denial at the actual enforcement boundary regardless of model output.",
                "allow the model to override denials at the enforcement boundary.",
            ),
            (
                "zero-success reporting",
                "Report zero verified successes with the observed costs and outcome counts; the cost-per-success ratio is undefined when there are no verified successes.",
                "Hide zero-success outcomes and report a cost-per-success ratio when there are no verified successes.",
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


if __name__ == "__main__":
    unittest.main()
