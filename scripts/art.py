#!/usr/bin/env python3
"""Build the profile README's animated SVGs, drawn as plates from a star atlas.

hero      the pulsar PSR B1257+12 sweeping its beam across "I break AI agents."
tile-*    one animated scene per project, each linked to its repo from the README
hunter    Team Hunter drawn as Orion, the hunter, beside the CTF numbers

Text is outlined by usvg so it renders the same everywhere. Motion is CSS and SMIL
inside each SVG; under prefers-reduced-motion everything stops on a composed still.
Needs fontTools, usvg (ships with resvg), and P052 plus Source Code Pro (the
`gsfonts` and `adobe-source-code-pro-fonts` packages on Arch).

Usage: python scripts/art.py
"""
import math
import random
import re
import subprocess
from functools import cache
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

OUT = Path(__file__).resolve().parent.parent / "assets"
FONT_FILES = {"serif": "/usr/share/fonts/gsfonts/P052-Bold.otf",
              "italic": "/usr/share/fonts/gsfonts/P052-Italic.otf",
              "mono": "/usr/share/fonts/adobe-source-code-pro/SourceCodePro-Regular.otf"}
FONT_ATTRS = {"serif": 'font-family="P052" font-weight="bold"',
              "italic": 'font-family="P052" font-style="italic"',
              "mono": 'font-family="Source Code Pro"'}

# AMOLED black with pastel light: lilac for structure, mint for the moment something breaks.
STAR, LILAC, VIOLET, MINT, MUTED = "#f5f3ff", "#c4b5fd", "#8b5cf6", "#6ee7b7", "#9d98bd"
TITLE = "#ede9fe"


# ---------------------------------------------------------------- text and frame

@cache
def outline(s, x, y, font, size, anchor="start", track=0):
    """Path data for a line of text, shaped and kerned by usvg."""
    src = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600">'
           f'<text x="{x}" y="{y}" {FONT_ATTRS[font]} font-size="{size}" letter-spacing="{track}" '
           f'text-anchor="{anchor}">{escape(s)}</text></svg>')
    out = subprocess.run(["usvg", "--use-font-file", FONT_FILES[font], "-", "-c"],
                         input=src, capture_output=True, text=True, check=True).stdout
    d = " ".join(re.findall(r' d="([^"]+)"', out))
    assert d, f"usvg drew nothing for {s!r}; is the {font} font installed?"
    return re.sub(r"-?\d+\.\d+", lambda m: f"{float(m.group()):.1f}".rstrip("0").rstrip("."), d)


def label(s, x, y, font="mono", size=15, fill=MUTED, anchor="start", track=0, extra=""):
    return f'<path fill="{fill}" {extra} d="{outline(s, x, y, font, size, anchor, track)}"/>'


BASE_CSS = """
.tw{animation:tw ease-in-out infinite alternate}
@keyframes tw{from{opacity:.12}to{opacity:.95}}
@keyframes spin{to{transform:rotate(360deg)}}
.still{display:none}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.move{display:none}.still{display:inline}}
"""


def frame(name, w, h, body, css="", title="", pad_left=0, pad_right=0, pad_bottom=0):
    """A black plate with rounded corners. Padding is transparent and sits outside the plate."""
    vw, vh = w + pad_left + pad_right, h + pad_bottom
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{vw}" height="{vh}" '
           f'viewBox="{-pad_left} 0 {vw} {vh}" role="img" aria-label="{escape(title)}">'
           f'<title>{escape(title)}</title><style>{BASE_CSS}{css}</style>'
           f'<clipPath id="plate"><rect width="{w}" height="{h}" rx="16"/></clipPath>'
           f'<g clip-path="url(#plate)"><rect width="{w}" height="{h}" fill="#000"/>{body}</g></svg>')
    (OUT / f"{name}.svg").write_text(svg)
    print(f"wrote {name}.svg ({len(svg) // 1024} KB)")


