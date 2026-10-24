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
from markdown_it.rules_inline import html_inline
from markdown_it.rules_inline.state_inline import StateInline
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

    def feed(self, data: str) -> None:
        # Visibility needs synchronous state; newer HTMLParser.feed can defer short chunks.
        self.rawdata += data
        self.goahead(0)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"code", "pre", "script", "style", "textarea", "title"}:
            self.tags.append(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.tags) - 1, -1, -1):
            if self.tags[index] == tag:
                del self.tags[index:]
                break


def _open_comment_offset(text: str, environment: dict[str, Any]) -> int | None:
    parser = MarkdownIt("commonmark")

    def located_html(state: StateInline, silent: bool) -> bool:
        start = state.pos
        if html_inline(state, silent):
            return True
        if silent or not state.src.startswith("<!--", start):
            return False
        token = state.push("comment_open", "", 0)
        token.meta["source_start"] = start
        state.pos += 4
        return True

    # Native rules consume code spans, escapes, attributes, and closed comments first.
    parser.inline.ruler.at("html_inline", located_html)
    children = parser.inline.parse(text, parser, environment, [])
    literal = LiteralHTML()
    for child in children:
        if child.type == "html_inline":
            literal.feed(child.content)
        elif child.type == "comment_open" and not literal.tags:
            return child.meta["source_start"]
    return None


def _source_position(lines: list[str], token: Token, offset: int) -> tuple[int, int]:
    prefix = token.content[:offset]
    row = prefix.count("\n")
    line = token.map[0] + row
    content = token.content.split("\n")[row]
    # CommonMark strips prefixes, indentation, and closing ATX hashes.
    indent = lines[line].find(content.strip()) - (len(content) - len(content.lstrip()))
    return line, indent + len(prefix.rsplit("\n", 1)[-1])


def _mask_literal_html(lines: list[str], tokens: list[Token], environment: dict[str, Any]) -> tuple[str, str]:
    """Mask literal Markdown, retaining its source for path hygiene and real tags."""
    source = "".join(lines)
    masked = list(source)
    hidden = []
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    def mask(start: int, end: int) -> None:
        hidden.append(source[start:end])
        # Inert text preserves paragraph context before a same-line HTML closer.
        masked[start:end] = [char if char.isspace() else "\ufffd" for char in source[start:end]]

    def located_html(state: StateInline, silent: bool) -> bool:
        start = state.pos
        if not html_inline(state, silent):
            return False
        if not silent:
            state.tokens[-1].meta["source_span"] = (start, state.pos)
        return True

    parser = MarkdownIt("commonmark")
    parser.inline.ruler.at("html_inline", located_html)
    contexts = [(LiteralHTML(), 0, len(source))]
    masked_comment = False
    for token in tokens:
        if token.type == "blockquote_open":
            contexts.append((LiteralHTML(), offsets[token.map[0]], offsets[token.map[1]]))
        elif token.type == "blockquote_close":
            literal, cursor, end = contexts.pop()
            if literal.tags:
                mask(cursor, end)
        if token.map is None:
            continue

        fragments = []
        if token.type == "html_block":
            fragments.append((offsets[token.map[0]], offsets[token.map[1]], token.content, 0))
        elif token.type == "inline":
            def position(offset: int) -> int:
                line, column = _source_position(lines, token, offset)
                return offsets[line] + column

            children = parser.inline.parse(token.content, parser, environment, [])
            for child in children:
                if child.type == "html_inline":
                    start, end = child.meta["source_span"]
                    fragments.append((position(start), position(end), child.content, start))
        for start, end, content, content_offset in fragments:
            literal, cursor, scope_end = contexts[-1]
            if literal.tags:
                mask(cursor, start)
            literal.feed(content)
            if literal.tags and literal.cdata_elem is None and literal.rawdata.startswith("<!--"):
                line, column = _source_position(lines, token, content_offset + len(content) - len(literal.rawdata))
                opening = offsets[line] + column
                closing = source.find("-->", opening + 4, scope_end)
                # Remove the whole comment before reparsing, including any inert closers.
                mask(opening, scope_end if closing < 0 else closing + 3)
                if closing >= 0:
                    line_start = source.rfind("\n", opening, closing) + 1
                    masked[max(opening, line_start):closing] = [""] * (closing - max(opening, line_start))
                    masked[closing:closing + 3] = "-->"
                masked_comment = True
                break
            contexts[-1] = (literal, end, scope_end)
        if masked_comment:
            break
    literal, cursor, end = contexts[0]
    if literal.tags and not masked_comment:
        mask(cursor, end)
    # Keep quoted examples scoped when reparsing the blanked source.
    for index, line in enumerate(lines):
        prefix = re.match(r"^(?:[ \t]*>[ \t]?)*", line)[0]
        masked[offsets[index]:offsets[index] + len(prefix)] = prefix
    return "".join(masked), "\n".join(hidden)


