#!/usr/bin/env python3
"""Build PDF manuals from the Markdown handbooks.

Source of truth: docs/handbook-de.md and docs/handbook-en.md.
This script converts each handbook to HTML, then renders to PDF via
headless Chrome (no external Python deps required).

The Markdown subset used in the handbooks is intentionally narrow:
    - H1, H2, H3 headers
    - Paragraphs
    - Unordered lists (`- `) with up to one level of nesting
    - Ordered lists (`1.`, `2.`, ...) with up to one level of nesting
    - GFM tables with header row and separator
    - Inline: **bold**, *italic*, `code`, [text](url)
    - Horizontal rules (`---`)

This narrow scope lets us implement a self-contained renderer here in
stdlib only, instead of depending on the `markdown` package which is
not installed on the project owner's machine.

Usage:
    python3 scripts/build_pdf_manual.py

Writes to repo root:
    CRAM-Anwenderhandbuch.pdf
    CRAM-User-Manual.pdf
"""

from __future__ import annotations

import datetime as _dt
import html as _html
import pathlib
import re
import struct
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def read_app_version() -> str:
    """Extract APP_VERSION from the HTML tool."""
    html_path = REPO_ROOT / "crisis-role-manager.html"
    text = html_path.read_text(encoding="utf-8")
    m = re.search(r"const\s+APP_VERSION\s*=\s*['\"]([^'\"]+)['\"]", text)
    if not m:
        raise RuntimeError("APP_VERSION not found in crisis-role-manager.html")
    return m.group(1)


# ---------------------------------------------------------------------------
# Markdown -> HTML renderer
# ---------------------------------------------------------------------------


_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<![*A-Za-z0-9])\*([^*]+)\*(?!\*)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
# Block-level image: `![alt](path)` on its own line. Captured before inline
# parsing so the link regex above does not turn it into a text link.
_IMAGE_BLOCK_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")


def _png_dimensions(path: pathlib.Path) -> tuple[int, int] | None:
    """Return (width, height) from a PNG file header, or None if unreadable.

    Uses only stdlib: PNG signature is 8 bytes, IHDR chunk header is 8 bytes,
    width+height live as big-endian uint32 at offsets 16-23.
    """
    try:
        with open(path, "rb") as f:
            header = f.read(24)
    except OSError:
        return None
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def _figure_class(width: int, height: int) -> str:
    """Pick a CSS size class for a figure based on the source PNG dimensions.

    Classes (ordered by check priority):
        tiny      width < 500       — small inline thumbnails (icons, badges)
        portrait  height > width    — modal screenshots (tall, narrow)
        wide      width > 1500      — full-app screenshots (landscape)
        standard  otherwise         — mid-size landscape panels
    """
    if width < 500:
        return "md-figure-tiny"
    if height > width:
        return "md-figure-portrait"
    if width > 1500:
        return "md-figure-wide"
    return "md-figure-standard"


def _render_inline(text: str) -> str:
    """Render inline markdown to HTML.

    Order matters: code first (protects its contents), then bold/italic/links.
    """
    # Protect inline code by replacing with placeholders.
    code_spans: list[str] = []

    def _stash_code(match: re.Match[str]) -> str:
        code_spans.append(match.group(1))
        return f"\x00CODE{len(code_spans) - 1}\x00"

    out = _INLINE_CODE.sub(_stash_code, text)
    out = _html.escape(out, quote=False)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _ITALIC.sub(r"<em>\1</em>", out)
    out = _LINK.sub(
        lambda m: f'<a href="{_html.escape(m.group(2), quote=True)}">'
        f"{_html.escape(m.group(1), quote=False)}</a>",
        out,
    )

    def _unstash(match: re.Match[str]) -> str:
        idx = int(match.group(1))
        return f"<code>{_html.escape(code_spans[idx], quote=False)}</code>"

    out = re.sub(r"\x00CODE(\d+)\x00", _unstash, out)
    return out