def stars(seed, w, h, n, twinkle, keep_out=()):
    """A fixed-seed starfield. keep_out holds (x0, y0, x1, y1) boxes to leave dark for text."""
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        if any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in keep_out):
            continue
        r = rng.choice([0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5])
        colour = rng.choice([STAR, STAR, STAR, LILAC, "#ddd6fe", "#d1fae5"])
        a = f'opacity="{rng.uniform(.25, .8):.2f}"'
        if len(out) < twinkle:
            a = (f'class="tw" style="animation-duration:{rng.uniform(2.2, 5.5):.1f}s;'
                 f'animation-delay:-{rng.uniform(0, 5):.1f}s"')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{colour}" {a}/>')
    return "".join(out)


def glow(id_, colour, stops=((0, .9), (.25, .35), (1, 0))):
    s = "".join(f'<stop offset="{o}" stop-color="{colour}" stop-opacity="{a}"/>' for o, a in stops)
    return f'<radialGradient id="{id_}">{s}</radialGradient>'


def plate_ticks(w, h, inset=14):
    """Graduations along the plate edge, like the border of an old star chart."""
    d = []
    for x in range(inset + 20, w - inset - 10, 20):
        t = 7 if (x - inset) % 100 == 0 else 3.5
        d.append(f"M{x} {inset}v{t}M{x} {h - inset}v{-t}")
    for y in range(inset + 20, h - inset - 10, 20):
        t = 7 if (y - inset) % 100 == 0 else 3.5
        d.append(f"M{inset} {y}h{t}M{w - inset} {y}h{-t}")
    return (f'<rect x="{inset}" y="{inset}" width="{w - 2 * inset}" height="{h - 2 * inset}" rx="6" '
            f'fill="none" stroke="{LILAC}" stroke-opacity=".14"/>'
            f'<path d="{"".join(d)}" stroke="{LILAC}" stroke-opacity=".22" stroke-width="1"/>')


GUTTER = 7  # each tile's half of the gap between a pair, so two tiles span the header exactly


def tile(name, title, sub, scene, css="", alt="", seed=0, side="left", top_row=False):
    w, h = 480, 300
    body = (stars(seed, w, h, 55, 10, keep_out=[(20, 222, 460, 290)]) + plate_ticks(w, h) + scene
            + label(title, 32, 254, "serif", 30, TITLE)
            + label(sub, 32, 280, "mono", 14, MUTED))
    frame(name, w, h, body, css, alt, pad_left=GUTTER if side == "right" else 0,
          pad_right=GUTTER if side == "left" else 0, pad_bottom=GUTTER - 2 if top_row else 0)


# ---------------------------------------------------------------- hero

