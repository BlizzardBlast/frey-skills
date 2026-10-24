"""Deterministic documentation links, anchors, inventories, and source boundaries."""

from __future__ import annotations

import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest import mock

from scripts.documentation import LiteralHTML, anchors, bare_reference_text, links, validate_documentation


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

    def test_inline_html_heading_text_preserves_slugs_and_duplicate_suffixes(self) -> None:
        for tag in ('code', 'pre'):
            for heading in (f'# Use <{tag}>debug</{tag}>', f'## Use <{tag}>debug</{tag}> ##',
                            f'Use <{tag}>debug</{tag}>\n==='):
                with self.subTest(heading=heading):
                    content = (heading + '\n\n# Use debug\n\n# Use `debug`\n\n# Use **debug**\n\n'
                               '[One](#use-debug) [Two](#use-debug-1) '
                               '[Three](#use-debug-2) [Four](#use-debug-3)\n')
                    self.assertEqual(anchors(content), {'use-debug', 'use-debug-1', 'use-debug-2', 'use-debug-3'})
                    self.assertEqual(self.errors(self.write('source.md', content)), [])

    def test_inline_html_heading_labels_resolve_only_visible_definitions(self) -> None:
        self.write('real.md', '# Real\n')
        hidden = 'Example <title>\n\n[ref]: missing.md\n\n</title>\n\n'
        for definition, slug in (('', 'use-debugref'), ('\n\n[ref]: real.md\n', 'use-debug')):
            with self.subTest(definition=definition):
                content = hidden + f'# [Use <code>debug</code>][ref]\n\n[Self](#{slug})\n' + definition
                self.assertEqual(anchors(content), {slug})
                self.assertEqual(self.errors(self.write('source.md', content)), [])

    def test_quoted_raw_html_keeps_following_headings_and_explicit_anchors(self) -> None:
        for tag in ('script', 'style', 'textarea', 'title'):
            for quote, following in (('> ', ''), ('> > ', ''), ('> > ', '> ')):
                with self.subTest(tag=tag, quote=quote, following=following):
                    example = '\n'.join(quote + line for line in (
                        f'<{tag} id="container">', '', '# Hidden', '', '<a id="example-only"></a>',
                    ))
                    after = '\n'.join(following + line for line in (
                        '# Visible', '', '<a id="after" name="legacy"></a>', '', '# Visible', '',
                        '[One](#visible) [Two](#visible-1) [ID](#after) [Name](#legacy) [Container](#container)',
                    ))
                    content = example + '\n' + following + '\n' + after + '\n'
                    self.assertEqual(anchors(content), {'container', 'visible', 'visible-1', 'after', 'legacy'})
                    self.assertEqual(self.errors(self.write('source.md', content)), [])
        self.assertEqual(anchors('> <a id="visible"></a>\n\n# Visible\n\n# Visible\n'),
                         {'visible', 'visible-1'})

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

    def test_attribute_markers_do_not_move_real_comment_openers(self) -> None:
        elements = (
            '<a id="before" title="<!--"></a>', '<a title="<!--" id="before"></a>',
            "<a id='before' title='<!--'></a>", "<a title='<!--' id='before'></a>",
            '<div id="before" title="<!--">Example</div>',
            '<a title="first\n<!--" id="before"></a>',
        )
        for element in elements:
            for quote in ('', '> ', '> > '):
                with self.subTest(element=element, quote=quote):
                    example = (f'<!-- closed --> {element} <!-- actual\n\n# Hidden\n\n'
                               '[Hidden](missing.md)\n\n[unused]: missing.md\n\n-->')
                    content = '\n'.join(quote + line for line in example.splitlines())
                    content += '\n\n# After\n\n[Before](#before) [After](#after)\n'
                    self.assertEqual(anchors(content), {'before', 'after'})
                    self.assertEqual(self.errors(self.write('source.md', content)), [])

    def test_visible_fragments_between_successive_comments_are_preserved(self) -> None:
        for quote in ('', '> ', '> > '):
            for reopen in ('<!-- next', '<!-- complete --> <!-- next'):
                with self.subTest(quote=quote, reopen=reopen):
                    content = '<!-- closed --> <!-- first\n\n# Hidden\n\n[hidden]: missing.md\n\n'
                    for name in ('middle', 'last'):
                        content += (f'<!-- finish --> <a id="{name}" title="<!--"></a> '
                                    f'[Visible](#{name}) {reopen}\n\n[Hidden](missing.md)\n\n')
                    content += '-->'
                    content = '\n'.join(quote + line for line in content.splitlines())
                    content += '\n\n# After\n\n[Middle](#middle) [Last](#last)\n'
                    self.assertEqual(anchors(content), {'middle', 'last', 'after'})
                    self.assertEqual(self.errors(self.write('source.md', content)), [])
                    self.assertIn('missing.md', bare_reference_text(content))

    def test_catalog_links_between_comments_stay_visible(self) -> None:
        choose = ('<!-- closed --> <!-- first\n\n[Hidden](missing.md)\n\n'
                  '--> [Sample](sample/SKILL.md) <!-- next\n\n[Hidden](missing.md)\n\n-->')
        paths = self.write_inventories(choose=choose)
        self.assertEqual(self.errors(*paths, names=('sample',)), [])

    def test_comment_tail_analysis_uses_full_document_reference_context(self) -> None:
        self.write('real.png', 'fixture\n')
        body = ('<!-- closed --> <!-- first\n\n[image]: missing.png\n\n'
                '--> ![<!--][image]\n\n# After\n\n[After](#after)\n')
        definition = '[image]: real.png\n\n'
        for content in (definition + body, body + '\n' + definition):
            with self.subTest(content=content):
                self.assertEqual(anchors(content), {'after'})
                self.assertEqual(self.errors(self.write('source.md', content)), [])

    def test_inert_markers_before_real_reopeners_keep_visible_content(self) -> None:
        self.write('real.png', 'fixture\n')
        for marker in ('`<!--`', r'\<!--', '&lt;!--', '![<!--](real.png)',
                       '<code><!-- literal</code>', '<title><!-- literal</title>', '`<!--\ncontinued`'):
            with self.subTest(marker=marker):
                content = ('<!-- closed --> <!-- first\n\nHidden\n\n'
                           f'--> {marker} <a id="middle"></a> <!-- actual\n\n'
                           '[Hidden](missing.md)\n\n-->\n\n# After\n')
                self.assertEqual(anchors(content), {'middle', 'after'})
                self.assertEqual(self.errors(self.write('source.md', content)), [])

    def test_hidden_definitions_cannot_change_comment_tail_visibility(self) -> None:
        body = ('<!-- closed --> <!-- first\n\nHidden\n\n--> ![<!--][image]\n\n'
                '# Hidden\n\n[Hidden](missing.md)\n\n-->\n\n# After\n')
        self.write('real.png', 'fixture\n')
        definitions = [f'Example <{tag}>\n\n[image]: real.png\n\n</{tag}>\n\n'
                       for tag in ('code', 'pre', 'script', 'style', 'textarea', 'title')]
        definitions.append('<!-- closed --> <!-- next\n\n[image]: real.png\n\n-->\n\n')
        for definition in definitions:
            for content in (definition + body, body + '\n' + definition):
                for quote in ('', '> ', '> > '):
                    with self.subTest(definition=definition, content=content, quote=quote):
                        source = '\n'.join(quote + line for line in content.splitlines()) + '\n'
                        self.assertEqual(anchors(source), {'after'})
                        self.assertEqual(self.errors(self.write('source.md', source)), [])
        self.assertEqual(anchors('[image]: real.png\n\n' + body), {'hidden', 'after'})

    def test_comments_in_literal_html_preserve_following_content(self) -> None:
        self.write('real.md', '# Real\n')
        comments = ('<!-- first --> <!-- second -->', '`<!--` and ' + r'\<!--',
                    '<!-- first --> <!-- second\n\nHidden\n\n-->',
                    '<!-- first --> <!-- second\n\nHidden\n\n--> <!-- third\n\nHidden\n\n-->')
        for tag in ('code', 'pre', 'script', 'style', 'textarea', 'title'):
            for prefix in ('', 'Example '):
                for comment in comments:
                    for quote in ('', '> ', '> > '):
                        with self.subTest(tag=tag, prefix=prefix, comment=comment, quote=quote):
                            content = (f'{prefix}<{tag} id="container">\n\n{comment}\n\n'
                                       f'[Hidden](missing.md)\n\n</{tag}>\n\n# After\n\n'
                                       '<a id="after-html" name="legacy"></a>\n\n[Visible](real.md#real)\n')
                            content = '\n'.join(quote + line for line in content.splitlines()) + '\n'
                            # Raw pre blocks do not interpret Markdown escapes or code spans.
                            expected = {'container'} if tag == 'pre' and not prefix and comment == comments[1] else {
                                'container', 'after', 'after-html', 'legacy'
                            }
                            self.assertEqual(anchors(content), expected)
                            self.assertEqual(self.errors(self.write('source.md', content)), [])

    def test_literal_comment_tails_preserve_same_line_container_closers(self) -> None:
        for tag in ('code', 'pre', 'script', 'style', 'textarea', 'title'):
            for gap in (' ', '    '):
                with self.subTest(tag=tag, gap=gap):
                    content = (f'Example <{tag}>\n\n<!-- first --> <!-- second\n\nHidden\n\n'
                               f'-->{gap}</{tag}>\n\n# After\n')
                    self.assertEqual(anchors(content), {'after'})
        for quote in ('', '> ', '> > '):
            content = ('Example <code>\n\n<!-- first --> <!-- second\n\nHidden\n\n'
                       '    -->    </code>\n\n# After\n')
            content = '\n'.join(quote + line for line in content.splitlines()) + '\n'
            self.assertEqual(anchors(content), {'after'})

    def test_literal_html_state_is_current_after_short_closing_chunks(self) -> None:
        for tag in ('code', 'pre', 'script', 'style', 'textarea', 'title'):
            with self.subTest(tag=tag):
                literal = LiteralHTML()
                literal.feed(f'<{tag}>')
                literal.feed('<!-- ' + 'inert ' * 100 + '-->')
                literal.feed(f'</{tag}>')
                self.assertEqual(literal.tags, [])
        literal = LiteralHTML()
        for fragment in ('<code>', '<!-- pending', '</code>'):
            literal.feed(fragment)
        self.assertEqual(literal.tags, ['code'])
        literal.feed('-->')
        literal.feed('</code>')
        self.assertEqual(literal.tags, [])

    def test_pending_literal_comments_keep_hidden_closers_and_paths_inert(self) -> None:
        opening = 'Example <code>\n\n<!-- first --> <!-- second\n\n'
        hidden = '</code>\n\n# Hidden\n\n[Hidden](references/hidden.md)\n\n'
        self.assertEqual(anchors(opening + hidden), set())
        content = opening + hidden + '-->\n\n[Still hidden](missing.md)\n\n</code>\n\n# After\n'
        self.assertEqual(anchors(content), {'after'})
        self.assertEqual(self.errors(self.write('source.md', content)), [])
        self.assertIn('references/hidden.md', bare_reference_text(content))

    def test_comments_in_literal_html_preserve_all_genuine_catalog_entries(self) -> None:
        entries = {'choose': '[Sample](sample/SKILL.md)', 'available': '### sample',
                   'layout': '```text\nsample/\n```', 'sources': '- `sample/`'}
        for key, entry in entries.items():
            for tag in ('code', 'pre', 'script', 'style', 'textarea', 'title'):
                for prefix in ('', 'Example '):
                    with self.subTest(key=key, tag=tag, prefix=prefix):
                        example = (f'{prefix}<{tag}>\n\n<!-- first --> <!-- second\n\nHidden\n\n-->'
                                   f'\n\n{entry}\n\n</{tag}>\n\n')
                        paths = self.write_inventories(**{key: example + entry})
                        self.assertEqual(self.errors(*paths, names=('sample',)), [])

    def test_hidden_definitions_cannot_change_literal_container_visibility(self) -> None:
        definition = 'Example <code>\n\n[image]: real.png\n\n</code>\n\n'
        self.write('real.png', 'fixture\n')
        for tag in ('code', 'pre', 'script', 'style', 'textarea', 'title'):
            body = (f'![<{tag}>][image]\n\n# Hidden\n\n[Hidden](references/hidden.md)\n\n'
                    f'</{tag}>\n\n# After\n')
            for content in (definition + body, body + '\n' + definition):
                with self.subTest(tag=tag, content=content):
                    self.assertEqual(anchors(content), {'after'})
                    self.assertEqual(self.errors(self.write('source.md', content)), [])
                    self.assertIn('references/hidden.md', bare_reference_text(content))
            self.assertEqual([target for target, _ in links('[image]: real.png\n\n' + body)],
                             ['real.png', 'references/hidden.md', 'real.png'])

    def test_hidden_reference_images_cannot_supply_catalog_entries(self) -> None:
        definition = 'Example <code>\n\n[image]: real.png\n\n</code>\n\n'
        entries = {'choose': '[Sample](sample/SKILL.md)', 'available': '### sample',
                   'layout': '```text\nsample/\n```', 'sources': '- `sample/`'}
        for key, entry in entries.items():
            for opening, closing in (('<!-- closed --> <!-- first\n\nHidden\n\n--> ![<!--][image]', '-->'),
                                     ('![<code>][image]', '</code>')):
                hidden = definition + f'{opening}\n\n{entry}\n\n{closing}\n\n'
                with self.subTest(key=key, opening=opening):
                    paths = self.write_inventories(**{key: hidden})
                    self.assertTrue(any("missing=['sample']" in error
                                        for error in self.errors(*paths, names=('sample',))))
                    paths = self.write_inventories(**{key: hidden + entry})
                    self.assertEqual(self.errors(*paths, names=('sample',)), [])

    def test_chained_hidden_definitions_preserve_visible_images_and_path_evidence(self) -> None:
        content = 'Example <code>\n\n[image0]: real.png\n\n</code>\n\n'
        for index in range(3):
            content += f'![<code>][image{index}]\n\n[image{index + 1}]: real.png\n\n</code>\n\n'
        content += ('<!-- closed --> <!-- first\n\nHidden\n\n--> ![<!--][image3]\n\n'
                    '# Hidden\n\n[Hidden](references/hidden.md)\n\n-->\n\n# After\n\n'
                    '![<!--][visible]\n\n[visible]: real.png\n')
        self.assertEqual(anchors(content), {'after'})
        self.assertEqual([target for target, _ in links(content)], ['real.png', 'real.png'])
        self.assertIn('references/hidden.md', bare_reference_text(content))

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

    def test_literal_html_cannot_replace_or_duplicate_catalog_entries(self) -> None:
        entries = {"choose": '[Sample](sample/SKILL.md)', "available": '### sample',
                   "layout": '```text\nsample/\n```', "sources": '- `sample/`'}
        for tag in ("code", "pre", "script", "style", "textarea", "title"):
            for prefix in ("", "Example "):
                for key, entry in entries.items():
                    with self.subTest(tag=tag, prefix=prefix, inventory=key):
                        hidden = f'{prefix}<{tag}>\n\n{entry}\n\n</{tag}>\n\n'
                        paths = self.write_inventories(**{key: hidden})
                        self.assertTrue(any("missing=['sample']" in error
                                            for error in self.errors(*paths, names=("sample",))))
                        paths = self.write_inventories(**{key: hidden + entry})
                        self.assertEqual(self.errors(*paths, names=("sample",)), [])

    def test_literal_html_excludes_links_images_and_reference_definitions(self) -> None:
        self.write("real.md", "# Real\n")
        for tag in ("code", "pre", "script", "style", "textarea", "title"):
            for prefix in ("", "Example "):
                with self.subTest(tag=tag, prefix=prefix):
                    content = (f'{prefix}<{tag} id="container">\n\n'
                               '[Hidden](missing.md) ![Hidden](missing.png)\n\n'
                               '[guide]: missing-reference.md\n\n'
                               f'references/hidden.md\n\n</{tag}>\n\n'
                               '<a id="after"></a>\n\n[Guide][guide]\n\n[guide]: real.md#real\n')
                    source = self.write("source.md", content)
                    self.assertEqual(self.errors(source), [])
                    self.assertEqual(anchors(content), {"container", "after"})
                    self.assertIn("references/hidden.md", bare_reference_text(content))

    def test_inline_literal_html_and_matching_closers_preserve_visible_links(self) -> None:
        for tag in ("code", "pre", "script", "style", "textarea", "title"):
            with self.subTest(tag=tag):
                content = (f'Before [One](one.md) <{tag} id="container">'
                           f'[Hidden](missing.md) ![Hidden](missing.png)</{tag}> '
                           '<a id="after"></a> [Two](two.md)\n')
                self.assertEqual(links(content), [("one.md", 1), ("two.md", 1)])
                self.assertEqual(anchors(content), {"container", "after"})
                heading = (f'# Before <{tag} id="container">Hidden</{tag}> '
                           '<a id="after"></a> After ##\n\n# Genuine\n')
                self.assertTrue({"container", "after", "genuine"}.issubset(anchors(heading)))
        for example in ('`<code>`', r'\<code>', '`<code>\ncontinued`', '<!-- <code> -->'):
            with self.subTest(example=example):
                self.assertEqual(links(example + '\n\n[Visible](real.md)\n'), [("real.md", 4 if '\n' in example else 3)])

    def test_nested_mismatched_and_quoted_literals_keep_their_visibility_scope(self) -> None:
        for opening, misleading in (
            ('Example <code><pre>', '</pre>'),
            ('Example <code><code>', '</code>'),
            ('Example <code>', '</pre>'),
            ('Example <title>', '</code>'),
            ('Example <code>', r'\</code>'),
            ('Example <code>', '`</code>`'),
            ('Example <code>', '```html\n</code>\n```'),
        ):
            with self.subTest(opening=opening, misleading=misleading):
                closing = '</title>' if '<title>' in opening else '</code>'
                content = (f'{opening}\n\n{misleading}\n\n[Hidden](missing.md)\n\n'
                           f'{closing}\n\n[Visible](real.md)\n')
                self.assertEqual([target for target, _ in links(content)], ['real.md'])
        for tag in ("code", "pre", "script", "style", "textarea", "title"):
            with self.subTest(quoted=tag):
                content = f'> Example <{tag}>\n>\n> [Hidden](missing.md)\n\n[Visible](real.md)\n'
                self.assertEqual(links(content), [('real.md', 5)])

    def test_literal_html_source_positions_survive_markdown_prefixes(self) -> None:
        for opening, closing, after in (
            ('# Example <code>', '</code>', '[Visible](real.md)'),
            ('# Example <code> ##', '</code>', '[Visible](real.md)'),
            ('## Example\x00<code> ###', '</code>', '[Visible](real.md)'),
            ('- Example <code>', '  </code>', '[Visible](real.md)'),
            ('-\tExample <code>', '  </code>', '[Visible](real.md)'),
            ('> Example <code>', '> </code>', '> [Visible](real.md)'),
            ('Example <code\n  id="container">', '</code>', '[Visible](real.md)'),
        ):
            with self.subTest(opening=opening):
                hidden = '> [Hidden](missing.md)' if opening.startswith('>') else '[Hidden](missing.md)'
                gap = '\n>\n' if opening.startswith('>') else '\n\n'
                content = gap.join((opening, hidden, closing, after)) + '\n'
                self.assertEqual([target for target, _ in links(content)], ['real.md'])

    def test_comment_line_separators_preserve_link_locations_and_anchors(self) -> None:
        for separator in ('\n', '\r\n', '\r', '\x85', '\f', '\v', '\x1c', '\x1d', '\x1e', '\u2028', '\u2029'):
            with self.subTest(separator=repr(separator)):
                content = (f'<!-- first{separator}line --> <!--\n\n# Hidden\n\n-->\n\n'
                           '# Visible\n\n[Visible](#visible)\n\n[unused]: missing.md\n')
                self.assertEqual(anchors(content), {"visible"})
                self.assertEqual(links(content), [("#visible", 10), ("missing.md", 12)])


if __name__ == "__main__":
    unittest.main()
