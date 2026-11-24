"""Validate active threat-modeling guidance in the dependency-equipped repository gate."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.documentation import LiteralHTML, inline_text, parse_visible


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "threat-modeling" / "references" / "system-model-and-threat-ledger.md"

AI_INFERENCE_CONTRACTS = (
    "**categories** of outbound content",
    "never retrieve or reproduce real",
    "inference hosts, model developers",
    "inference-hosting and model-development",
    "without assuming separate entities or trust boundaries",
    "A single entity may perform both roles",
    "identify separate actors or boundaries",
    "only when inspected evidence or the stated design",
    "Record which entities can see",
    "use `unknown` for material access relationships",
    "developer hosting its own model",
    "without an invented inter-entity boundary",
    "private inference host",
    "separate host forwards prompts to the model developer",
    "trace that evidenced transfer and boundary",
    "zero-data-retention (ZDR)",
    "each downstream processor",
    "including fallback/retry routes",
    "mismatches or unknown propagation",
    "router's ZDR flag",
    "Do not assert a confirmed leak",
    "canary experiment, live provider",
    "**not** authorized by this read-only",
    "mark the affected coverage `PARTIAL`",
)

DELEGATED_ACTION_CONTRACTS = (
    "initiating principal, execution principal, downstream resource owner, and actual enforcement points",
    "specific task, operation, resource, destination and lifetime",
    "distinguish user authorization from agent/service credentials",
    "Check effective permissions at the downstream enforcement point, not just tool availability or prompt instructions",
    "subagent can acquire broader authority than the authorized task",
    "Model fallback, retries and substitutions when the intended resource fails",
    "Access to an alternative resource is not authorization to use it for this task",
    "Distinguish explicitly authorized failover from agent-selected scope expansion",
    "examine denial and escalation paths",
    "Map revocation and containment separately for model access, process execution, queued or in-flight actions, issued credentials and downstream resource access",
    "Blocking model access alone does not prove downstream access is revoked or that in-flight work stopped",
    "enforcement timing, propagation limits and effects that cannot be undone",
    "an unavailable authorized store versus an accessible but unapproved store",
    "a low-privilege requester using an agent with broader service permissions",
    "a model gateway denial while an already-issued resource credential remains usable",
    "threat hypotheses, not evidence of actual vulnerabilities or authority to execute tools, test credentials, or probe a live system",
    "Unknown material delegation or containment paths leave affected coverage `PARTIAL`",
    "Keep proposed controls distinct from observed implementation and validation status",
    "the existing read-only and bounded-stop rules still apply",
)

CONTRACTS = (
    (
        "AI inference supply-chain boundaries (when in scope)",
        AI_INFERENCE_CONTRACTS,
        ("host/developer", "inference host and model developer as separate actors"),
    ),
    (
        "Delegated agent actions and containment (when in scope)",
        DELEGATED_ACTION_CONTRACTS,
        (),
    ),
)


def section_prose(content: str, title: str) -> tuple[list[tuple[int, int]], list[str]]:
    """Return active paragraph text and matching root section source ranges."""
    tokens, _ = parse_visible(content)
    literal = LiteralHTML()
    quoted = 0
    active = False
    start = None
    ranges = []
    paragraphs = []
    for index, token in enumerate(tokens):
        if (
            token.type == "heading_open" and token.level == 0
            and token.tag in {"h1", "h2"} and not literal.tags
        ):
            if start is not None:
                ranges.append((start, token.map[0]))
            active = token.tag == "h2" and inline_text(tokens[index + 1].children or []) == title
            start = token.map[0] if active else None
        elif token.type == "blockquote_open":
            quoted += 1
        elif token.type == "blockquote_close":
            quoted -= 1
        elif token.type == "html_block" and not quoted:
            literal.feed(token.content)
        elif token.type == "inline" and not quoted:
            parts = []
            for child in token.children or []:
                if child.type == "html_inline":
                    literal.feed(child.content)
                elif literal.tags:
                    parts.append("\0")
                elif child.type == "text":
                    parts.append(child.content)
                elif child.type in {"softbreak", "hardbreak"}:
                    parts.append(" ")
                elif child.type == "code_inline" and child.content in {"unknown", "PARTIAL"}:
                    # These are named contract states, not example instructions.
                    parts.append(child.content)
                elif child.type in {"code_inline", "image"}:
                    parts.append("\0")
            if active and index > 0 and tokens[index - 1].type == "paragraph_open":
                paragraphs.append(" ".join("".join(parts).split()))
    if start is not None:
        ranges.append((start, len(content.splitlines())))
    return ranges, paragraphs


class ThreatModelingProseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = LEDGER.read_text(encoding="utf-8")

    def assert_contract(
        self, content: str, title: str, required: tuple[str, ...], forbidden: tuple[str, ...]
    ) -> None:
        ranges, paragraphs = section_prose(content, title)
        self.assertEqual(len(ranges), 1, f"Require one active root section: {title}")
        for phrase in required:
            # Constants preserve the source spelling for mutation tests.
            visible = phrase.replace("**", "").replace("`", "")
            self.assertTrue(any(visible in paragraph for paragraph in paragraphs), phrase)
        for phrase in forbidden:
            self.assertFalse(any(phrase in paragraph for paragraph in paragraphs), phrase)

    def source_section(self, title: str) -> tuple[str, str, str]:
        ranges, _ = section_prose(self.ledger, title)
        self.assertEqual(len(ranges), 1, title)
        start, end = ranges[0]
        lines = self.ledger.splitlines(keepends=True)
        return "".join(lines[:start]), "".join(lines[start:end]), "".join(lines[end:])

    def test_published_contracts(self) -> None:
        for title, required, forbidden in CONTRACTS:
            with self.subTest(section=title):
                self.assert_contract(self.ledger, title, required, forbidden)

    def test_inactive_duplicate_and_wrong_section_examples(self) -> None:
        for title, required, forbidden in CONTRACTS:
            prefix, section, suffix = self.source_section(title)
            hidden = (
                f"<!--\n{section}\n-->\n",
                f"```markdown\n{section}\n```\n",
                f"<pre>\n{section}\n</pre>\n",
                "\n".join("> " + line for line in section.splitlines()) + "\n",
            )
            for index, example in enumerate(hidden):
                with self.subTest(section=title, example=index):
                    with self.assertRaises(AssertionError):
                        self.assert_contract(prefix + example + suffix, title, required, forbidden)
                    # An inert lookalike must not count as a duplicate active heading.
                    self.assert_contract(prefix + example + "\n" + section + suffix, title, required, forbidden)
            for invalid in (
                prefix + section + "\n" + section + suffix,
                prefix + f"## {title}\n\n## Example\n" + section.split("\n", 1)[1] + suffix,
            ):
                with self.subTest(section=title), self.assertRaises(AssertionError):
                    self.assert_contract(invalid, title, required, forbidden)

    def test_every_required_clause_rejects_loss_or_example_only_text(self) -> None:
        for title, required, forbidden in CONTRACTS:
            prefix, section, suffix = self.source_section(title)
            for phrase in required:
                pattern = re.compile(r"\s+".join(re.escape(word) for word in phrase.split()))
                altered, removed = pattern.subn("", section)
                with self.subTest(section=title, phrase=phrase):
                    self.assertGreater(removed, 0, "Mutation must change the published section")
                    for replacement in ("", f"\n\n<!-- {phrase} -->\n", f"\n\n```text\n{phrase}\n```\n"):
                        with self.assertRaises(AssertionError):
                            self.assert_contract(prefix + altered + replacement + suffix, title, required, forbidden)

    def test_visible_section_ranges_ignore_inert_duplicates(self) -> None:
        title, _, _ = CONTRACTS[0]
        visible = f"## {title}\n\nReal instruction.\n\n"
        hidden = f"<!--\n{visible}-->\n\n"
        content = hidden + visible + "## Next section\n"
        ranges, paragraphs = section_prose(content, title)
        self.assertEqual(ranges, [(len(hidden.splitlines()), len((hidden + visible).splitlines()))])
        self.assertEqual(paragraphs, ["Real instruction."])

    def test_literal_or_separate_paragraphs_cannot_supply_an_instruction(self) -> None:
        title = "Example"
        required = ("task-scoped authority",)
        for body in ("`task-scoped authority`", "task-scoped\n\nauthority", "> task-scoped authority"):
            with self.subTest(body=body), self.assertRaises(AssertionError):
                self.assert_contract(f"## {title}\n\n{body}\n", title, required, ())
        self.assert_contract(f"## {title}\n\n- **task-scoped**\n  authority\n", title, required, ())

    def test_forbidden_inference_role_conflation_is_rejected(self) -> None:
        title, required, forbidden = CONTRACTS[0]
        prefix, section, suffix = self.source_section(title)
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                with self.assertRaises(AssertionError):
                    self.assert_contract(prefix + section + "\n\n" + phrase + "\n" + suffix, title, required, forbidden)


if __name__ == "__main__":
    unittest.main()