def hero():
    W, H = 1000, 380
    px, py = 846, 132             # the pulsar
    size, track, x0, base = 88, -2.2, 56, 268
    T = 9                         # seconds per rotation of the beams
    text, word = "I break AI agents.", "break"

    font = TTFont(FONT_FILES["serif"])
    glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    k = size / font["head"].unitsPerEm

    def advance(s):
        return sum(hmtx[cmap[ord(c)]][0] * k + track for c in s)

    pen = BoundsPen(glyphs)
    glyphs[cmap[ord("x")]].draw(pen)
    cut = base - pen.bounds[3] * k / 2            # halfway up the x-height
    start = text.index(word)
    left = x0 + advance(text[:start]) - advance(" ") / 2
    right = x0 + advance(text[: start + len(word)]) + advance(" ") / 2
    shift, gap = 11, 3

    d = outline(text, x0, base, "serif", size, "start", track)
    title_clip = (f'<clipPath id="rest"><path clip-rule="evenodd" d="M0 0H{W}V{H}H0Z'
                  f'M{left:.1f} 0H{right:.1f}V{cut + gap / 2:.1f}H{left:.1f}Z"/></clipPath>'
                  f'<clipPath id="slid"><rect x="{left + shift:.1f}" y="0" width="{right - left:.1f}" '
                  f'height="{cut - gap / 2:.1f}"/></clipPath>')

    def title(fill):
        return (f'<g fill="{fill}"><path clip-path="url(#rest)" d="{d}"/>'
                f'<g clip-path="url(#slid)"><g class="jolt"><path transform="translate({shift} 0)" d="{d}"/>'
                f'</g></g></g>')

    # The beams start pointed at "break", so the reduced-motion still shows the word being hit.
    bx, by = (left + right) / 2, cut
    aim = math.degrees(math.atan2(by - py, bx - px)) % 360
    start_angle = aim - 180         # beam two (drawn at 180 degrees) begins on the word
    hits = [0.0, 0.5]               # fractions of a turn when a beam crosses the word
    jolt = "".join(f"{max(p * 100 - 1.5, 0):.2f}%{{transform:translateX(0)}}"
                   f"{p * 100 + .6:.2f}%{{transform:translateX(9px)}}"
                   f"{p * 100 + 4:.2f}%{{transform:translateX(0)}}" for p in hits)
    flash = "".join(f"{max(p * 100 - 1, 0):.2f}%{{opacity:0}}{p * 100 + .6:.2f}%{{opacity:1}}"
                    f"{p * 100 + 6:.2f}%{{opacity:0}}" for p in hits)
    css = (f".beam{{transform-origin:{px}px {py}px;animation:beam {T}s linear infinite}}"
           f"@keyframes beam{{from{{transform:rotate({start_angle:.1f}deg)}}"
           f"to{{transform:rotate({start_angle + 360:.1f}deg)}}}}"
           f".jolt{{animation:jolt {T}s linear infinite}}@keyframes jolt{{{jolt}100%{{transform:translateX(0)}}}}"
           f".flash{{opacity:0;animation:flash {T}s linear infinite}}@keyframes flash{{{flash}100%{{opacity:0}}}}"
           f"@media (prefers-reduced-motion:reduce){{.flash{{opacity:.8}}}}")

    L, half = 1000, 2.6             # beam length and half-angle in degrees
    a = math.radians(half)
    wedge = (f"M{px} {py}L{px + L * math.cos(a):.1f} {py + L * math.sin(a):.1f}"
             f"L{px + L * math.cos(a):.1f} {py - L * math.sin(a):.1f}Z")
    beams = (f'<path d="{wedge}" fill="url(#beamfade)"/>'
             f'<path d="{wedge}" fill="url(#beamfade)" transform="rotate(180 {px} {py})"/>')
    rot = f'transform="rotate({start_angle:.1f} {px} {py})"'

    defs = (f'<defs>{glow("core", "#ffffff", ((0, 1), (.08, .9), (.3, .25), (1, 0)))}'
            f'{glow("neb", VIOLET, ((0, .35), (.5, .08), (1, 0)))}{glow("neb2", MINT, ((0, .12), (1, 0)))}'
            f'<linearGradient id="beamfade" gradientUnits="userSpaceOnUse" x1="{px}" y1="0" x2="{px + L}" y2="0">'
            f'<stop offset="0" stop-color="#fff" stop-opacity=".85"/><stop offset=".35" stop-color="{LILAC}" '
            f'stop-opacity=".35"/><stop offset="1" stop-color="{LILAC}" stop-opacity="0"/></linearGradient>'
            f'<mask id="lit"><g class="beam" {rot}><path d="{wedge}" fill="#fff"/>'
            f'<path d="{wedge}" fill="#fff" transform="rotate(180 {px} {py})"/></g></mask>'
            f'{title_clip}</defs>')

    # Magnetic field loops ride along with the beams, the way a pulsar's axis carries them.
    loops = "".join(f'<ellipse cx="{px}" cy="{py + s * 20}" rx="44" ry="20" fill="none" stroke="{LILAC}" '
                    f'stroke-opacity=".28" transform="rotate(90 {px} {py})"/>' for s in (-1, 1))
    body = (defs
            + f'<ellipse cx="{px}" cy="{py}" rx="360" ry="260" fill="url(#neb)"/>'
            + f'<ellipse cx="120" cy="400" rx="420" ry="220" fill="url(#neb2)"/>'
            + stars(7, W, H, 190, 34, keep_out=[(40, 180, 740, 290), (40, 30, 330, 72)])
            + plate_ticks(W, H)
            + f'<g class="beam" {rot}>{beams}{loops}</g>'
            + f'<circle cx="{px}" cy="{py}" r="70" fill="url(#core)"/>'
            + f'<circle cx="{px}" cy="{py}" r="4.2" fill="#fff"/>'
            + title(TITLE)
            + f'<g mask="url(#lit)">{title(MINT)}</g>'
            + f'<rect class="flash" x="{left + 4:.1f}" y="{cut - .6:.1f}" width="{right - left + shift:.1f}" '
              f'height="1.2" fill="{MINT}"/>'
            + label("PRANEESH R V", x0 + 2, 64, "mono", 17, LILAC, track=5)
            + label("AI RED TEAMING  ·  OFFENSIVE SECURITY  ·  AMRITA '27", x0 + 2, 330, "mono", 15, MUTED,
                    track=1.5)
            + f'<path d="M{px} {py + 12}V{py + 64}" stroke="{LILAC}" stroke-opacity=".35"/>'
            + label("PSR B1257+12", px, py + 86, "mono", 13, LILAC, "middle", 1)
            + label("13h 00m 03s  +12° 40′ 57″", px, py + 104, "mono", 11, MUTED, "middle"))
    frame("hero", W, H, body, css, "I break AI agents. Praneesh R V, AI red teaming and offensive security.")


