"""Turn the reference lily image into real ASCII art (text), then into SVGs.

Idea: the reference picture is itself made of tiny characters. If we blur it,
each region becomes a smooth "ink density". We then cut the picture into a grid
of cells (one cell = one character on screen) and pick a character whose own
ink density matches that cell: ' ' is empty, '@' is the densest.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

SRC, OUT_TXT = sys.argv[1], sys.argv[2]
COLS = int(sys.argv[3]) if len(sys.argv) > 3 else 96

# Characters ordered from least ink to most ink.
RAMP = " .:-=+*#%@"

# A monospace glyph is roughly 0.6 em wide. We will draw rows 1.15 em apart,
# so one cell is 1.15/0.6 ~= 1.92 times taller than it is wide.
CELL_ASPECT = 1.15 / 0.6

img = Image.open(SRC).convert("L")
a = np.asarray(img)
ys, xs = np.where(a > 60)
pad = 6
box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0),
       min(xs.max() + pad, img.width), min(ys.max() + pad, img.height))
img = img.crop(box)

# Blur so individual glyph strokes merge into a density field.
dens = np.asarray(img.filter(ImageFilter.GaussianBlur(2.2)), dtype=np.float32)

cw = img.width / COLS
ch = cw * CELL_ASPECT
rows = int(img.height / ch)

grid = np.zeros((rows, COLS), dtype=np.float32)
for r in range(rows):
    for c in range(COLS):
        y0, y1 = int(r * ch), int((r + 1) * ch)
        x0, x1 = int(c * cw), int((c + 1) * cw)
        grid[r, c] = dens[y0:y1, x0:x1].mean()

# Normalise: treat the 99th percentile of the lit cells as "full ink".
lit = grid[grid > 6]
hi = np.percentile(lit, 99)
g = np.clip(grid / hi, 0, 1)
# A gamma below 1 lifts faint petal interiors so they read as texture, not holes.
g = g ** 0.75
g[grid < 7] = 0  # true background stays empty

lines = []
for r in range(rows):
    s = "".join(RAMP[min(int(v * (len(RAMP) - 1) + 0.5), len(RAMP) - 1)] for v in g[r])
    lines.append(s.rstrip())

# Trim blank rows top and bottom.
while lines and not lines[0].strip():
    lines.pop(0)
while lines and not lines[-1].strip():
    lines.pop()

with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(f"{COLS} cols x {len(lines)} rows -> {OUT_TXT}")
