import csv, glob, os

rows = sorted(glob.glob(r"data\real\*.png"))
os.makedirs("data", exist_ok=True)
with open(r"data\labels.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["filename", "grid_size", "dots_expected", "quality"])
    for p in rows:
        w.writerow([os.path.basename(p), "", "", ""])
print("Made data\\labels.csv with", len(rows), "rows")