# ---------------------------------------------------------------- project tiles

PLANET = (f'<radialGradient id="planet" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#ddd6fe"/>'
          f'<stop offset=".45" stop-color="#7c6fd6"/><stop offset="1" stop-color="#1e1b4b"/></radialGradient>'
          f'{glow("halo", LILAC, ((0, .5), (.4, .12), (1, 0)))}{glow("minthalo", MINT, ((0, .55), (.4, .12), (1, 0)))}')


def planet(x, y, r):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 2.2}" fill="url(#halo)"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#planet)"/>'
            f'<circle cx="{x}" cy="{y}" r="{r + 5}" fill="none" stroke="{LILAC}" stroke-opacity=".25"/>')


def ellipse_path(cx, cy, rx, ry):
    return f"M{cx - rx} {cy}a{rx} {ry} 0 1 0 {2 * rx} 0a{rx} {ry} 0 1 0 {-2 * rx} 0Z"


def spin_css(cls, x, y, seconds, reverse=False):
    return (f".{cls}{{transform-origin:{x}px {y}px;animation:spin {seconds}s linear infinite"
            f"{' reverse' if reverse else ''}}}")


def tile_ctf():
    ax, ay, bx, by = 112, 122, 360, 112
    arc = f"M{ax + 26} {ay - 10}Q{(ax + bx) / 2} 18 {bx - 32} {by - 10}"
    T = 3.6  # one packet leaves every T/3 seconds; every third one carries the injection
    packets = "".join(
        f'<circle r="{3.4 if i == 2 else 2.4}" fill="{MINT if i == 2 else STAR}">'
        f'<animateMotion dur="{T}s" begin="-{i * T / 3:.1f}s" repeatCount="indefinite" path="{arc}"/></circle>'
        for i in range(3))
    cells = "".join(
        f'<rect x="{bx + 50 * math.cos(math.radians(a)) - 3:.1f}" y="{by + 50 * math.sin(math.radians(a)) - 3:.1f}" '
        f'width="6" height="6" rx="1" fill="{MINT if a == 90 else LILAC}" '
        + ('class="poison"' if a == 90 else 'opacity=".55"') + "/>" for a in range(0, 360, 45))
    scene = (f'<defs>{PLANET}</defs>'
             f'<path d="{arc}" fill="none" stroke="{LILAC}" stroke-opacity=".35" stroke-dasharray="3 5"/>'
             + planet(ax, ay, 20) + planet(bx, by, 26)
             + f'<g class="cells">{cells}</g>'
             + f'<circle class="hit" cx="{bx}" cy="{by}" r="30" fill="none" stroke="{MINT}" stroke-width="2"/>'
             + f'<g class="move">{packets}</g>'
             + f'<circle class="still" cx="{(ax + bx) / 2}" cy="{46}" r="3.4" fill="{MINT}"/>'
             + label("reader", ax, ay + 44, "mono", 12, MUTED, "middle")
             + label("executor", bx, by + 70, "mono", 12, MUTED, "middle")
             + label('{"role":"admin"}', (ax + bx) / 2, 32, "mono", 12, MINT, "middle", extra='opacity=".8"'))
    css = (spin_css("cells", bx, by, 18)
           + f".hit{{opacity:0;transform-origin:{bx}px {by}px;animation:hit {T}s ease-out infinite;"
             f"animation-delay:{T / 3:.1f}s}}"
           + "@keyframes hit{0%{opacity:.9;transform:scale(1)}35%{opacity:0;transform:scale(1.7)}100%{opacity:0}}"
           + ".poison{animation:tw 1.4s ease-in-out infinite alternate}")
    tile("tile-ctf", "Agent CTF challenges", "A2A injection  ·  memory poisoning", scene, css,
         "Agent red-teaming CTF challenges: an injected packet crosses an A2A link and hits the executor agent, "
         "whose memory holds one poisoned cell.", seed=11, top_row=True)


