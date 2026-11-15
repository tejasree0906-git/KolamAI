# run_all.py (v2): run the pipeline on every picture in data/labels.csv
# Run:  python run_all.py baseline      (the word is a tag, so old results are NOT overwritten)
#       python run_all.py after_fix1
import csv, os, sys, time
import cv2

sys.path.insert(0, "src")
from pipeline import run_pipeline
from detect_dots import detect_dots

TAG = sys.argv[1] if len(sys.argv) > 1 else "run"
RESIZE = True      # True = same as the app (500 px wide)
SPEED = 40         # fast GIFs
OUT = os.path.join("results", "run_all_%s.csv" % TAG)
LOG = os.path.join("results", "run_all_%s_log.txt" % TAG)

os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

class Tee:                       # print on screen AND save to the log file
    def __init__(self, *s): self.s = s
    def write(self, t):
        for x in self.s: x.write(t)
    def flush(self):
        for x in self.s: x.flush()
logf = open(LOG, "w", encoding="utf-8")
sys.stdout = Tee(sys.__stdout__, logf)

with open(os.path.join("data", "labels.csv"), newline="") as f:
    labels = list(csv.DictReader(f))

rows = []
for r in labels:
    name = r["filename"]
    expected = int(r["dots_expected"])
    src = os.path.join("data", "real", name)
    img = cv2.imread(src)
    if img is None:
        rows.append([name, "", "", expected, "", "NO", "", "", "ERROR", "cannot open picture"])
        print(name, "ERROR cannot open")
        continue
    h0, w0 = img.shape[:2]
    path = src
    if RESIZE:
        img = cv2.resize(img, (500, int(h0 * 500 / w0)))
        path = os.path.join("uploads", name)
        cv2.imwrite(path, img)
    t0 = time.time()
    try:
        out = run_pipeline(path, SPEED)
        found = out["n_dots"]
        row = [name, w0, h0, expected, found, "YES" if found == expected else "NO",
               out["n_strands"], out["all_closed"], "OK", ""]
    except Exception as e:
        status = "STOPPED" if isinstance(e, ValueError) else "CRASH"
        try:                      # NEW in v2: still count the dots when a later stage stopped
            found = detect_dots(path)
        except Exception:
            found = ""
        row = [name, w0, h0, expected, found, "YES" if found == expected else "NO",
               "", "", status, str(e) if status == "STOPPED" else repr(e)]
    rows.append(row)
    print(name, row[8], "found", row[4], "of", expected, "| strands", row[6],
          "| closed", row[7], "|", row[9], "| %.0fs" % (time.time() - t0))

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["filename", "width", "height", "dots_expected", "dots_found",
                "dots_match", "strands", "all_closed", "status", "message"])
    w.writerows(rows)

n = len(rows)
dm = sum(1 for r in rows if r[5] == "YES")
ok = sum(1 for r in rows if r[8] == "OK")
print("\n=== SUMMARY (%s) ===" % TAG)
print("Pictures:", n)
print("Dot count correct:", dm, "of", n, "= %.0f%%" % (100 * dm / n))
print("Whole pipeline OK:", ok, "of", n, "= %.0f%%" % (100 * ok / n))
for g, lo, hi in [("3x3 (k01-k15)", 0, 15), ("2-4-4-2 (k16-k20)", 15, 20), ("1-3-5-3-1 (k21-k25)", 20, 25)]:
    part = rows[lo:hi]
    print(g, ": dots correct", sum(1 for r in part if r[5] == "YES"), "of", len(part),
          "| pipeline OK", sum(1 for r in part if r[8] == "OK"))
print("Saved:", OUT, "and", LOG)