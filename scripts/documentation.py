"""Offline local Markdown links, heading anchors, and canonical skill inventories."""

from __future__ import annotations

import os
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt
from markdown_it.token import Token

try:
    from scripts.repository_layout import SourcePathError, validate_source_path
except ModuleNotFoundError:
    from repository_layout import SourcePathError, validate_source_path


def parse(text: str) -> tuple[list[Token], dict[str, Any]]:
    """Parse CommonMark; exclude only closed mapping frontmatter, keeping line maps."""
    lines = text.splitlines()
    frontmatter_text = ""
    if lines and lines[0] == "---":
        for end in range(1, len(lines)):
            if lines[end] != "---":
                continue
            try:
                frontmatter = yaml.safe_load("\n".join(lines[1:end]))
            except yaml.YAMLError:
                frontmatter = None
            if isinstance(frontmatter, dict):
                frontmatter_text = "\n".join(lines[:end + 1])
                lines[:end + 1] = [""] * (end + 1)
            break
    environment: dict[str, Any] = {}
    tokens = MarkdownIt("commonmark").parse("\n".join(lines), environment)
    environment["frontmatter_text"] = frontmatter_text
    return tokens, environment


def inline_text(tokens: list[Token]) -> str:
    """Use rendered label/code text, without destinations, reference labels, or HTML."""
    result = []
    for token in tokens:
        if token.type in {"text", "code_inline"}:
            result.append(token.content)
        elif token.type in {"softbreak", "hardbreak"}:
            result.append(" ")
        elif token.children:
            result.append(inline_text(token.children))
    return "".join(result)


class LiteralHTML(HTMLParser):
    """Track matched literal containers across Markdown token boundaries."""

    # Older Python patch releases lack native RCDATA handling.
    CDATA_CONTENT_ELEMENTS = HTMLParser.CDATA_CONTENT_ELEMENTS + ("textarea", "title")

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"code", "pre", "script", "style", "textarea", "title"}:
            self.tags.append(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.tags) - 1, -1, -1):
            if self.tags[index] == tag:
                del self.tags[index:]
                break


def _has_open_comment(text: str, environment: dict[str, Any]) -> bool:
    parser = MarkdownIt("commonmark")
    # Inline parsing keeps escape tokens separate before the full parser joins text.
    children = parser.inline.parse(text, parser, environment, [])
    literal = LiteralHTML()
    for child in children:
        if child.type == "html_inline":
            literal.feed(child.content)
        elif child.type == "text" and not literal.tags and re.search(r"<!--(?:(?!-->).)*$", child.content, re.DOTALL):
            return True
    return False


def parse_visible(text: str) -> tuple[list[Token], dict[str, Any]]:
    """Exclude reopened HTML comments, preserving source lines and Markdown tails."""
    lines = text.splitlines(keepends=True)
    while True:
        tokens, environment = parse("".join(lines))
        contexts = [(LiteralHTML(), len(lines))]
        for token in tokens:
            if token.type == "blockquote_open":
                contexts.append((LiteralHTML(), token.map[1]))
            elif token.type == "blockquote_close":
                contexts.pop()
            literal, scope_end = contexts[-1]
            if token.type != "html_block":
                for child in token.children or []:
                    if child.type == "html_inline":
                        literal.feed(child.content)
                continue
            literal.feed(token.content)
            if literal.tags or not literal.rawdata.startswith("<!--"):
                continue

            # CommonMark ends an HTML block at its first closer, even when a
            # second comment on that line still hides subsequent Markdown.
            source = "".join(lines[token.map[0]:token.map[1]])
            opening = re.search(r"<!--(?:(?!-->).)*$", source, re.DOTALL)
            assert opening is not None
            prefix = source[:opening.start()]
            start = token.map[0] + prefix.count("\n")
            column = len(prefix.rsplit("\n", 1)[-1])
            end = scope_end
            closing_tail = None
            for closing_line in range(token.map[1], scope_end):
                _, closed, tail = lines[closing_line].partition("-->")
                if not closed:
                    continue
                # Retain quoted context and multiline code spans after closure.
                quote_prefix = re.match(r"^(?:[ \t]*>[ \t]?)*", lines[closing_line])[0]
                tail_source = quote_prefix + "-->" + tail + "".join(lines[closing_line + 1:scope_end])
                tail_tokens, tail_environment = parse(tail_source)
                paragraph = next((item.content for item in tail_tokens if item.type == "inline"), "")
                if not _has_open_comment(paragraph, tail_environment):
                    end = closing_line + 1
                    closing_tail = quote_prefix + "-->" + tail
                    break
            lines[start] = lines[start][:column] + "\n"
            for line in range(start + 1, end):
                quote_prefix = re.match(r"^(?:[ \t]*>[ \t]?)*", lines[line])[0]
                lines[line] = quote_prefix + "\n"
            if closing_tail is not None:
                lines[end - 1] = closing_tail
            # Reparse to resolve reference links against visible definitions only.
            # Each iteration removes a comment opener, so the loop is finite.
            break
        else:
            return tokens, environment