def tile_granzion():
    cx, cy = 240, 112
    orbits = [(70, 24, 7), (122, 42, 11), (178, 60, 17)]
    parts = [f'<defs>{PLANET}</defs><circle cx="{cx}" cy="{cy}" r="46" fill="url(#halo)"/>',
             f'<circle cx="{cx}" cy="{cy}" r="5" fill="#fff"/>']
    moving = []
    for i, (rx, ry, secs) in enumerate(orbits):
        path = ellipse_path(cx, cy, rx, ry)
        parts.append(f'<path d="{path}" fill="none" stroke="{LILAC}" stroke-opacity=".22"/>')
        forged = i == 1
        card_colour = MINT if forged else LILAC
        # The forged agent card is split along the same cut as "break" in the header.
        card = (f'<rect x="8" y="-5" width="14" height="4.4" rx="1" fill="{card_colour}" '
                f'transform="translate({2.5 if forged else 0} 0)"/>'
                f'<rect x="8" y=".6" width="14" height="4.4" rx="1" fill="{card_colour}"/>')
        body = (f'<circle r="{5 if i else 4}" fill="url(#planet)"/>'
                + (f'<circle r="14" fill="url(#minthalo)"/>' if forged else "") + card)
        moving.append(f'<g>{body}<animateMotion dur="{secs}s" begin="-{i * 2.3:.1f}s" '
                      f'repeatCount="indefinite" path="{path}"/></g>')
    tilt = f'transform="rotate(-10 {cx} {cy})"'
    scene = (f'<g {tilt}>{"".join(parts)}<g class="move">{"".join(moving)}</g>'
             f'<g class="still"><g transform="translate({cx + 122} {cy})"><circle r="14" fill="url(#minthalo)"/>'
             f'<rect x="10.5" y="-5" width="14" height="4.4" rx="1" fill="{MINT}"/>'
             f'<rect x="8" y=".6" width="14" height="4.4" rx="1" fill="{MINT}"/></g></g></g>'
             )
    tile("tile-granzion", "Granzion Labs", "2 merged PRs  ·  4 attack scenarios", scene, "",
         "Granzion Labs: agents orbit an orchestrator, and one of them carries a forged agent card.", seed=23,
         side="right", top_row=True)


