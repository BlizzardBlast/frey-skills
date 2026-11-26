"""Validate visible human-usability guidance in the repository gate, not model behavior."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.documentation import inline_text, parse_visible, section_tokens


SKILL_ROOT = Path(__file__).resolve().parents[1] / "test-strategy"


class HumanUsabilityProseTests(unittest.TestCase):
    """Protect the visible guidance and key decisions, not model behavior."""

    TITLE = "Human usability evidence (conditional)"
    REFERENCE = SKILL_ROOT / "references" / "risk-and-scenario-rules.md"
    HEADER = "| Example condition | Observable strategy decision |"
    CASES = {
        "A changed onboarding journey must be understood unaided": (
            "Propose a goal-based participant task and separate functional/accessibility checks"
        ),
        "A scripted E2E test completes an onboarding journey": (
            "Count it as functional evidence, not a human usability result"
        ),
        "No participants are available for optional formative research": (
            "Record the gap without inventing results or automatically blocking release"
        ),
        "A required human usability acceptance measure cannot be assessed": (
            "Record blocked evidence and apply the existing readiness rules"
        ),
        "Participant reports success but the wrong record was saved": (
            "Record incorrect completion, not verified success"
        ),
        "Prototype completes a simulated save": (
            "Record the prototype outcome only; production persistence remains unverified"
        ),
        "Routine visual fix with no material usability risk": (
            "Use ordinary risk-based verification; participant research is not required"
        ),
    }
    # Exact normalized policy blocks protect selected decisions, not arbitrary
    # prose semantics. Intentional policy changes require updating the contract.
    GUARDRAILS = (
        (
            "When the change materially affects a user journey and its success depends on "
            "discoverability, comprehension, or human effort, distinguish functional verification "
            "from formative usability observation. Routine visual fixes, internal APIs, and "
            "deterministic behavior alone do not require participant research."
        ),
        (
            "Ground the goal and observable success condition in authorized requirements. "
            "Independently verify actual task outcomes where applicable, using the smallest "
            "suitable observable evidence (for example, the correct saved record or calculated "
            "result); a participant's belief that they succeeded is not sufficient. Do not invent "
            "requirements or require privileged inspection when ordinary user-visible evidence "
            "establishes the outcome."
        ),
        (
            "For a prototype, record its version, linked states, simulated behavior and "
            "limitations; do not infer production behavior from it. Distinguish a verified "
            "prototype outcome from an actual production side effect."
        ),
        (
            "Use synthetic/minimized data, a safe environment and consented, non-identifying "
            "observations. Do not prescribe external uploads, recordings, recruitment, production "
            "mutations or telemetry without explicit authority."
        ),
        (
            "Keep required functional, accessibility and security checks independent. An "
            "automated E2E script, screenshot review, or simulated agent participant can "
            "supplement review but cannot prove human discoverability, comprehension or measured "
            "human task time."
        ),
        (
            "Mark unavailable participant or prototype evidence explicitly; do not claim that "
            "research ran. Optional formative evidence is not a universal merge/release gate. If "
            "human evidence is an accepted requirement or is material to a critical/high-risk "
            "decision, apply the parent skill's completeness/readiness rules and record the "
            "blocked coverage."
        ),
    )

    def assert_usability_contract(self, document: str) -> None:
        tokens, _ = parse_visible(document)
        headings = [
            index
            for index, token in enumerate(tokens[:-1])
            if token.type == "heading_open"
            and token.tag == "h2"
            and token.level == 0
            and inline_text(tokens[index + 1].children or []) == self.TITLE
        ]
        self.assertEqual(len(headings), 1, "Require one visible usability section")
        section = section_tokens(document, self.TITLE)
        tables = [
            section[index + 1].content
            for index, token in enumerate(section[:-1])
            if token.type == "paragraph_open"
            and token.level == 0
            and section[index + 1].type == "inline"
            and section[index + 1].content.startswith(self.HEADER)
        ]
        self.assertEqual(len(tables), 1, "Require one visible case table")
        rows = tables[0].splitlines()
        self.assertEqual(rows[:2], [self.HEADER, "| --- | --- |"])
        self.assertEqual(len(rows), len(self.CASES) + 2)
        cases = {}
        for row in rows[2:]:
            self.assertTrue(row.startswith("| ") and row.endswith(" |"), row)
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertEqual(len(cells), 2, row)
            condition, decision = cells
            self.assertNotIn(condition, cases)
            cases[condition] = decision
        self.assertEqual(cases, self.CASES)

        # Only plain, active root paragraphs and direct list-item paragraphs
        # can supply a policy block. Do not stitch fragments across blocks,
        # ignore punctuation, or match a substring inside a reversed statement.
        paragraphs = []
        for index, token in enumerate(section[:-1]):
            if token.type != "paragraph_open":
                continue
            direct_item = (
                token.level == 2
                and index > 0
                and section[index - 1].type == "list_item_open"
                and section[index - 1].level == 1
            )
            if token.level != 0 and not direct_item:
                continue
            inline = section[index + 1]
            if inline.type != "inline" or inline.content.startswith("|"):
                continue
            children = inline.children or []
            if any(child.type not in {"text", "softbreak", "hardbreak"} for child in children):
                continue
            prose = "".join(
                child.content if child.type == "text" else " "
                for child in children
            )
            paragraphs.append(" ".join(prose.split()).casefold())
        for boundary in self.GUARDRAILS:
            self.assertEqual(paragraphs.count(boundary.casefold()), 1, boundary)

    def test_human_usability_contract(self) -> None:
        self.assert_usability_contract(self.REFERENCE.read_text(encoding="utf-8"))

    def test_rejects_missing_duplicate_and_reversed_decisions(self) -> None:
        document = self.REFERENCE.read_text(encoding="utf-8")
        for condition, decision in self.CASES.items():
            row = f"| {condition} | {decision} |"
            for replacement in ("", row + "\n" + row, f"| {condition} | Unverified |"):
                with self.subTest(condition=condition, replacement=replacement):
                    with self.assertRaises(AssertionError):
                        self.assert_usability_contract(document.replace(row, replacement, 1))

    def test_rejects_hidden_case_table_and_removed_authority_boundary(self) -> None:
        document = self.REFERENCE.read_text(encoding="utf-8")
        start = document.index(self.HEADER)
        end = document.index("\n\n", start)
        table = document[start:end]
        for wrapper in (("<!--\n", "\n-->"), ("```markdown\n", "\n```")):
            with self.subTest(wrapper=wrapper):
                hidden = document.replace(table, wrapper[0] + table + wrapper[1], 1)
                with self.assertRaises(AssertionError):
                    self.assert_usability_contract(hidden)
        weakened = document.replace("without explicit authority", "without approval", 1)
        self.assertNotEqual(weakened, document)
        with self.assertRaises(AssertionError):
            self.assert_usability_contract(weakened)

    def test_rejects_reversed_or_weakened_policy_blocks(self) -> None:
        document = self.REFERENCE.read_text(encoding="utf-8")
        mutations = (
            ("Independently verify actual task outcomes",
             "Do not independently verify actual task outcomes"),
            ("Optional formative evidence is not a universal",
             "Reject the rule that optional formative evidence is not a universal"),
            ("do not require participant", "require participant"),
            ("cannot prove human discoverability", "can prove human discoverability"),
            ("apply the parent skill's", "do not apply the parent skill's"),
            ("do not infer production behavior from it", "infer production behavior from it"),
            ("without explicit authority", "without approval"),
        )
        for original, replacement in mutations:
            with self.subTest(original=original):
                self.assertEqual(document.count(original), 1)
                with self.assertRaises(AssertionError):
                    self.assert_usability_contract(document.replace(original, replacement, 1))

    def test_rejects_policy_block_moved_into_quoted_or_fenced_example(self) -> None:
        document = self.REFERENCE.read_text(encoding="utf-8")
        start = document.index("- Keep required functional, accessibility and security checks independent.")
        end = document.index("\n- Mark unavailable", start)
        policy = document[start:end]
        for replacement in (
            "\n".join("> " + line for line in policy.splitlines()) + "\n",
            "\n\n```markdown\n" + policy + "\n```\n",
            "\n\n<!--\n" + policy + "\n-->\n",
        ):
            with self.subTest(replacement=replacement), self.assertRaises(AssertionError):
                self.assert_usability_contract(document.replace(policy, replacement, 1))


if __name__ == "__main__":
    unittest.main()
