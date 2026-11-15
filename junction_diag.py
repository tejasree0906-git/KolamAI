# junction_diag.py  -  usage: python junction_diag.py k10 248 181 248 321
import sys
sys.path.insert(0, "src")
from build_graph import build_graph
name = sys.argv[1]
spots = [(int(sys.argv[i]), int(sys.argv[i + 1])) for i in range(2, len(sys.argv), 2)]
G, slab, jlab = build_graph(name + ".png")
print()
for (sx, sy) in spots:
    print(f"== near (x={sx}, y={sy})")
    for n, d in G.nodes(data=True):
        px, py = d["pos"]
        if ((px - sx) ** 2 + (py - sy) ** 2) ** 0.5 < 45:
            print(f"  node {n} at (x={px:.0f}, y={py:.0f}) degree {G.degree(n)}")
            for u, v, k, e in G.edges(n, keys=True, data=True):
                length = int((slab == e["seg"]).sum())
                print(f"     edge {u}-{v} seg {e['seg']} length {length} px")