class HTMLAnchors(LiteralHTML):
    def __init__(self) -> None:
        super().__init__()
        self.names: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        super().handle_starttag(tag, attrs)
        self.names.update(
            value for key, value in attrs
            if value is not None and (key == "id" or (tag == "a" and key == "name"))
        )


def anchors(text: str) -> set[str]:
    tokens, _ = parse_visible(text)
    found: set[str] = set()
    explicit = HTMLAnchors()
    counts: Counter[str] = Counter()
    for index, token in enumerate(tokens):
        if token.type == "html_block":
            explicit.feed(token.content)
        for child in token.children or []:
            if child.type == "html_inline":
                explicit.feed(child.content)
        if token.type == "heading_open" and explicit.cdata_elem is None:
            title = inline_text(tokens[index + 1].children or []).lower()
            slug = re.sub(r"\s", "-", re.sub(r"[^\w\-\s]", "", title))
            candidate = slug
            while candidate in found:
                counts[slug] += 1
                candidate = f"{slug}-{counts[slug]}"
            found.add(candidate)
    return found | explicit.names


def section_tokens(text: str, title: str) -> list[Token]:
    """Keep parsed section blocks and reference links resolved against the full document."""
    tokens, _ = parse_visible(text)
    start = None
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or token.level != 0 or token.tag not in {"h1", "h2"}:
            continue
        if start is not None:
            return tokens[start:index]
        if token.tag == "h2" and inline_text(tokens[index + 1].children or []) == title:
            start = index + 3  # Skip heading_open, inline, and heading_close.
    return tokens[start:] if start is not None else []


def linked_skills(tokens: list[Token]) -> list[str]:
    names = []
    for token in tokens:
        for child in token.children or []:
            if child.type != "link_open":
                continue
            try:
                target = urlsplit(child.attrGet("href") or "")
            except ValueError:
                continue  # Link validation reports malformed destinations separately.
            if target.scheme or target.netloc:
                continue
            match = re.fullmatch(r"(?:\./)?([a-z0-9-]+)/SKILL\.md", unquote(target.path))
            if match:
                names.append(match.group(1))
    return names


def heading_skills(tokens: list[Token]) -> list[str]:
    names = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.level == 0 and token.tag == "h3":
            title = inline_text(tokens[index + 1].children or [])
            if re.fullmatch(r"[a-z0-9-]+", title):
                names.append(title)
    return names


def listed_directories(tokens: list[Token]) -> list[str]:
    names = []
    for index, token in enumerate(tokens):
        if token.type != "list_item_open":
            continue
        following = tokens[index + 1:index + 3]
        if len(following) != 2 or following[0].type != "paragraph_open" or following[1].type != "inline":
            continue
        first = next((child for child in following[1].children or []
                      if child.type in {"text", "code_inline"} and child.content.strip()), None)
        if first is not None and first.type == "code_inline":
            match = re.fullmatch(r"([a-z0-9-]+)/", first.content)
            if match:
                names.append(match.group(1))
    return names


def layout_directories(tokens: list[Token]) -> list[str]:
    return [name for token in tokens if token.type in {"fence", "code_block", "inline"}
            for name in re.findall(r"^([a-z0-9-]+)/\s*$", token.content, re.MULTILINE)]


