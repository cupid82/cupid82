"""Wrap the ASCII flower text in an SVG: real <text> characters, purple gradient,
and a slow "breathing" glow that travels down the flower line by line.

Why SVG and not a ```code block``` in the README?
  - A code block is always grey/white text on a grey box; GitHub strips colours.
  - An SVG keeps the characters as real text but lets us colour and animate them.
  - GitHub shows SVGs through an <img>, so scripts never run there, but CSS
    animations inside the SVG do.
"""
import sys
from xml.sax.saxutils import escape

TXT, OUT_DARK, OUT_LIGHT = sys.argv[1:4]

FONT = 10.0          # px
ADV = FONT * 0.6     # width of one monospace character
LINE = FONT * 1.15   # distance between rows (must match CELL_ASPECT in ascii_flower.py)
PAD = 8

THEMES = {
    "dark": ["#faf5ff", "#e9d5ff", "#d8b4fe", "#c4b5fd", "#a78bfa"],
    "light": ["#8b5cf6", "#7c3aed", "#6d28d9", "#5b21b6", "#4c1d95"],
}

lines = open(TXT, encoding="utf-8").read().rstrip("\n").split("\n")
cols = max(len(l) for l in lines)
W = round(cols * ADV + 2 * PAD)
H = round(len(lines) * LINE + 2 * PAD)


def build(stops, weight):
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">',
        '<title id="t">ASCII lily</title>',
        '<desc id="d">A lily drawn with ASCII characters in shades of purple.</desc>',
        "<defs>",
        f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="{W}" y1="0" x2="{W * 0.35:.0f}" y2="{H}">',
    ]
    for i, c in enumerate(stops):
        out.append(f'<stop offset="{i / (len(stops) - 1):.2f}" stop-color="{c}"/>')
    out += [
        "</linearGradient>",
        "<style>",
        "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;"
        f"font-size:{FONT}px;font-weight:{weight};white-space:pre;animation:b 7s ease-in-out infinite}}",
        "@keyframes b{0%,100%{opacity:.78}50%{opacity:1}}",
        "@media (prefers-reduced-motion:reduce){text{animation:none;opacity:.9}}",
        "</style>",
        "</defs>",
        '<g fill="url(#g)">',
    ]
    for r, line in enumerate(lines):
        body = line.lstrip(" ")
        if not body:
            continue
        lead = len(line) - len(body)
        x = PAD + lead * ADV
        y = PAD + (r + 0.85) * LINE
        # Negative delays: every row is already mid-animation on load, and each
        # row lags the one above it by 0.09s, so the glow rolls downwards.
        delay = r * 0.09 - 7
        out.append(
            f'<text x="{x:.1f}" y="{y:.1f}" textLength="{len(body) * ADV:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve" style="animation-delay:{delay:.2f}s">'
            f"{escape(body)}</text>"
        )
    out += ["</g>", "</svg>", ""]
    return "\n".join(out)


for path, theme in ((OUT_DARK, "dark"), (OUT_LIGHT, "light")):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(build(THEMES[theme], 700 if theme == 'light' else 400))
print(f"{W}x{H}px, {len(lines)} rows x {cols} cols")