def tile_redcalibur():
    cx, cy, R, T = 240, 114, 86, 6
    rng = random.Random(5)
    dots, secrets = [], []
    while len(dots) + len(secrets) < 30:
        a, r = rng.uniform(0, 2 * math.pi), R * math.sqrt(rng.uniform(.04, .92))
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        if len(secrets) < 5 and r > 30:
            secrets.append((x, y, math.degrees(a) % 360))
        else:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="{LILAC}" opacity=".45"/>')
    found = []
    for x, y, ang in secrets:
        delay = ang / 360 * T - T  # negative, so the sweep and the ping are in phase from the first frame
        style = f'style="animation-delay:{delay:.2f}s"'
        found.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{MINT}"/>'
                     f'<circle class="ping" cx="{x:.1f}" cy="{y:.1f}" r="7" fill="none" stroke="{MINT}" {style}/>'
                     f'<rect class="redact" x="{x + 6:.1f}" y="{y - 2.5:.1f}" width="18" height="5" rx="1" '
                     f'fill="{LILAC}" {style}/>')
    sweep = "".join(
        f'<path d="M{cx} {cy}L{cx + R * math.cos(math.radians(-a)):.1f} {cy + R * math.sin(math.radians(-a)):.1f}'
        f'A{R} {R} 0 0 1 {cx + R * math.cos(math.radians(-a + 5)):.1f} {cy + R * math.sin(math.radians(-a + 5)):.1f}Z" '
        f'fill="{MINT}" opacity="{.28 * (1 - a / 40):.3f}"/>' for a in range(0, 40, 5))
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LILAC}" stroke-opacity=".2"/>'
                    for r in (R / 3, 2 * R / 3, R))
    scene = (rings
             + f'<path d="M{cx - R} {cy}H{cx + R}M{cx} {cy - R}V{cy + R}" stroke="{LILAC}" stroke-opacity=".12"/>'
             + "".join(dots)
             + f'<g class="sweep">{sweep}<path d="M{cx} {cy}H{cx + R}" stroke="{MINT}" stroke-opacity=".8"/></g>'
             + "".join(found))
    css = (spin_css("sweep", cx, cy, T)
           + f".ping{{transform-box:fill-box;transform-origin:center;opacity:0;animation:ping {T}s ease-out infinite}}"
           + "@keyframes ping{0%{opacity:1;transform:scale(.4)}25%{opacity:0;transform:scale(1.8)}100%{opacity:0}}"
           + f".redact{{animation:redact {T}s linear infinite}}"
           + "@keyframes redact{0%{opacity:0}6%{opacity:.85}85%{opacity:.85}100%{opacity:0}}")
    tile("tile-redcalibur", "RedCalibur 2.0", "exposure workbench  ·  KEV + EPSS", scene, css,
         "RedCalibur 2.0: a radar sweep finds exposed secrets on a developer machine and redacts each one.", seed=37)


def tile_crucible():
    cx, cy, T = 240, 112, 8
    a, b = ellipse_path(cx, cy, 160, 46), ellipse_path(cx, cy, 160, 46)
    check = f"M{cx + 18} {cy - 30}l5 5 10 -11"
    scene = (f'<defs>{PLANET}</defs><circle cx="{cx}" cy="{cy}" r="42" fill="url(#halo)"/>'
             f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="#fff"/>'
             f'<g transform="rotate(-16 {cx} {cy})"><path d="{a}" fill="none" stroke="{LILAC}" stroke-opacity=".45"/>'
             f'<g class="move"><circle r="4.5" fill="url(#planet)"><animateMotion dur="{T}s" '
             f'repeatCount="indefinite" path="{a}"/></circle></g></g>'
             f'<g class="rival" transform="rotate(16 {cx} {cy})"><path d="{b}" fill="none" stroke="{MINT}" '
             f'stroke-opacity=".6" stroke-dasharray="4 4"/><g class="move"><circle r="4.5" fill="{MINT}">'
             f'<animateMotion dur="{T}s" begin="-{T / 2}s" repeatCount="indefinite" path="{b}"/></circle></g></g>'
             f'<path class="verdict" d="{check}" fill="none" stroke="{MINT}" stroke-width="2.4" '
             f'stroke-linecap="round" stroke-linejoin="round"/>'
             + label("claim", cx, cy + 26, "mono", 12, MUTED, "middle")
             + label("rival", cx + 150, cy + 64, "mono", 12, MINT, "middle", extra='class="rival"'))
    css = (f".rival{{animation:falsify {T}s ease-in-out infinite}}"
           "@keyframes falsify{0%,40%{opacity:1}55%,88%{opacity:.1}100%{opacity:1}}"
           f".verdict{{opacity:0;animation:verdict {T}s ease-in-out infinite}}"
           "@keyframes verdict{0%,48%{opacity:0}58%,86%{opacity:1}96%,100%{opacity:0}}"
           "@media (prefers-reduced-motion:reduce){.verdict{opacity:1}.rival{opacity:.25}}")
    tile("tile-crucible", "Crucible", "falsification gate for AI agents", scene, css,
         "Crucible: a claim with two rival explanations in orbit; the rival is tested, fades, and the claim "
         "gets a verdict.", seed=41, side="right")


