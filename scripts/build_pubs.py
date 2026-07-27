#!/usr/bin/env python3
"""Regenerate the publications section of index.html from data/papers.bib.

Usage:
    python3 scripts/build_pubs.py           # rewrite index.html in place
    python3 scripts/build_pubs.py --check   # exit 1 if index.html is stale

Only the region between the PUBS:START and PUBS:END markers is touched.
Standard library only, so there is nothing to install.
"""

import argparse
import html
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "data" / "papers.bib"
PAGE = ROOT / "index.html"

ME = "Jinquan Hang"
START = "<!-- PUBS:START -->"
END = "<!-- PUBS:END -->"
INDENT = " " * 10

# LaTeX markup that DBLP exports and that has to become plain text for the web.
COMBINING = {
    "`": "\u0300", "'": "\u0301", "^": "\u0302", "~": "\u0303", '"': "\u0308",
    "=": "\u0304", ".": "\u0307", "c": "\u0327", "v": "\u030c", "u": "\u0306",
    "H": "\u030b", "r": "\u030a", "k": "\u0328",
}
STANDALONE = {
    "ss": "ß", "ae": "æ", "AE": "Æ", "oe": "œ", "OE": "Œ", "aa": "å",
    "AA": "Å", "o": "ø", "O": "Ø", "l": "ł", "L": "Ł", "i": "ı", "j": "ȷ",
}


def read_value(text, i):
    """Read one field value starting at i. Returns (raw value, index after it)."""
    while i < len(text) and text[i].isspace():
        i += 1
    if i >= len(text):
        return "", i

    if text[i] == "{":
        depth, start, i = 1, i + 1, i + 1
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        return text[start : i - 1], i

    if text[i] == '"':
        start = i = i + 1
        while i < len(text) and text[i] != '"':
            i += 1
        return text[start:i], i + 1

    start = i
    while i < len(text) and text[i] not in ",\n":
        i += 1
    return text[start:i], i


def parse_bib(text):
    """Parse the BibTeX dialect DBLP emits into a list of dicts."""
    entries = []
    for match in re.finditer(r"@(\w+)\s*\{", text):
        kind = match.group(1).lower()
        if kind in ("string", "comment", "preamble"):
            continue

        # Walk from the opening brace to its match, respecting nesting.
        depth, i = 1, match.end()
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        if depth:
            sys.exit(
                f"Unbalanced braces in {BIB} — entry starting with "
                f"{text[match.start() : match.start() + 60]!r} is never closed."
            )
        body = text[match.end() : i - 1]

        key, _, fields = body.partition(",")
        entry = {"_type": kind, "_key": key.strip()}
        consumed = 0
        for field in re.finditer(r"(\w+)\s*=\s*", fields):
            if field.start() < consumed:
                continue  # an '=' that lives inside a value we already read
            raw, consumed = read_value(fields, field.end())
            entry[field.group(1).lower()] = " ".join(raw.split())
        entries.append(entry)
    return entries


def plain(value):
    """Render a BibTeX field as plain Unicode: strip protective braces, decode accents."""

    def combine(match):
        mark = COMBINING[match.group(1)]
        return unicodedata.normalize("NFC", match.group(2) + mark)

    # \"{u} / \'e / \c{c} -> accented letter
    value = re.sub(r'\\([`\'^~"=.cvuHrk])\s*\{\s*(\w)\s*\}', combine, value)
    value = re.sub(r'\\([`\'^~"=.])\s*(\w)', combine, value)
    # \v S / \c c -- letter commands need the space, so \cite is left alone
    value = re.sub(r"\\([cvuHrk])\s+(\w)", combine, value)
    # \ss, \o, \aa ... -> ß, ø, å
    for tex, char in sorted(STANDALONE.items(), key=lambda kv: -len(kv[0])):
        value = re.sub(r"\\" + tex + r"(\{\})?(?![A-Za-z])", char, value)
    value = value.replace("---", "\u2014").replace("--", "\u2013")
    value = value.replace(r"\&", "&").replace(r"\%", "%").replace(r"\$", "$")
    return re.sub(r"(?<!\\)[{}]", "", value).strip()


def format_authors(raw):
    """'A and B and C' -> 'A, B, C' with my own name in bold."""
    out = []
    for name in re.split(r"\s+and\s+", plain(raw)):
        name = name.strip()
        if not name:
            continue
        escaped = html.escape(name)
        out.append(f"<b>{escaped}</b>" if name == ME else escaped)
    return ", ".join(out)


def render(entries):
    """Render every entry, newest year first, file order preserved within a year."""
    ordered = sorted(entries, key=lambda e: int(e.get("year", 0)), reverse=True)

    blocks = []
    for entry in ordered:
        links = []
        for label, field in (("Paper", "url"), ("Code", "code"), ("Slides", "slides")):
            if entry.get(field):
                links.append(f'[<a href="{html.escape(entry[field])}">{label}</a>]')

        venue = html.escape(plain(entry.get("venue", entry.get("year", ""))))
        meta = f'<span class="venue">{venue}</span>'
        if links:
            meta += " " + " ".join(links)

        # A stable per-paper anchor, so others can deep-link a single entry.
        anchor = re.sub(r"[^a-z0-9-]", "", entry.get("_key", "").lower())

        blocks.append(
            f'{INDENT}<article class="pub" id="pub-{anchor}">\n'
            f'{INDENT}  <p class="pub-title">{html.escape(plain(entry.get("title", "")))}</p>\n'
            f'{INDENT}  <p class="pub-authors">{format_authors(entry.get("author", ""))}</p>\n'
            f'{INDENT}  <p class="pub-meta">{meta}</p>\n'
            f"{INDENT}</article>"
        )
    return "\n".join(blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify index.html is up to date instead of rewriting it",
    )
    args = parser.parse_args()

    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    if not entries:
        sys.exit(f"No entries found in {BIB}")

    page = PAGE.read_text(encoding="utf-8")
    head, marker, rest = page.partition(START)
    _, end_marker, tail = rest.partition(END)
    if not marker or not end_marker:
        sys.exit(f"Missing {START} / {END} markers in {PAGE}")

    # Spliced literally — never through re.sub, whose replacement argument would
    # reinterpret backslashes coming from the bibliography.
    updated = f"{head}{START}\n{render(entries)}\n{INDENT}{END}{tail}"

    if args.check:
        if updated != page:
            sys.exit("index.html is out of date — run: python3 scripts/build_pubs.py")
        print(f"index.html is up to date ({len(entries)} publications)")
        return

    if updated == page:
        print(f"index.html already current ({len(entries)} publications)")
    else:
        PAGE.write_text(updated, encoding="utf-8")
        print(f"Wrote {len(entries)} publications into index.html")


if __name__ == "__main__":
    main()
