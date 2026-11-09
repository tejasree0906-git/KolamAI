import os                                                    # NEW 74
import sys                                                   # NEW 74
HERE = os.path.dirname(os.path.abspath(__file__))            # NEW 74: the src folder
if HERE not in sys.path:                                     # NEW 74: so "import detect_dots" works from anywhere (the app lives in app/)
    sys.path.insert(0, HERE)                                 # NEW 74
import matplotlib                                            # NEW 75
matplotlib.use("Agg")                                        # NEW 75: draw without a window
import matplotlib.pyplot as plt                              # NEW 75
from matplotlib.animation import PillowWriter                # NEW 75
from detect_dots import detect_dots                          # NEW 76: your 4 stages, unchanged
from build_graph import build_graph, RES                     # NEW 76
from trace_path import order_all_roads, build_strands, save_path_data   # NEW 76
from animate_path import load_path_data, make_animation      # NEW 76


def run_pipeline(path, speed=15):                            # NEW 77
    """One picture in, results out. Raises ValueError with a friendly sentence when something is wrong.
    Returns a dictionary: dots picture, skeleton picture, GIF, and the counts."""
    name = os.path.basename(path)                            # NEW 77: for example "upload.png"
    stem = os.path.splitext(name)[0]                         # NEW 77: "upload"

    n_dots = detect_dots(path)                               # NEW 78: stage 1 and 2: dots + skeleton (saves files in results/)
    if n_dots == 0:                                          # NEW 78
        raise ValueError("I could not find any dots in this picture.")   # NEW 78

    result = build_graph(name)                               # NEW 79: stage 3: graph
    if result is None:                                       # NEW 79
        raise ValueError("I could not find a line pattern in this picture.")   # NEW 79
    G, slab, jlab = result                                   # NEW 79

    roads = order_all_roads(G, slab)                         # NEW 80: stage 4: path
    strands, report = build_strands(G, roads)                # NEW 80
    if not strands:                                          # NEW 80
        raise ValueError("I could not trace a drawing path in this picture.")   # NEW 80
    marks = [d["pos"] for n, d in G.nodes(data=True) if n.startswith("J")]   # NEW 80: crossing centres (the data file expects them)
    save_path_data(name, slab.shape, strands, marks)         # NEW 80: writes results/path_<stem>.json

    data = load_path_data(stem)                              # NEW 81: stage 5: animation
    fig, anim, n_frames = make_animation(data, speed=speed)  # NEW 81
    gif = os.path.join(RES, "anim_" + stem + ".gif")         # NEW 81
    anim.save(gif, writer=PillowWriter(fps=25))              # NEW 81
    plt.close(fig)                                           # NEW 81

    return {                                                 # NEW 82
        "dots_img": os.path.join(RES, name),                 # NEW 82: picture with red rings
        "skel_img": os.path.join(RES, "skel_" + name),       # NEW 82: skeleton picture
        "gif": gif,                                          # NEW 82
        "n_dots": n_dots,                                    # NEW 82
        "n_strands": len(strands),                           # NEW 82
        "all_closed": all(r[1] for r in report),             # NEW 82
    }                                                        # NEW 82


if __name__ == "__main__":                                   # NEW 83: python src/pipeline.py data/real/k03.png
    if len(sys.argv) < 2:                                    # NEW 83
        raise SystemExit("Usage: python src/pipeline.py data/real/k03.png")   # NEW 83
    out = run_pipeline(sys.argv[1])                          # NEW 83
    print("dots:", out["n_dots"], "| strands:", out["n_strands"], "| all closed:", out["all_closed"])   # NEW 83
    print("saved:", out["gif"])                              # NEW 83