# ---------------------------------------------------------------- Team Hunter as Orion

ORION = {  # name: (right ascension in hours, declination in degrees, magnitude, colour)
    "Betelgeuse": (5.919, 7.41, .5, "#ffb38a"), "Bellatrix": (5.419, 6.35, 1.64, "#dbe6ff"),
    "Meissa": (5.585, 9.93, 3.39, "#dbe6ff"), "Alnitak": (5.679, -1.94, 1.77, "#e6edff"),
    "Alnilam": (5.604, -1.20, 1.69, "#e6edff"), "Mintaka": (5.533, -.30, 2.23, "#e6edff"),
    "Saiph": (5.796, -9.67, 2.06, "#e6edff"), "Rigel": (5.242, -8.20, .13, "#cfe0ff")}
ORION_LINES = [("Meissa", "Betelgeuse"), ("Meissa", "Bellatrix"), ("Betelgeuse", "Bellatrix"),
               ("Betelgeuse", "Alnitak"), ("Bellatrix", "Mintaka"), ("Alnitak", "Alnilam"),
               ("Alnilam", "Mintaka"), ("Alnitak", "Saiph"), ("Mintaka", "Rigel")]


def hunter():
    W, H = 1000, 280
    ox, oy, scale = 186, 124, 9  # sky centre on the plate, and pixels per degree

    def at(name):
        ra, dec, _, _ = ORION[name]
        return ox - (ra - 5.58) * 15 * scale, oy - dec * scale  # east is to the left on a sky chart

    lines = []
    for a, b in ORION_LINES:
        (x1, y1), (x2, y2) = at(a), at(b)
        n = math.hypot(x2 - x1, y2 - y1)
        lines.append(f'<path class="draw" d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke="{LILAC}" '
                     f'stroke-opacity=".45" stroke-dasharray="{n:.1f}" style="--n:{n:.1f}"/>')
    orion = []
    for name, (_, _, mag, colour) in ORION.items():
        x, y = at(name)
        r = 5.4 - 1.15 * mag
        orion.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 4.5:.1f}" fill="url(#starglow)"/>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{colour}"/>')
    stats = [(400, "8th", "in India on CTFtime", "for the 2026 season"),
             (580, "50+", "CTFs played", "with Team Hunter"),
             (766, "200+", "players at L3m0nCTF", "2025, which I led")]
    right = "".join(label(big, x, 150, "serif", 72, TITLE) + label(l1, x + 2, 182, "mono", 14, MUTED)
                    + label(l2, x + 2, 202, "mono", 14, MUTED) for x, big, l1, l2 in stats)
    body = (f'<defs>{glow("starglow", "#dbe6ff", ((0, .45), (.3, .12), (1, 0)))}'
            f'{glow("neb", VIOLET, ((0, .22), (1, 0)))}</defs>'
            + f'<ellipse cx="{ox}" cy="{oy}" rx="220" ry="170" fill="url(#neb)"/>'
            + stars(3, W, H, 150, 26, keep_out=[(390, 70, 960, 250)])
            + plate_ticks(W, H)
            + f'<g fill="none">{"".join(lines)}</g>' + "".join(orion)
            + label("TEAM HUNTER", ox, H - 34, "mono", 14, LILAC, "middle", 5)
            + label("CAPTURE THE FLAG", 402, 70, "mono", 14, LILAC, track=5)
            + right
            + label("best finishes: CREST 3rd, CryptoNite 5th", 402, 240, "mono", 13, LILAC))
    css = (".draw{stroke-dashoffset:0;animation:draw 2.6s ease-out both}"
           "@keyframes draw{from{stroke-dashoffset:var(--n)}to{stroke-dashoffset:0}}")
    frame("hunter", W, H, body, css,
          "Team Hunter, drawn as Orion the hunter. 8th in India on CTFtime for 2026, 50+ CTFs played, "
          "200+ players at L3m0nCTF 2025.")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    hero()
    tile_ctf()
    tile_granzion()
    tile_redcalibur()
    tile_crucible()
    hunter()