def parse_visible(text: str) -> tuple[list[Token], dict[str, Any]]:
    """Exclude literal HTML and reopened comments, retaining source line maps."""
    lines = [line.replace("\0", "\ufffd") + "\n" for line in text.splitlines()]
    hidden = []
    heading_source = {}
    comment_tails: set[int] = set()
    while True:
        source = "".join(lines)
        tokens, environment = parse(source)
        for index, token in enumerate(tokens):
            if token.type == "heading_open":
                heading_source.setdefault(token.map[0], tokens[index + 1].content)
        visible, literal_source = _mask_literal_html(lines, tokens, environment)
        if visible != source:
            hidden.append(literal_source)
            lines = visible.splitlines(keepends=True)
            continue
        contexts = [(LiteralHTML(), len(lines))]
        for token in tokens:
            if token.type == "blockquote_open":
                contexts.append((LiteralHTML(), token.map[1]))
            elif token.type == "blockquote_close":
                contexts.pop()
            literal, scope_end = contexts[-1]
            opening = None
            if token.type == "html_block":
                literal.feed(token.content)
                if not literal.tags and literal.rawdata.startswith("<!--"):
                    opening = len(token.content) - len(literal.rawdata)
            else:
                if token.type == "inline" and not literal.tags and any(
                    token.map[0] <= line < token.map[1] for line in comment_tails
                ):
                    content = "\n".join(token.content.split("\n")[:scope_end - token.map[0]])
                    opening = _open_comment_offset(content, environment)
                for child in token.children or []:
                    if child.type == "html_inline":
                        literal.feed(child.content)
            if opening is None:
                continue

            # CommonMark ends an HTML block at its first closer, even when a
            # second comment on that line still hides subsequent Markdown.
            start, column = _source_position(lines, token, opening)
            end = scope_end
            closing_tail = None
            for closing_line in range(token.map[1], scope_end):
                _, closed, tail = lines[closing_line].partition("-->")
                if closed:
                    end = closing_line + 1
                    quote_prefix = re.match(r"^(?:[ \t]*>[ \t]?)*", lines[closing_line])[0]
                    closing_tail = quote_prefix + "-->" + tail
                    break
            removed = lines[start:end]
            removed[0] = removed[0][column:]
            if closing_tail is not None:
                removed[-1] = removed[-1].partition("-->")[0]
            hidden.append("".join(removed))
            lines[start] = lines[start][:column] + "\n"
            for line in range(start + 1, end):
                quote_prefix = re.match(r"^(?:[ \t]*>[ \t]?)*", lines[line])[0]
                lines[line] = quote_prefix + "\n"
            if closing_tail is not None:
                lines[end - 1] = closing_tail
                comment_tails.add(end - 1)
            # Removed definitions can expose HTML in image labels, including retained tails.
            break
        else:
            environment["hidden_source"] = "\n".join(hidden)
            environment["heading_source"] = heading_source
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
    tokens, environment = parse_visible(text)
    found: set[str] = set()
    explicit_names: set[str] = set()
    contexts = [HTMLAnchors()]
    parser = MarkdownIt("commonmark")
    counts: Counter[str] = Counter()
    for index, token in enumerate(tokens):
        if token.type == "blockquote_open":
            contexts.append(HTMLAnchors())
        elif token.type == "blockquote_close":
            explicit_names.update(contexts.pop().names)
        explicit = contexts[-1]
        if token.type == "html_block":
            explicit.feed(token.content)
        for child in token.children or []:
            if child.type == "html_inline":
                explicit.feed(child.content)
        if token.type == "heading_open" and explicit.cdata_elem is None:
            # Preserve rendered labels, resolving references against visible definitions.
            source = environment["heading_source"].get(token.map[0], tokens[index + 1].content)
            title = inline_text(parser.inline.parse(source, parser, environment, [])).lower()
            slug = re.sub(r"\s", "-", re.sub(r"[^\w\-\s]", "", title))
            candidate = slug
            while candidate in found:
                counts[slug] += 1
                candidate = f"{slug}-{counts[slug]}"
            found.add(candidate)
    return found | explicit_names | contexts[0].names


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
    tokens, environment = parse_visible(text)
    # Frontmatter and hidden example destinations remain literal path evidence.
    fragments = [environment["frontmatter_text"], environment["hidden_source"]]
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
