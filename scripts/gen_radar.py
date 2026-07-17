#!/usr/bin/env python3
"""Generate contribution-radar SVGs (dark + light) from GitHub contribution data.

Usage: GITHUB_TOKEN=... python scripts/gen_radar.py <outdir>
"""
import json
import math
import os
import sys
import urllib.request

USER = "PraneeshRV"
W, H = 900, 470
CX, CY = 450, 240
R_MIN, R_MAX = 62, 188
SWEEP_S = 12  # seconds per revolution

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""

THEMES = {
    "dark": {
        "bg": "#07070f", "grid": "#1c2340", "ring_label": "#5a648a",
        "beam": "#00e5ff", "beam_fade": "#00e5ff00", "blip": "#00e5ff",
        "blip_hot": "#ff2fd6", "dot_empty": "#232a4a", "text": "#9aa4c2",
        "accent": "#ff2fd6",
    },
    "light": {
        "bg": "#eff1f5", "grid": "#ccd0da", "ring_label": "#8c8fa1",
        "beam": "#40a02b", "beam_fade": "#40a02b00", "blip": "#40a02b",
        "blip_hot": "#df8e1d", "dot_empty": "#dce0e8", "text": "#4c4f69",
        "accent": "#8839ef",
    },
}


def fetch_days():
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    return days, cal["totalContributions"]


def polar(frac, weekday):
    theta = frac * 360 - 90  # start at top, clockwise
    r = R_MIN + (weekday / 6) * (R_MAX - R_MIN)
    rad = math.radians(theta)
    return theta, CX + r * math.cos(rad), CY + r * math.sin(rad)


def render(days, total, t):
    n = len(days)
    max_c = max((d["contributionCount"] for d in days), default=1) or 1
    busiest = max(days, key=lambda d: d["contributionCount"])
    parts = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Contribution radar — one blip per day, past year">',
        '<defs>',
        f'<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["beam_fade"]}"/><stop offset="1" stop-color="{t["beam"]}" stop-opacity="0.55"/></linearGradient>',
        '</defs>',
        f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
    ]
    # rings + cross-hairs
    for r in (R_MIN, (R_MIN + R_MAX) / 2, R_MAX):
        parts.append(f'<circle cx="{CX}" cy="{CY}" r="{r:.0f}" fill="none" stroke="{t["grid"]}" stroke-width="1"/>')
    parts.append(f'<path d="M{CX - R_MAX} {CY}H{CX + R_MAX}M{CX} {CY - R_MAX}V{CY + R_MAX}" stroke="{t["grid"]}" stroke-width="1"/>')

    # month ticks
    seen = set()
    for i, d in enumerate(days):
        mon = d["date"][:7]
        if mon in seen:
            continue
        seen.add(mon)
        theta, _, _ = polar(i / n, 6)
        rad = math.radians(theta)
        lx = CX + (R_MAX + 16) * math.cos(rad)
        ly = CY + (R_MAX + 16) * math.sin(rad)
        label = d["date"][5:7]
        parts.append(f'<text x="{lx:.0f}" y="{ly:.0f}" font-family="ui-monospace, Menlo, monospace" font-size="11" fill="{t["ring_label"]}" text-anchor="middle" dominant-baseline="middle">{label}</text>')

    # blips
    for i, d in enumerate(days):
        c = d["contributionCount"]
        _, x, y = polar(i / n, d["weekday"])
        if c == 0:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.2" fill="{t["dot_empty"]}"/>')
            continue
        frac = i / n
        begin = frac * SWEEP_S
        size = 1.6 + 2.6 * min(c / max_c, 1) ** 0.5
        color = t["blip_hot"] if c >= max_c * 0.6 else t["blip"]
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.1f}" fill="{color}" opacity="0.22">'
            f'<animate attributeName="opacity" values="1;0.22;0.22" keyTimes="0;0.25;1" dur="{SWEEP_S}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )

    # sweep beam (wedge + edge line), rotates once per SWEEP_S
    parts.append(
        f'<g><path d="M{CX} {CY} L{CX} {CY - R_MAX} A{R_MAX} {R_MAX} 0 0 1 {CX + R_MAX * math.sin(math.radians(34)):.1f} {CY - R_MAX * math.cos(math.radians(34)):.1f} Z" '
        f'fill="url(#beam)" opacity="0.35" transform="rotate(-34 {CX} {CY})"/>'
        f'<line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R_MAX}" stroke="{t["beam"]}" stroke-width="1.6" opacity="0.9"/>'
        f'<animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" dur="{SWEEP_S}s" repeatCount="indefinite"/></g>'
    )
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="3" fill="{t["beam"]}"/>')

    # HUD text
    mono = 'font-family="ui-monospace, Menlo, monospace"'
    parts += [
        f'<text x="24" y="34" {mono} font-size="14" fill="{t["accent"]}" letter-spacing="2">CONTRIBUTION RADAR</text>',
        f'<text x="24" y="54" {mono} font-size="11" fill="{t["text"]}">365d sweep · ring = weekday · blip = commits</text>',
        f'<text x="{W - 24}" y="34" {mono} font-size="12" fill="{t["text"]}" text-anchor="end">contacts: {total}</text>',
        f'<text x="{W - 24}" y="54" {mono} font-size="12" fill="{t["text"]}" text-anchor="end">peak: {busiest["contributionCount"]} on {busiest["date"]}</text>',
        '</svg>',
    ]
    return "\n".join(parts)


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "dist"
    os.makedirs(outdir, exist_ok=True)
    days, total = fetch_days()
    for name, theme in THEMES.items():
        path = os.path.join(outdir, f"radar-{name}.svg")
        with open(path, "w") as f:
            f.write(render(days, total, theme))
        print(f"wrote {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
