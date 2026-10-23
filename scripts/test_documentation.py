"""Deterministic documentation links, anchors, inventories, and source boundaries."""

from __future__ import annotations

import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest import mock

from scripts.documentation import anchors, bare_reference_text, validate_documentation


class DocumentationTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def errors(self, *paths: Path, names: tuple[str, ...] = ()) -> list[str]:
        return [message for _, message in validate_documentation(self.root, list(paths), names)]

    def write_inventories(
        self,
        *,
        choose: str = "[Sample](sample/SKILL.md)",
        available: str = "### sample",
        layout: str = "```text\nsample/\n```",
        sources: str = "- `sample/`",
    ) -> tuple[Path, Path]:
        self.write("sample/SKILL.md", "# Sample\n")
        readme = self.write(
            "README.md",
            f"## Choose a skill\n\n{choose}\n\n## Available Skills\n\n{available}\n\n"
            f"## Skill Structure\n\nCurrent layout:\n\n{layout}\n",
        )
        contributor = self.write("CONTRIBUTING.md", f"## Source of Truth\n\n{sources}\n")
        return readme, contributor

    def test_relative_encoded_reference_and_fragment_links_pass(self) -> None:
        source = self.write("docs/source.md", '[One](../target%20file.md#some-code)\n[Two][ref]\n\n[ref]: <../target file.md#some-code-1>\n[Local](#local)\n\n# Local\n')
        self.write("target file.md", "# Some `code`\n\n# Some code\n")
        self.assertEqual(self.errors(source), [])

    def test_missing_file_anchor_and_escaping_link_are_reported(self) -> None:
        source = self.write("docs/source.md", "[File](missing.md)\n[Anchor](target.md#missing)\n[Escape](../../outside.md)\n")
        self.write("docs/target.md", "# Existing\n")
        errors = self.errors(source)
        self.assertEqual(len(errors), 3)
        self.assertIn("target does not exist", errors[0])
        self.assertIn("heading anchor does not exist", errors[1])
        self.assertIn("must stay below the repository", errors[2])

    def test_fenced_inline_code_frontmatter_and_external_links_are_excluded(self) -> None:
        source = self.write("source.md", '---\nexample: "[data](missing.md)"\n---\n\n~~~markdown\n[example](missing.md)\n~~~\n`[code](missing.md)`\n[web](https://example.invalid/page#missing)\n')
        self.assertEqual(self.errors(source), [])

    def test_duplicate_headings_setext_and_explicit_html_anchors(self) -> None:
        self.assertEqual(anchors('# A!\n# A\n# A-1\n# A\n\nSetext\n======\n\n<a id="manual"></a>\n'),
                         {"a", "a-1", "a-1-1", "a-2", "setext", "manual"})

    def test_non_anchor_name_attributes_are_not_fragment_targets(self) -> None:
        for element in (
            '<div name="claimed-target"></div>', '<input name="claimed-target">',
            '<meta name="claimed-target" content="fixture">', '<form name="claimed-target"></form>',
        ):
            with self.subTest(element=element):
                content = element + '\n\n[Go](#claimed-target)\n'
                source = self.write("source.md", content)
                self.assertNotIn("claimed-target", anchors(content))
                errors = self.errors(source)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("heading anchor does not exist", errors[0])

    def test_html_ids_and_legacy_anchor_names_are_fragment_targets(self) -> None:
        for element in (
            '<div id="claimed-target"></div>', '<input id="claimed-target" name="not-an-anchor" />',
            '<a name="claimed-target"></a>', '<A NAME="claimed-target"></A>',
        ):
            with self.subTest(element=element):
                content = element + '\n\n[Go](#claimed-target)\n'
                source = self.write("source.md", content)
                self.assertEqual(anchors(content), {"claimed-target"})
                self.assertEqual(self.errors(source), [])
        source = self.write("source.md", '<a id="by-id" name="by-name"></a>\n\n[ID](#by-id) [Name](#by-name)\n')
        self.assertEqual(self.errors(source), [])

    def test_legacy_html_parser_excludes_rcdata_contents_but_keeps_real_anchors(self) -> None:
        with mock.patch.object(HTMLParser, "RCDATA_CONTENT_ELEMENTS", (), create=True):
            for tag in ("textarea", "title"):
                with self.subTest(tag=tag):
                    content = (
                        f'<{tag} id="container">\n<a id="example-only"></a>\n</{tag}>\n\n'
                        '<a id="after"></a>\n\n[Container](#container) [After](#after) [Missing](#example-only)\n'
                    )
                    source = self.write("source.md", content)
                    self.assertEqual(anchors(content), {"container", "after"})
                    errors = self.errors(source)
                    self.assertEqual(len(errors), 1, errors)
                    self.assertIn("heading anchor does not exist", errors[0])

    def test_rcdata_headings_cannot_become_fragment_targets(self) -> None:
        with mock.patch.object(HTMLParser, "RCDATA_CONTENT_ELEMENTS", (), create=True):
            for tag in ("textarea", "title"):
                for prefix in ("", "Example "):
                    with self.subTest(tag=tag, prefix=prefix):
                        content = f'{prefix}<{tag}>\n\n# Example only\n\n</{tag}>\n\n# After\n'
                        self.assertEqual(anchors(content), {"after"})

    def test_balanced_parentheses_and_reference_heading_labels(self) -> None:
        source = self.write("source.md", '[Design](design(v2).md#guide)\n')
        self.write("design(v2).md", '# [Guide][ref]\n\n[ref]: https://example.invalid\n')
        self.assertEqual(self.errors(source), [])
        self.assertEqual(anchors('# [Guide][ref]\n\n[ref]: https://example.invalid\n'), {"guide"})

    def test_indented_escaped_nested_and_commented_examples_are_not_links(self) -> None:
        source = self.write("source.md", '    [Indented](missing.md)\n\n\\[Escaped](missing.md)\n\n<!-- [Comment](missing.md) -->\n\n- Example:\n\n    ```markdown\n    [Nested fence](missing.md)\n    ```\n')
        self.assertEqual(self.errors(source), [])

    def test_unclosed_frontmatter_and_nonmapping_thematic_breaks_do_not_hide_links(self) -> None:
        for content in ('---\n\n# Guide\n[Broken](missing.md)\n',
                        '---\n\n# Guide\n---\n[Broken](missing.md)\n'):
            with self.subTest(content=content):
                source = self.write("source.md", content)
                self.assertTrue(any("missing.md" in error for error in self.errors(source)))

    def test_comment_and_code_only_headings_and_html_anchors_are_not_targets(self) -> None:
        source = self.write("source.md", '<!--\n# Hidden\n<a id="hidden-id"></a>\n-->\n\n```markdown\n# Code\n```\n\n[Hidden](#hidden)\n[Commented anchor](#hidden-id)\n[Code](#code)\n')
        self.assertEqual(len(self.errors(source)), 3)

    def test_unused_reference_definitions_are_validated(self) -> None:
        source = self.write("source.md", '[unused]: missing.md\n')
        self.assertIn("missing.md", self.errors(source)[0])

    def test_reopened_comments_hide_anchors_links_and_reference_definitions(self) -> None:
        hidden = '# Hidden\n\n[Hidden](missing.md)\n\n[unused]: missing-reference.md\n'
        for opening in ('<!-- closed --> <!--', '<!-- first\n--> <!-- second'):
            for closing in ('', '\n-->\n\n# Visible\n\n[Visible](#visible)\n'):
                with self.subTest(opening=opening, closing=closing):
                    content = opening + '\n\n' + hidden + closing
                    source = self.write("source.md", content)
                    self.assertEqual(anchors(content), {"visible"} if closing else set())
                    self.assertEqual(self.errors(source), [])
                    if closing:
                        source.write_text(content + '\n[Hidden](#hidden)\n', encoding="utf-8")
                        self.assertIn("heading anchor does not exist", self.errors(source)[0])
        # Literal references remain checked even inside an example comment.
        self.assertIn('references/hidden.md', bare_reference_text(
            '<!-- closed --> <!--\n\nreferences/hidden.md\n\n-->\n',
        ))

    def test_reopened_comments_preserve_visible_prefix_and_literal_tails(self) -> None:
        for tail in ('`<!--`', r'\<!--', '`<pre>`', r'\<pre>', '`<!--\ncontinued`'):
            with self.subTest(tail=tail):
                content = ('<!-- closed --> <a id="before"></a> <!--\n\n# Hidden\n\n'
                           f'--> {tail}\n\n# After\n')
                self.assertEqual(anchors(content), {"before", "after"})

    def test_hidden_reference_definitions_cannot_override_visible_links(self) -> None:
        source = self.write("source.md", '<!-- closed --> <!--\n\n[guide]: missing.md\n\n-->\n\n'
                            '[Guide][guide]\n\n[guide]: real.md#real\n')
        self.write("real.md", "# Real\n")
        self.assertEqual(self.errors(source), [])

    def test_reopened_comments_in_quotes_do_not_hide_following_document(self) -> None:
        for closing in ('', '>\n> --> `<!--`\n'):
            with self.subTest(closing=closing):
                source = self.write("source.md", '> <!-- closed --> <!--\n>\n> # Hidden\n>\n'
                                    '> [Hidden](missing.md)\n' + closing + '\n# Visible\n\n[Visible](#visible)\n')
                self.assertEqual(anchors(source.read_text(encoding="utf-8")), {"visible"})
                self.assertEqual(self.errors(source), [])

    def test_linked_target_is_rejected_without_reading_external_content(self) -> None:
        target = self.write("target.md", "# Target\n")
        link = self.root / "link.md"
        try:
            link.symlink_to(target)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        source = self.write("source.md", "[Linked](link.md#target)\n")
        self.assertIn("symlink or junction", self.errors(source)[0])

    def test_all_readme_and_contributor_inventories_match_discovery(self) -> None:
        readme, contributor = self.write_inventories()
        self.assertEqual(self.errors(readme, contributor, names=("sample",)), [])
        original = readme.read_text(encoding="utf-8")
        for removed in ("[Sample](sample/SKILL.md)", "### sample", "sample/\n"):
            with self.subTest(inventory=removed):
                readme.write_text(original.replace(removed, ""), encoding="utf-8")
                self.assertTrue(any("inventory" in error for error in self.errors(readme, names=("sample",))))
        readme.write_text(original, encoding="utf-8")
        contributor.write_text("## Source of Truth\n\n- `sample/`\n- `sample/`\n- `extra/`\n", encoding="utf-8")
        errors = self.errors(contributor, names=("sample",))
        self.assertTrue(any("duplicates=['sample']" in error and "extra=['extra']" in error for error in errors))

    def test_inventory_examples_cannot_replace_real_entries(self) -> None:
        entries = {
            "choose": ("Choose a skill", "[Sample](sample/SKILL.md)"),
            "available": ("Available Skills", "### sample"),
            "sources": ("Source of Truth", "- `sample/`"),
        }
        for key, (label, entry) in entries.items():
            for opening, closing in (("<!--", "-->"), ("```markdown", "```"), ("~~~markdown", "~~~")):
                with self.subTest(inventory=label, wrapper=opening):
                    paths = self.write_inventories(**{key: f"{opening}\n{entry}\n{closing}"})
                    errors = self.errors(*paths, names=("sample",))
                    self.assertTrue(any(f"{label} inventory" in error and "missing=['sample']" in error for error in errors))
        paths = self.write_inventories(layout="<!--\n```text\nsample/\n```\n-->")
        self.assertTrue(any("Current layout inventory" in error for error in self.errors(*paths, names=("sample",))))

    def test_reference_links_and_rendered_headings_are_inventory_entries(self) -> None:
        readme, contributor = self.write_inventories(
            choose="[Sample][skill-ref]",
            available="### **sample**",
            sources="1. **`sample/`** supporting resources",
        )
        readme.write_text(
            readme.read_text(encoding="utf-8") + "\n## References\n\n[skill-ref]: <./sample/SKILL.md#sample>\n",
            encoding="utf-8",
        )
        self.assertEqual(self.errors(readme, contributor, names=("sample",)), [])

    def test_reopened_comments_cannot_replace_or_duplicate_catalog_entries(self) -> None:
        entries = {"choose": '[Sample](sample/SKILL.md)', "available": '### sample',
                   "layout": '```text\nsample/\n```', "sources": '- `sample/`'}
        for key, entry in entries.items():
            hidden = '<!-- closed --> <!--\n\n' + entry + '\n\n-->\n\n'
            with self.subTest(inventory=key):
                paths = self.write_inventories(**{key: hidden})
                self.assertTrue(any("missing=['sample']" in error
                                    for error in self.errors(*paths, names=("sample",))))
                paths = self.write_inventories(**{key: hidden + entry})
                self.assertEqual(self.errors(*paths, names=("sample",)), [])

    def test_parsed_inventory_duplicates_are_still_rejected(self) -> None:
        duplicates = {
            "choose": ("Choose a skill", "[One](sample/SKILL.md)\n[Two][alias]\n\n[alias]: sample/SKILL.md"),
            "available": ("Available Skills", "### sample\n\n### `sample`"),
            "sources": ("Source of Truth", "- `sample/`\n- `sample/`"),
        }
        for key, (label, entries) in duplicates.items():
            with self.subTest(inventory=label):
                paths = self.write_inventories(**{key: entries})
                errors = self.errors(*paths, names=("sample",))
                self.assertTrue(any(f"{label} inventory" in error and "duplicates=['sample']" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
