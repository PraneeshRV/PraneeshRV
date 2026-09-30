#!/usr/bin/env python3
"""Build the README's two SVGs in light, dark and OS-following variants.

header: "I break AI agents." with the word "break" sliced.
map:    a multi-agent system, cut where my work breaks it.

Text is converted to outlines by usvg, so the SVGs look the same on every
machine. Needs fontTools, usvg (ships with resvg), and P052 plus Source Code
Pro (the `gsfonts` and `adobe-source-code-pro-fonts` packages on Arch).

Usage: python scripts/art.py
"""
import subprocess
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

FONTS = ["/usr/share/fonts/gsfonts/P052-Bold.otf",
         "/usr/share/fonts/gsfonts/P052-Italic.otf",
         "/usr/share/fonts/adobe-source-code-pro/SourceCodePro-Regular.otf"]
OUT = Path(__file__).resolve().parent.parent / "assets"

# Placeholder colours, swapped per theme after outlining. The theme values are GitHub's own
# text, muted and danger colours, so the SVGs sit on the page instead of on a card.
INK, MUTED, ACCENT = "#010203", "#010204", "#010205"
THEMES = {"light": {INK: "#1f2328", MUTED: "#59636e", ACCENT: "#cf222e"},
          "dark": {INK: "#f0f6fc", MUTED: "#9198a1", ACCENT: "#ff7b72"}}


def write(name, source):
    outlined = subprocess.run(
        ["usvg", *(a for f in FONTS for a in ("--use-font-file", f)), "-", "-c"],
        input=source, capture_output=True, text=True, check=True).stdout
    # usvg drops a viewBox that matches the size, but <img width="100%"> needs it to scale.
    width, height = source.split('viewBox="0 0 ')[1].split('"')[0].split()
    outlined = outlined.replace("<svg ", f'<svg viewBox="0 0 {width} {height}" ', 1)
    variants = {}
    for theme, colours in THEMES.items():
        svg = outlined
        for placeholder, colour in colours.items():
            svg = svg.replace(placeholder, colour)
        variants[theme] = svg
        (OUT / f"{name}-{theme}.svg").write_text(svg)
    # Fallback for renderers that ignore <picture>: follows the OS colour scheme instead.
    dark = "".join(f'[{attr}="{THEMES["light"][p]}"]{{{attr}:{THEMES["dark"][p]}}}'
                   for p in (INK, MUTED, ACCENT) for attr in ("fill", "stroke"))
    style = f"<style>@media (prefers-color-scheme: dark) {{ {dark} }}</style>"
    (OUT / f"{name}.svg").write_text(variants["light"].replace(">", ">" + style, 1))
    print(f"wrote {name} ({width}x{height})")


def header():
    text, word = "I break AI agents.", "break"
    size, track = 100, -2.5  # font size and letter-spacing, in px
    shift, gap = 12, 3       # how far the top of the word slides, and the height of the cut
    font = TTFont(FONTS[0])
    glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    k = size / font["head"].unitsPerEm

    def advance(s):
        return sum(hmtx[cmap[ord(c)]][0] * k + track for c in s)

    def bounds(c):
        pen = BoundsPen(glyphs)
        glyphs[cmap[ord(c)]].draw(pen)
        return pen.bounds  # xMin, yMin, xMax, yMax in font units

    ink = [bounds(c) for c in text if c != " "]
    top, bottom = max(b[3] for b in ink) * k, min(b[1] for b in ink) * k
    x0 = -bounds(text[0])[0] * k  # first stroke sits flush with the README's left edge
    base = round(top) + 2
    width = round(x0 + advance(text[:-1]) + bounds(text[-1])[2] * k) + 2
    height = round(base - bottom) + 18  # room below the descenders before the first line of text

    # The word's horizontal range runs to the middle of the spaces around it.
    start = text.index(word)
    space = advance(" ") / 2
    left = x0 + advance(text[:start]) - space
    right = x0 + advance(text[: start + len(word)]) + space
    cut = base - bounds("x")[3] * k / 2  # halfway up the x-height

    line = (f'<text x="{x0:.2f}" y="{base}" font-family="P052" font-weight="bold" '
            f'font-size="{size}" letter-spacing="{track}" fill="{INK}">{text}</text>')
    write("header", f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<clipPath id="rest"><path clip-rule="evenodd" d="M0 0H{width}V{height}H0Z M{left:.2f} 0H{right:.2f}V{cut + gap / 2:.2f}H{left:.2f}Z"/></clipPath>
<clipPath id="slid"><rect x="{left + shift:.2f}" y="0" width="{right - left:.2f}" height="{cut - gap / 2:.2f}"/></clipPath>
<g clip-path="url(#rest)">{line}</g>
<g clip-path="url(#slid)"><g transform="translate({shift} 0)">{line}</g></g>
</svg>""")


def attack_map():
    W, Y, B = 760, 62, 166  # width, main line, shared-memory bus
    H = B + 50
    G = 13                  # half the gap cut into a line at a break
    serif = 'font-family="P052" font-style="italic" font-size="24"'
    mono = 'font-family="Source Code Pro" font-size="16"'
    parts = []

    def line(d):
        parts.append(f'<path d="{d}" stroke="{MUTED}" stroke-width="1.5" fill="none"/>')

    def label(x, y, text, style, colour, anchor="middle"):
        parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" {style} fill="{colour}">{text}</text>')

    def node(x, y):
        parts.append(f'<rect x="{x - 5}" y="{y - 5}" width="10" height="10" fill="{INK}"/>')

    def brk(x, y, text, lx, ly, anchor="middle"):
        s = 7
        parts.append(f'<path d="M{x - s} {y - s}L{x + s} {y + s}M{x + s} {y - s}L{x - s} {y + s}" '
                     f'stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round"/>')
        label(lx, ly, text, mono, ACCENT, anchor)

    # input -A2A-> orchestrator -task queue-> agents -MCP-> tools, with the orchestrator and
    # agents sharing memory below, and agent identity checked on the A2A hop.
    line(f"M8 {Y}H{210 - G}M{210 + G} {Y}H{420 - G}M{420 + G} {Y}H{646 - G}M{646 + G} {Y}H752")
    line(f"M300 {Y}V{B}H{420 - G}M{420 + G} {B}H540V{Y}")
    line(f"M80 {Y}V{130 - G}M80 {130 + G}V{B}")
    for x in (13, 300, 540, 747):
        node(x, Y)
    node(80, B)
    label(8, Y - 30, "input", serif, INK, "start")
    label(300, Y - 30, "orchestrator", serif, INK)
    label(540, Y - 30, "agents", serif, INK)
    label(752, Y - 30, "tools", serif, INK, "end")
    label(80, B + 38, "agent identity", serif, INK)
    for x, y, text in [(210, Y, "A2A"), (420, Y, "task queue"), (646, Y, "MCP"), (420, B, "shared memory")]:
        label(x, y - 12, text, mono, MUTED)
    brk(210, Y, "JSON injection", 210, Y + 34)
    brk(80, 130, "token, card forgery", 100, 136, "start")
    brk(420, Y, "task-queue poisoning", 420, Y + 34)
    brk(420, B, "memory poisoning", 420, B + 34)
    brk(646, Y, "exposed configs", 646, Y + 34)
    write("map", f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
                 f'viewBox="0 0 {W} {H}">{"".join(parts)}</svg>')


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    header()
    attack_map()
