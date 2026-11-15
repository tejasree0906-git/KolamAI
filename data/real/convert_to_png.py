import cv2, glob, os

SRC = r"D:\Downloads\jpeg folder"
DST = r"D:\KolamAI\KolamAI\data\real"

os.makedirs(DST, exist_ok=True)
files = sorted(glob.glob(os.path.join(SRC, "*.jpeg")) +
               glob.glob(os.path.join(SRC, "*.jpg")))

done = 0
for f in files:
    name = os.path.splitext(os.path.basename(f))[0]
    out = os.path.join(DST, name + ".png")
    if os.path.exists(out):
        print("SKIP (already there):", out)
        continue
    img = cv2.imread(f)
    if img is None:
        print("CANNOT OPEN:", f)
        continue
    cv2.imwrite(out, img)
    print("OK:", name + ".jpeg ->", name + ".png")
    done += 1

print("Finished. Converted:", done, "of", len(files))