_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_HR_RE = re.compile(r"^-{3,}\s*$")
_UL_RE = re.compile(r"^(\s*)- (.*)$")
_OL_RE = re.compile(r"^(\s*)\d+\.\s+(.*)$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")


def _split_row(line: str) -> list[str]:
    """Split a markdown table row into cell strings."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [c.strip() for c in stripped.split("|")]


def markdown_to_html(md: str) -> str:
    """Convert the supported markdown subset to HTML.

    Block-level parser is a simple line-by-line state machine. Good enough
    for the handbook subset; not a general markdown library.
    """
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    def close_list_stack(stack: list[str]) -> None:
        while stack:
            out.append(f"</{stack.pop()}>")

    list_stack: list[str] = []  # stack of "ul"/"ol", parallel to indent levels
    indent_stack: list[int] = []

    while i < n:
        line = lines[i]
        stripped = line.rstrip()

        # Blank line -> close paragraphs/lists if we're in flow text contexts.
        if stripped == "":
            close_list_stack(list_stack)
            indent_stack.clear()
            i += 1
            continue

        # Horizontal rule
        if _HR_RE.match(stripped):
            close_list_stack(list_stack)
            indent_stack.clear()
            out.append("<hr/>")
            i += 1
            continue

        # Block-level image: a line that is just `![alt](path)`. Resolve the
        # path relative to docs/ (the markdown source location), then emit
        # as a figure with the same path absolutised so Chrome's file://
        # loader can find it regardless of where the temp HTML lives.
        im = _IMAGE_BLOCK_RE.match(stripped)
        if im:
            close_list_stack(list_stack)
            indent_stack.clear()
            alt = im.group(1).strip()
            src = im.group(2).strip()
            resolved = (DOCS_DIR / src).resolve()
            src_url = "file://" + str(resolved)
            dims = _png_dimensions(resolved)
            size_class = _figure_class(*dims) if dims else "md-figure-standard"
            out.append(f'<figure class="md-figure {size_class}">')
            out.append(
                f'<img src="{_html.escape(src_url, quote=True)}" '
                f'alt="{_html.escape(alt, quote=True)}"/>'
            )
            if alt:
                out.append(f"<figcaption>{_render_inline(alt)}</figcaption>")
            out.append("</figure>")
            i += 1
            continue

        # Headers
        m = _HEADER_RE.match(stripped)
        if m:
            close_list_stack(list_stack)
            indent_stack.clear()
            level = len(m.group(1))
            content = _render_inline(m.group(2).strip())
            out.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # Table: header row followed by a separator row
        if "|" in stripped and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1]):
            close_list_stack(list_stack)
            indent_stack.clear()
            headers = _split_row(stripped)
            i += 2  # consume header + separator
            rows: list[list[str]] = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                rows.append(_split_row(lines[i]))
                i += 1
            out.append('<table class="md-table">')
            out.append("<thead><tr>")
            for h in headers:
                out.append(f"<th>{_render_inline(h)}</th>")
            out.append("</tr></thead><tbody>")
            for row in rows:
                out.append("<tr>")
                # Pad/truncate to header count to avoid raggedness.
                cells = (row + [""] * len(headers))[: len(headers)]
                for c in cells:
                    out.append(f"<td>{_render_inline(c)}</td>")
                out.append("</tr>")
            out.append("</tbody></table>")
            continue

        # Unordered list item
        um = _UL_RE.match(line)
        om = _OL_RE.match(line)
        if um or om:
            indent_str = (um or om).group(1)
            indent = len(indent_str.expandtabs(4))
            content = (um or om).group(2)
            kind = "ul" if um else "ol"

            # Adjust list stack to match indent.
            while indent_stack and indent_stack[-1] > indent:
                out.append(f"</{list_stack.pop()}>")
                indent_stack.pop()
            if indent_stack and indent_stack[-1] == indent:
                # Same level — if list type differs, close + reopen.
                if list_stack[-1] != kind:
                    out.append(f"</{list_stack.pop()}>")
                    indent_stack.pop()
                    out.append(f"<{kind}>")
                    list_stack.append(kind)
                    indent_stack.append(indent)
            else:
                # Deeper indent than current stack -> open a new list.
                out.append(f"<{kind}>")
                list_stack.append(kind)
                indent_stack.append(indent)

            out.append(f"<li>{_render_inline(content)}</li>")
            i += 1
            continue

        # Default: paragraph. Collect consecutive non-blank, non-block lines.
        close_list_stack(list_stack)
        indent_stack.clear()
        para: list[str] = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].rstrip()
            if nxt == "":
                break
            if _HEADER_RE.match(nxt) or _HR_RE.match(nxt):
                break
            if _UL_RE.match(lines[i]) or _OL_RE.match(lines[i]):
                break
            if "|" in nxt and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1]):
                break
            para.append(nxt)
            i += 1
        out.append(f"<p>{_render_inline(' '.join(para))}</p>")

    close_list_stack(list_stack)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Page wrapper + Chrome render
# ---------------------------------------------------------------------------


CSS = """
@page {
  size: A4;
  margin: 22mm 18mm 22mm 18mm;
}
* { box-sizing: border-box; }
html, body {
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.5;
  color: #111;
  background: #fff;
  margin: 0;
  padding: 0;
}
.cover {
  page-break-after: always;
  text-align: left;
  padding-top: 60mm;
}
.cover h1 {
  font-size: 32pt;
  margin: 0 0 6mm 0;
  font-weight: 700;
  letter-spacing: -0.5pt;
}
.cover .sub {
  font-size: 14pt;
  color: #555;
  margin-bottom: 24mm;
}
.cover .meta {
  font-size: 10pt;
  color: #666;
  border-top: 1px solid #ccc;
  padding-top: 4mm;
}
.cover .meta div { margin: 1mm 0; }
h1 {
  font-size: 22pt;
  margin: 18pt 0 8pt 0;
  page-break-after: avoid;
  border-bottom: 2px solid #222;
  padding-bottom: 4pt;
}
h2 {
  font-size: 15pt;
  margin: 16pt 0 6pt 0;
  page-break-after: avoid;
}
h3 {
  font-size: 12pt;
  margin: 12pt 0 4pt 0;
  page-break-after: avoid;
  color: #333;
}
p, ul, ol { margin: 0 0 8pt 0; }
ul, ol { padding-left: 6mm; }
li { margin: 1.5pt 0; }
li > ul, li > ol { margin: 2pt 0 2pt 0; }
hr {
  border: 0;
  border-top: 1px solid #ccc;
  margin: 14pt 0;
}
code {
  font-family: "SF Mono", Menlo, Consolas, monospace;
  background: #f3f3f3;
  padding: 0.5pt 3pt;
  border-radius: 2pt;
  font-size: 9.5pt;
}
a { color: #1a4f8a; text-decoration: none; }
strong { font-weight: 600; }
table.md-table {
  width: 100%;
  border-collapse: collapse;
  margin: 6pt 0 12pt 0;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
table.md-table th,
table.md-table td {
  border: 1px solid #c8c8c8;
  padding: 4pt 6pt;
  text-align: left;
  vertical-align: top;
}
table.md-table th {
  background: #f0f0f0;
  font-weight: 600;
}
figure.md-figure {
  margin: 10pt auto 14pt auto;
  padding: 0;
  page-break-inside: avoid;
  break-inside: avoid;
  text-align: center;
}
figure.md-figure img {
  display: block;
  margin: 0 auto;
  border: 1px solid #d0d0d0;
  border-radius: 3pt;
  box-shadow: 0 1pt 3pt rgba(0,0,0,0.08);
}
figure.md-figure figcaption {
  margin-top: 4pt;
  font-size: 9pt;
  color: #555;
  font-style: italic;
  text-align: center;
}
/* Size classes -- width:auto + height:auto with both caps lets the browser
   pick the smaller scaling factor, preserving aspect ratio. */
figure.md-figure-tiny img {
  max-width: 35%;
  max-height: 4cm;
  width: auto;
  height: auto;
}
figure.md-figure-portrait img {
  max-width: 65%;
  max-height: 12cm;
  width: auto;
  height: auto;
}
figure.md-figure-standard img {
  max-width: 85%;
  max-height: 10cm;
  width: auto;
  height: auto;
}
figure.md-figure-wide img {
  max-width: 100%;
  max-height: 9cm;
  width: auto;
  height: auto;
}
"""


def wrap_html(body: str, title: str, subtitle: str, version: str, build_date: str, lang: str) -> str:
    """Wrap rendered body with cover page + styling."""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<title>{_html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<section class="cover">
  <h1>{_html.escape(title)}</h1>
  <div class="sub">{_html.escape(subtitle)}</div>
  <div class="meta">
    <div><strong>Version:</strong> {_html.escape(version)}</div>
    <div><strong>Build:</strong> {_html.escape(build_date)}</div>
    <div><strong>Source:</strong> docs/handbook-{lang}.md</div>
    <div><strong>License:</strong> Apache 2.0</div>
  </div>
</section>
{body}
</body>
</html>
"""


def render_to_pdf(html_path: pathlib.Path, pdf_path: pathlib.Path) -> None:
    """Invoke headless Chrome to render HTML to PDF."""
    if not pathlib.Path(CHROME_BIN).exists():
        raise RuntimeError(f"Chrome not found at {CHROME_BIN}")
    # Chrome insists on absolute paths for --print-to-pdf and file:// URLs.
    file_url = "file://" + str(html_path.resolve())
    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--no-sandbox",
        f"--print-to-pdf={pdf_path.resolve()}",
        "--virtual-time-budget=5000",
        file_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"Chrome failed: exit {result.returncode}")


# ---------------------------------------------------------------------------
# Per-language drivers
# ---------------------------------------------------------------------------


def build_de(version: str, build_date: str) -> pathlib.Path:
    md = (DOCS_DIR / "handbook-de.md").read_text(encoding="utf-8")
    # Strip the first H1 line because the cover already has the title.
    md = re.sub(r"^# [^\n]*\n+", "", md, count=1)
    body = markdown_to_html(md)
    html = wrap_html(
        body,
        title="CRAM Anwenderhandbuch",
        subtitle="Crisis Role Availability Manager",
        version=version,
        build_date=build_date,
        lang="de",
    )
    pdf_path = REPO_ROOT / "CRAM-Anwenderhandbuch.pdf"
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tf:
        tf.write(html)
        tmp = pathlib.Path(tf.name)
    try:
        render_to_pdf(tmp, pdf_path)
    finally:
        tmp.unlink(missing_ok=True)
    return pdf_path


def build_en(version: str, build_date: str) -> pathlib.Path:
    md = (DOCS_DIR / "handbook-en.md").read_text(encoding="utf-8")
    md = re.sub(r"^# [^\n]*\n+", "", md, count=1)
    body = markdown_to_html(md)
    html = wrap_html(
        body,
        title="CRAM User Manual",
        subtitle="Crisis Role Availability Manager",
        version=version,
        build_date=build_date,
        lang="en",
    )
    pdf_path = REPO_ROOT / "CRAM-User-Manual.pdf"
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tf:
        tf.write(html)
        tmp = pathlib.Path(tf.name)
    try:
        render_to_pdf(tmp, pdf_path)
    finally:
        tmp.unlink(missing_ok=True)
    return pdf_path


def main() -> int:
    version = read_app_version()
    build_date = _dt.date.today().isoformat()
    print(f"CRAM PDF build — version={version} date={build_date}")
    de = build_de(version, build_date)
    print(f"  wrote {de.relative_to(REPO_ROOT)} ({de.stat().st_size:,} bytes)")
    en = build_en(version, build_date)
    print(f"  wrote {en.relative_to(REPO_ROOT)} ({en.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
