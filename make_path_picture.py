# make_path_picture.py
# Makes results/path_<name>.png from results/path_<name>.json.
# Only for the README picture. It does NOT change anything in src/.
# Run from the project root:  python make_path_picture.py k24

import json
import sys

import matplotlib
matplotlib.use("Agg")                       # draw without a window
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle

name = sys.argv[1] if len(sys.argv) > 1 else "k24"
with open(f"results/path_{name}.json") as f:
    data = json.load(f)

w, h = data["width"], data["height"]
fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_facecolor("#111111")
fig.patch.set_facecolor("#111111")
ax.set_xlim(0, w)
ax.set_ylim(h, 0)                           # y axis flipped, like a picture
ax.set_aspect("equal")
ax.axis("off")

for x, y, r in data["dots"]:                # dots, all the same size
    ax.add_patch(Circle((x, y), 9, color="#cccccc", zorder=2))

total = sum(len(s) for s in data["strands"])
cmap = plt.get_cmap("coolwarm")             # blue = start, red = end
count = 0
for si, strand in enumerate(data["strands"]):
    pts = np.array(strand, dtype=float)
    segs = np.stack([pts[:-1], pts[1:]], axis=1)
    colors = [cmap((count + i) / max(total - 1, 1)) for i in range(len(pts) - 1)]
    ax.add_collection(LineCollection(segs, colors=colors, linewidths=2.2, zorder=3))
    for i in range(0, len(pts), 150):       # a number every 150 points
        ax.text(pts[i][0], pts[i][1], str(count + i), color="white", fontsize=5, zorder=5)
    ax.add_patch(Circle(tuple(pts[0]), 12, fill=False, edgecolor="#00ff66", linewidth=2.5, zorder=6))
    print(f"strand {si + 1}: {len(pts)} points, starts at ({pts[0][0]:.0f}, {pts[0][1]:.0f})")
    count += len(pts)

for x, y in data["crossings"]:              # white ring on every crossing
    ax.add_patch(Circle((x, y), 7, fill=False, edgecolor="white", linewidth=1.5, zorder=4))

fig.savefig(f"results/path_{name}.png", facecolor=fig.get_facecolor())
print("saved results/path_%s.png" % name)
