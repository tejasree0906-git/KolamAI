# spur_diag.py  -  usage: python spur_diag.py k22
import sys
import cv2
import numpy as np
from scipy.ndimage import convolve

name = sys.argv[1]
img = cv2.imread(f"results/skel_{name}.png", 0)
sk = img > 127
if sk.mean() > 0.5:          # white background -> flip
    sk = ~sk

k = np.ones((3, 3), int)
nb = (convolve(sk.astype(int), k, mode="constant") - 1) * sk

ends = list(zip(*np.where(nb == 1)))
print(name, "endpoints:", len(ends))

def neighbours(y, x):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if (dy or dx) and 0 <= y+dy < sk.shape[0] and 0 <= x+dx < sk.shape[1]:
                if sk[y+dy, x+dx]:
                    yield (y+dy, x+dx)

for (y, x) in ends:
    seen = {(y, x)}
    cur = (y, x)
    length = 0
    why = "dead end"
    while True:
        nxt = [p for p in neighbours(*cur) if p not in seen]
        if not nxt:
            why = "reached another end"
            break
        cur = nxt[0]
        seen.add(cur)
        length += 1
        if nb[cur] >= 3:
            why = "reached junction"
            break
    print(f"  endpoint at (x={x}, y={y}): walk {length} px, {why}")