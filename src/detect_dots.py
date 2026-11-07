import cv2, os, json                              # NEW 26: json writes the dots file
import numpy as np                                 # NEW 2: for an empty black picture
from skimage.morphology import skeletonize         # NEW 3: thins a line to 1 pixel

def detect_dots(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)

    count = 0
    dot_ids = []
    dots = []                                              # NEW 27: centre and size of every dot
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        roundness = area / (3.14159 * (max(w, h) / 2) ** 2)
        if 150 < area < 4000 and 0.6 < w / h < 1.5 and roundness > 0.5:
            cx, cy = centroids[i]
            r = int(max(w, h) / 2) + 8
            cv2.circle(img, (int(cx), int(cy)), r, (0, 0, 255), 3)
            count += 1
            dot_ids.append(i)
            dots.append([int(round(cx)), int(round(cy)), r])        # NEW 28: remember this dot

    # PIECE 1: remove the dots, keep only the curve
    curve = bw.copy()
    for i in dot_ids:
        curve[labels == i] = 0

    # NEW 2: keep only real curve pieces
    H, W = curve.shape                                       # NEW 2: picture height and width
    n2, labels2, stats2, _ = cv2.connectedComponentsWithStats(curve, connectivity=8)  # NEW 2
    clean = np.zeros_like(curve)                             # NEW 2: empty black picture
    kept = 0                                                 # NEW 2
    for j in range(1, n2):                                   # NEW 2
        x, y, w, h, area = stats2[j]                         # NEW 2
        touches_edge = x == 0 or y == 0 or x + w == W or y + h == H   # NEW 2
        if area >= 100 and not touches_edge:                 # NEW 2: big enough, not the frame
            clean[labels2 == j] = 255                        # NEW 2: keep this piece
            kept += 1                                        # NEW 2
    print("   curve pieces kept:", kept, "dropped:", (n2 - 1) - kept)   # NEW 2

    # NEW 3: thin the clean curve to a 1-pixel line
    skel = skeletonize(clean > 0)                            # NEW 3: True/False picture in, thinned True/False picture out
    skel_img = (skel * 255).astype(np.uint8)                 # NEW 3: back to 0/255 so we can save it
    print("   curve pixels:", int((clean > 0).sum()), "-> skeleton pixels:", int(skel.sum()))   # NEW 3

    os.makedirs("results", exist_ok=True)
    name = os.path.basename(path)
    cv2.imwrite("results/" + name, img)
    cv2.imwrite("results/curve_" + name, curve)
    cv2.imwrite("results/clean_" + name, clean)              # NEW 2: save the cleaned picture
    cv2.imwrite("results/skel_" + name, skel_img)            # NEW 3: save the skeleton
    with open("results/dots_" + os.path.splitext(name)[0] + ".json", "w") as f:   # NEW 29: dots file, e.g. results/dots_k01.json
        json.dump(dots, f)                                   # NEW 29: list of [x, y, radius]
    return count

for name in ["k01.png", "k02.png", "k03.png", "k04.png"]:
    print(name, "-> found", detect_dots("data/real/" + name), "expected 9")