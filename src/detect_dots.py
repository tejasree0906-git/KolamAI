import cv2, os

def detect_dots(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)

    count = 0
    dot_ids = []                                   # NEW: shape numbers that are dots
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        roundness = area / (3.14159 * (max(w, h) / 2) ** 2)
        if 150 < area < 4000 and 0.6 < w / h < 1.5 and roundness > 0.5:
            cx, cy = centroids[i]
            r = int(max(w, h) / 2) + 8
            cv2.circle(img, (int(cx), int(cy)), r, (0, 0, 255), 3)
            count += 1
            dot_ids.append(i)                      # NEW: remember this dot

    curve = bw.copy()                              # NEW: photocopy, erase on the copy
    for i in dot_ids:                              # NEW
        curve[labels == i] = 0                     # NEW: rub out every dot

    os.makedirs("results", exist_ok=True)
    name = os.path.basename(path)
    cv2.imwrite("results/" + name, img)
    cv2.imwrite("results/curve_" + name, curve)    # NEW: save the curve-only picture
    return count

for name in ["k01.png", "k02.png", "k03.png", "k04.png"]:
    print(name, "-> found", detect_dots("data/real/" + name), "expected 9")