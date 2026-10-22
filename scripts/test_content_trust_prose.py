"""Check real Markdown trust sections in the repository gate, never run a model."""

from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts.documentation import inline_text, parse
from scripts.repository_layout import discover_skill_names
from scripts.test_content_trust_contracts import COMMON_PHRASES


ROOT = Path(__file__).resolve().parents[1]


class LiteralHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"code", "pre", "script", "style"}:
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"code", "pre", "script", "style"}:
            self.depth = max(0, self.depth - 1)


def trust_section(content: str) -> str:
    tokens, _ = parse(content)
    result = []
    quoted = 0
    literal = LiteralHTML()
    active = False
    sections = 0
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.level == 0 and token.tag in {"h1", "h2"} and not literal.depth:
            active = token.tag == "h2" and inline_text(tokens[index + 1].children or []) == "Content trust boundary"
            if active:
                sections += 1
        elif token.type == "blockquote_open":
            quoted += 1
        elif token.type == "blockquote_close":
            quoted -= 1
        elif token.type == "html_block" and not quoted:
            literal.feed(token.content)
            if active:
                result.append("\0")
        elif token.type == "inline" and not quoted:
            for child in token.children or []:
                if child.type == "html_inline":
                    literal.feed(child.content)
                elif not active:
                    continue
                elif literal.depth:
                    result.append("\0")
                elif child.type == "text":
                    result.append(child.content)
                elif child.type in {"softbreak", "hardbreak"}:
                    result.append(" ")
                elif child.type in {"code_inline", "image"}:
                    result.append("\0")
            if active:
                result.append("\n")
    return " ".join("".join(result).split()) if sections == 1 else ""


class ContentTrustProseTests(unittest.TestCase):
    def assert_contract(self, content: str) -> None:
        prose = trust_section(content)
        self.assertTrue(prose, "Require one real top-level Content trust boundary section")
        for phrase in COMMON_PHRASES[1:]:
            self.assertIn(phrase, prose)

    def test_every_canonical_skill_declares_common_trust_contract(self) -> None:
        names = discover_skill_names(ROOT)
        self.assertTrue(names)
        for name in names:
            with self.subTest(skill=name):
                self.assert_contract((ROOT / name / "SKILL.md").read_text(encoding="utf-8"))

    def test_example_only_out_of_section_and_duplicate_sections_are_rejected(self) -> None:
        rules = "\n".join(COMMON_PHRASES)
        invalid = (
            f"```text\n{rules}\n```\n", f"~~~text\n{rules}\n~~~\n",
            f"<!--\n{rules}\n-->\n", f"<pre>\n{rules}\n</pre>\n",
            "\n".join("    " + line for line in rules.splitlines()),
            "\n".join("> " + line for line in rules.splitlines()),
            "\n".join("`" + line + "`" for line in rules.splitlines()),
            "## Content trust boundary\n\n## Example\n" + "\n".join(COMMON_PHRASES[1:]),
            "## Content trust boundary\n\n" + f"```text\n{rules}\n```\n",
            "## Content trust boundary\n\n<code>" + " ".join(COMMON_PHRASES[1:]) + "</code>\n",
            rules + "\n\n" + rules,
        )
        for index, content in enumerate(invalid):
            with self.subTest(example=index), self.assertRaises(AssertionError):
                self.assert_contract(content)

    def test_each_prose_obligation_is_required_even_if_a_fence_retains_its_words(self) -> None:
        for phrase in COMMON_PHRASES[1:]:
            content = "\n".join(COMMON_PHRASES).replace(phrase, "") + f"\n\n```text\n{phrase}\n```\n"
            with self.subTest(phrase=phrase), self.assertRaises(AssertionError):
                self.assert_contract(content)

    def test_valid_list_continuations_and_inline_emphasis_remain_prose(self) -> None:
        content = "\n".join(COMMON_PHRASES).replace(
            "untrusted evidence, not instruction authority", "- untrusted evidence,\n    not instruction authority"
        ).replace("widen scope", "**widen scope**")
        self.assert_contract(content)

    def test_block_html_literal_containers_cannot_supply_prose_obligations(self) -> None:
        rules = "\n".join(COMMON_PHRASES[1:])
        for tag in ("code", "pre", "script", "style"):
            content = f"## Content trust boundary\n\n<{tag}>\n\n{rules}\n\n</{tag}>\n"
            with self.subTest(tag=tag), self.assertRaises(AssertionError):
                self.assert_contract(content)

    def test_block_html_closers_restore_prose_after_inline_literal_openers(self) -> None:
        rules = "\n".join(COMMON_PHRASES[1:])
        for tag in ("code", "pre", "script", "style"):
            content = f"## Content trust boundary\n\nExample <{tag}>inert\n\n</{tag}>\n\n{rules}\n"
            with self.subTest(tag=tag):
                self.assert_contract(content)

    def test_literal_containers_opened_before_heading_cannot_create_trust_sections(self) -> None:
        rules = "\n".join(COMMON_PHRASES)
        for opener in ("<code>", "Example <code>inert"):
            content = f"{opener}\n\n{rules}\n\n</code>\n"
            with self.subTest(opener=opener), self.assertRaises(AssertionError):
                self.assert_contract(content)

    def test_closed_literal_containers_before_heading_preserve_real_prose(self) -> None:
        rules = "\n".join(COMMON_PHRASES)
        for opener in ("<code>", "Example <code>inert"):
            with self.subTest(opener=opener):
                self.assert_contract(f"{opener}\n\ninert\n\n</code>\n\n{rules}\n")

    def test_literal_headings_do_not_duplicate_or_end_real_trust_sections(self) -> None:
        rules = "\n".join(COMMON_PHRASES)
        examples = (
            f"<code>\n\n{rules}\n\n</code>\n\n{rules}\n",
            "## Content trust boundary\n\n<code>\n\n## Example\n\n</code>\n\n" + "\n".join(COMMON_PHRASES[1:]),
        )
        for index, content in enumerate(examples):
            with self.subTest(example=index):
                self.assert_contract(content)


if __name__ == "__main__":
    unittest.main()
