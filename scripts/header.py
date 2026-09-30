#!/usr/bin/env python3
"""Build the README header: "I break AI agents." with the word "break" sliced.

Text is converted to outlines by usvg, so the SVGs look the same on every
machine. Needs fontTools, usvg (ships with resvg) and P052 Bold from the URW
base35 fonts (the `gsfonts` package on Arch).

Usage: python scripts/header.py [path/to/P052-Bold.otf]
"""
import subprocess
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

FONT = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/fonts/gsfonts/P052-Bold.otf"
OUT = Path(__file__).resolve().parent.parent / "assets"
TEXT, WORD = "I break AI agents.", "break"
SIZE, TRACK = 100, -2.5  # font size and letter-spacing, in px
SHIFT, GAP = 12, 3       # how far the top of the word slides, and the height of the cut
LIGHT, DARK = "#1f2328", "#f0f6fc"  # GitHub's own text colours
SENTINEL = "#010203"

font = TTFont(FONT)
glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
k = SIZE / font["head"].unitsPerEm


def advance(s):
    return sum(hmtx[cmap[ord(c)]][0] * k + TRACK for c in s)


def bounds(c):
    pen = BoundsPen(glyphs)
    glyphs[cmap[ord(c)]].draw(pen)
    return pen.bounds  # xMin, yMin, xMax, yMax in font units


ink = [bounds(c) for c in TEXT if c != " "]
top, bottom = max(b[3] for b in ink) * k, min(b[1] for b in ink) * k
x0 = -bounds(TEXT[0])[0] * k  # first stroke sits flush with the README's left edge
base = round(top) + 2
width = round(x0 + advance(TEXT[:-1]) + bounds(TEXT[-1])[2] * k) + 2
height = round(base - bottom) + 18  # room below the descenders before the first line of text

# The word's horizontal range runs to the middle of the spaces around it.
start = TEXT.index(WORD)
space = advance(" ") / 2
left = x0 + advance(TEXT[:start]) - space
right = x0 + advance(TEXT[: start + len(WORD)]) + space
cut = base - bounds("x")[3] * k / 2  # halfway up the x-height

line = (f'<text x="{x0:.2f}" y="{base}" font-family="P052" font-weight="bold" '
        f'font-size="{SIZE}" letter-spacing="{TRACK}" fill="{SENTINEL}">{TEXT}</text>')
source = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<clipPath id="rest"><path clip-rule="evenodd" d="M0 0H{width}V{height}H0Z M{left:.2f} 0H{right:.2f}V{cut + GAP / 2:.2f}H{left:.2f}Z"/></clipPath>
<clipPath id="slid"><rect x="{left + SHIFT:.2f}" y="0" width="{right - left:.2f}" height="{cut - GAP / 2:.2f}"/></clipPath>
<g clip-path="url(#rest)">{line}</g>
<g clip-path="url(#slid)"><g transform="translate({SHIFT} 0)">{line}</g></g>
</svg>"""

outlined = subprocess.run(["usvg", "--use-font-file", FONT, "-", "-c"], input=source,
                          capture_output=True, text=True, check=True).stdout
assert SENTINEL in outlined, "usvg dropped the text; is the font path right?"
# usvg drops a viewBox that matches the size, but <img width="100%"> needs it to scale.
outlined = outlined.replace("<svg ", f'<svg viewBox="0 0 {width} {height}" ', 1)

OUT.mkdir(exist_ok=True)
(OUT / "header-light.svg").write_text(outlined.replace(SENTINEL, LIGHT))
(OUT / "header-dark.svg").write_text(outlined.replace(SENTINEL, DARK))
# Fallback for renderers that ignore <picture>: follows the OS colour scheme instead.
style = f"<style>@media (prefers-color-scheme: dark) {{ path {{ fill: {DARK} }} }}</style>"
(OUT / "header.svg").write_text(outlined.replace(SENTINEL, LIGHT).replace(">", ">" + style, 1))
print(f"wrote {width}x{height} header SVGs to {OUT}")
