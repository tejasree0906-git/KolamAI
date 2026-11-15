# piece_diag.py  -  usage: python piece_diag.py k10 k22 k05
import sys, cv2, numpy as np
for name in sys.argv[1:]:
    img = cv2.imread(f"results/skel_{name}.png", 0)
    n, lab, st, cen = cv2.connectedComponentsWithStats((img > 0).astype(np.uint8), connectivity=8)
    print(name, "skeleton pieces:", n - 1)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        print(f"   piece {i}: {a} px, box {w}x{h} at (x={x}, y={y})")