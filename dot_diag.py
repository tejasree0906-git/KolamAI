# dot_diag.py: show WHY a shape is (not) accepted as a dot.
# Run:  python dot_diag.py k17      (uses uploads\k17.png, the 500 px picture made by run_all.py)
import sys, os, math
import cv2

name = sys.argv[1] if len(sys.argv) > 1 else "k17"
path = os.path.join("uploads", name + ".png")
img = cv2.imread(path)
if img is None:
    sys.exit("Cannot open " + path + ". Run run_all.py first.")
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(grey, (5, 5), 0)
t, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
n, labels, stats, cents = cv2.connectedComponentsWithStats(bw, connectivity=8)
print(name, "size", img.shape[1], "x", img.shape[0], "| Otsu cut-off", t, "| shapes", n - 1)
print("Limits: area 150..4000 | w/h 0.6..1.5 | roundness > 0.5\n")
print("id  area   w   h   w/h  round  A R C  verdict")
rows = []
for i in range(1, n):
    x, y, w, h, a = stats[i]
    if a < 20:
        continue
    ratio = w / h
    rnd = a / (math.pi * (max(w, h) / 2) ** 2)
    A = 150 < a < 4000
    R = 0.6 < ratio < 1.5
    C = rnd > 0.5
    rows.append((a, i, w, h, ratio, rnd, A, R, C))
for a, i, w, h, ratio, rnd, A, R, C in sorted(rows, reverse=True)[:30]:
    v = "DOT" if (A and R and C) else "no"
    print("%2d %5d %3d %3d %5.2f %5.2f  %s %s %s  %s" % (i, a, w, h, ratio, rnd,
          "Y" if A else "n", "Y" if R else "n", "Y" if C else "n", v))
print("\nShapes passing all 3 tests:", sum(1 for r in rows if r[6] and r[7] and r[8]))
print("A = area ok, R = width/height ok, C = roundness ok. 'n' shows which test rejects a shape.")