def links(text: str) -> list[tuple[str, int]]:
    tokens, environment = parse_visible(text)
    found = []
    for token in tokens:
        line = token.map[0] + 1 if token.map else 1
        pending = list(reversed(token.children or []))
        while pending:
            child = pending.pop()
            if child.type in {"link_open", "image"}:
                destination = child.attrGet("href" if child.type == "link_open" else "src")
                if destination is not None:
                    found.append((destination, line))
            pending.extend(reversed(child.children or []))
    # Keep validating unused definitions, which have no rendered link tokens.
    for reference in environment.get("references", {}).values():
        found.append((reference["href"], reference["map"][0] + 1))
    return list(dict.fromkeys(found))


def bare_reference_text(text: str) -> str:
    """Keep literal/prose references; leave actual links to Markdown validation."""
    tokens, environment = parse(text)
    # parse() excludes closed mapping frontmatter; its literal paths still need
    # the legacy skill-relative checks, unlike Markdown link destinations.
    fragments = [environment["frontmatter_text"]]
    for token in tokens:
        if token.type in {"fence", "code_block", "html_block"}:
            fragments.append(token.content)
        elif token.type == "inline":
            depth = 0
            for child in token.children or []:
                if child.type == "link_open":
                    depth += 1
                elif child.type == "link_close":
                    depth -= 1
                elif not depth and child.type != "image":
                    fragments.append(child.content)
    return "\n".join(fragments)


def validate_documentation(root: Path, files: list[Path], names: tuple[str, ...]) -> list[tuple[Path, str]]:
    errors: list[tuple[Path, str]] = []
    cache: dict[Path, str] = {}

    def read(path: Path) -> str:
        validate_source_path(path, root)
        if path not in cache:
            cache[path] = path.read_text(encoding="utf-8")
        return cache[path]

    for source in files:
        try:
            source_parts = source.relative_to(root).parts
            skill_root = root / source_parts[0] if source_parts and source_parts[0] in names else None
            for destination, line in links(read(source)):
                parsed = urlsplit(destination)
                if parsed.scheme or parsed.netloc:
                    continue
                target = Path(os.path.abspath(source.parent / unquote(parsed.path))) if parsed.path else source
                try:
                    validate_source_path(target, root)
                    if skill_root is not None and not target.is_relative_to(skill_root):
                        raise ValueError("target must stay below the skill directory")
                    if not target.exists():
                        raise ValueError("target does not exist")
                    if parsed.fragment and target.suffix.lower() == ".md" and unquote(parsed.fragment) not in anchors(read(target)):
                        raise ValueError("heading anchor does not exist")
                except (OSError, UnicodeError, SourcePathError, ValueError) as exc:
                    errors.append((source, f"near line {line}: invalid local Markdown link {destination!r}: {exc}"))
        except (OSError, UnicodeError, SourcePathError, ValueError) as exc:
            errors.append((source, f"could not validate Markdown: {exc}"))

    readme = root / "README.md"
    contributing = root / "CONTRIBUTING.md"
    inventories = []
    try:
        if readme.is_file():
            text = read(readme)
            inventories.extend((
                (readme, "Choose a skill", linked_skills(section_tokens(text, "Choose a skill"))),
                (readme, "Available Skills", heading_skills(section_tokens(text, "Available Skills"))),
                (readme, "Current layout", layout_directories(section_tokens(text, "Skill Structure"))),
            ))
        if contributing.is_file():
            inventories.append((contributing, "Source of Truth", listed_directories(section_tokens(read(contributing), "Source of Truth"))))
        for path, label, actual in inventories:
            if Counter(actual) != Counter(names):
                errors.append((path, f"{label} inventory must list every canonical skill exactly once; missing={sorted(set(names) - set(actual))}, extra={sorted(set(actual) - set(names))}, duplicates={sorted(name for name, count in Counter(actual).items() if count > 1)}"))
    except (OSError, UnicodeError, SourcePathError) as exc:
        errors.append((root, f"could not validate skill inventories: {exc}"))
    return errors
