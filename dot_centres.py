# dot_centres.py  -  usage: python dot_centres.py k10
import sys, cv2, numpy as np
name = sys.argv[1]
img = cv2.imread(f"uploads/{name}.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
_, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
n, lab, st, cen = cv2.connectedComponentsWithStats(bw, connectivity=8)
c = []
for i in range(1, n):
    x, y, w, h, a = st[i]
    rd = a / (3.14159 * (max(w, h) / 2) ** 2)
    if 100 < a < 4000 and 0.6 < w / h < 1.5 and rd > 0.5:
        c.append((i, a, w, h, float(cen[i][0]), float(cen[i][1])))
print(name, "candidates (area 100 to 4000):", len(c))
for i, a, w, h, cx, cy in c:
    print(f"  id {i:2d} area {a:4d} {w}x{h} centre (x={cx:.0f}, y={cy:.0f})")
print("pairs closer than 30 px:")
for p in range(len(c)):
    for q in range(p + 1, len(c)):
        d = ((c[p][4] - c[q][4]) ** 2 + (c[p][5] - c[q][5]) ** 2) ** 0.5
        if d < 30:
            print(f"  id {c[p][0]} and id {c[q][0]}: {d:.0f} px apart")