import os
import cv2
import numpy as np
try:
    import networkx as nx
except ImportError:
    raise SystemExit("networkx is missing. Run this in your terminal: pip install networkx")

MERGE = 9   # junction pixels closer than about this many pixels become ONE junction

# find the results folder: look in the current folder, then next to this file, then one level up
HERE = os.path.dirname(os.path.abspath(__file__))
for base in (os.getcwd(), HERE, os.path.dirname(HERE)):
    if os.path.isdir(os.path.join(base, "results")):
        RES = os.path.join(base, "results")
        break
else:
    raise SystemExit("Cannot find the results folder. Run detect_dots.py first, then run this file.")


def build_graph(name):
    path = os.path.join(RES, "skel_" + name)
    img = cv2.imread(path, 0)
    if img is None:
        print("   cannot open", path, "- run detect_dots.py first")
        return None
    skel = img > 0                                             # True where the 1-pixel line is
    s = skel.astype(np.uint8)

    # STEP 1: count the neighbours of every pixel (3x3 box sum, minus the pixel itself)
    nb = cv2.filter2D(s, -1, np.ones((3, 3), np.float32), borderType=cv2.BORDER_CONSTANT) - s
    endpoints = skel & (nb == 1)                               # 1 neighbour  = dead end
    junction_px = skel & (nb >= 3)                             # 3+ neighbours = crossroad

    # STEP 2: a crossing leaves several junction pixels close together, merge them into one
    zone = cv2.dilate(junction_px.astype(np.uint8), np.ones((MERGE, MERGE), np.uint8))
    nj, jlab, _, jcent = cv2.connectedComponentsWithStats(zone, connectivity=8)

    # STEP 3: cut the junction zones out, what is left are the line segments (the roads)
    segs = skel & (zone == 0)
    ns, slab = cv2.connectedComponents(segs.astype(np.uint8), connectivity=8)

    print("   piece 1: endpoint pixels", int(endpoints.sum()), "| junction pixels", int(junction_px.sum()))
    print("   piece 2: junctions after merge", nj - 1)
    print("   piece 3: roads (segments)", ns - 1)

    # STEP 4: nodes = junctions + endpoints
    G = nx.MultiGraph()                                        # allows loops and parallel edges
    for j in range(1, nj):
        G.add_node("J%d" % j, pos=(float(jcent[j][0]), float(jcent[j][1])))
    epid = np.zeros(skel.shape, int)                           # numbers the endpoint pixels
    ys, xs = np.nonzero(endpoints)
    for k, (y, x) in enumerate(zip(ys, xs)):
        epid[y, x] = k + 1
        G.add_node("E%d" % k, pos=(float(x), float(y)))

    # STEP 5: edges = segments, joined to the nodes at their two ends
    for k in range(1, ns):
        seg = (slab == k).astype(np.uint8)
        grown = cv2.dilate(seg, np.ones((3, 3), np.uint8))     # grow 1 pixel to touch the junction zone
        js = set(int(v) for v in np.unique(jlab[grown > 0])) - {0}   # junctions this segment touches
        es = set(int(v) for v in np.unique(epid[seg > 0])) - {0}     # endpoints inside this segment
        ends = ["J%d" % j for j in sorted(js)] + ["E%d" % (e - 1) for e in sorted(es)]
        if len(ends) == 1 and not es:                          # leaves a junction and comes back = loop
            ends = ends * 2
        if len(ends) == 2:
            G.add_edge(ends[0], ends[1], seg=k)
        else:
            print("   segment", k, "has", len(ends), "ends, skipped")

    # picture to check with your own eyes: green = junction, blue = endpoint
    out = cv2.cvtColor(cv2.dilate(s, np.ones((3, 3), np.uint8)) * 255, cv2.COLOR_GRAY2BGR)
    for node, d in G.nodes(data=True):
        color = (0, 255, 0) if node.startswith("J") else (255, 0, 0)
        cv2.circle(out, (int(d["pos"][0]), int(d["pos"][1])), 12, color, 3)
    cv2.imwrite(os.path.join(RES, "graph_" + name), out)

    n_end = sum(1 for n in G if n.startswith("E"))
    print("   junctions:", nj - 1, "endpoints:", n_end, "edges:", G.number_of_edges(),
          "pieces:", nx.number_connected_components(G))
    print("   degrees:", sorted(dict(G.degree()).values()))
    return G, slab, jlab                                       # NEW 1: also give back the road labels and junction labels


if __name__ == "__main__":
    for name in ["k01.png", "k02.png", "k03.png", "k04.png"]:
        print(name)
        result = build_graph(name)
        if result is None:                                     # NEW 2
            continue                                           # NEW 2
        G, slab, jlab = result                                 # NEW 2
        for n, (u, v, key, d) in enumerate(G.edges(keys=True, data=True)):   # NEW 3: first 3 roads only
            if n == 3:                                         # NEW 3
                break                                          # NEW 3
            print("   edge", u, v, "key", key, "seg", d["seg"], "pixels", int((slab == d["seg"]).sum()))   # NEW 3