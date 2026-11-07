import os
import cv2
import numpy as np
import networkx as nx                                       # NEW 9
from build_graph import build_graph, RES                   # NEW 1: reuse the graph code


def order_road(slab, k):                                   # NEW 2
    """Pixels of road k as an ordered list of (x, y), from one end to the other."""
    ys, xs = np.nonzero(slab == k)                         # NEW 2: the pile of pixels of this road
    pixels = set(zip(xs.tolist(), ys.tolist()))            # NEW 2

    def farthest(start):                                   # NEW 3: spread out step by step (BFS)
        parent = {start: None}                             # NEW 3: remembers where we came from
        queue = [start]                                    # NEW 3
        last = start                                       # NEW 3
        for p in queue:                                    # NEW 3
            last = p                                       # NEW 3: the last pixel reached is the farthest
            x, y = p                                       # NEW 3
            for dx in (-1, 0, 1):                          # NEW 3
                for dy in (-1, 0, 1):                      # NEW 3
                    q = (x + dx, y + dy)                   # NEW 3: a neighbour pixel
                    if q in pixels and q not in parent:    # NEW 3: on the road and not visited yet
                        parent[q] = p                      # NEW 3
                        queue.append(q)                    # NEW 3
        return last, parent                                # NEW 3

    start = next(iter(pixels))                             # NEW 4: any pixel of the road
    end_a, _ = farthest(start)                             # NEW 4: walk 1 finds end A
    end_b, parent = farthest(end_a)                        # NEW 4: walk 2 from A finds end B
    path = []                                              # NEW 4
    p = end_b                                              # NEW 4
    while p is not None:                                   # NEW 4: walk back from B to A
        path.append(p)                                     # NEW 4
        p = parent[p]                                      # NEW 4
    return path[::-1], len(pixels)                         # NEW 4: flip so it runs A to B


def order_all_roads(G, slab):                              # NEW 7
    """For every edge of the graph, the ordered pixels of its road. Returns {(u, v, key): path}."""
    roads = {}                                             # NEW 7
    for u, v, key, d in G.edges(keys=True, data=True):     # NEW 7: every road in the graph
        path, total = order_road(slab, d["seg"])           # NEW 7: reuse Piece 2
        roads[(u, v, key)] = (path, total)                 # NEW 7
    return roads                                           # NEW 7


def build_strokes(G, roads):                               # NEW 10
    """One ordered (x, y) list per connected piece, pieces sorted left to right."""
    pieces = [G.subgraph(c).copy() for c in nx.connected_components(G)]      # NEW 10: split into pieces
    pieces.sort(key=lambda P: min(G.nodes[n]["pos"][0] for n in P))          # NEW 10: left to right
    strokes, report = [], []                               # NEW 10
    for P in pieces:                                       # NEW 10
        if not nx.is_eulerian(P):                          # NEW 10: every degree even and connected?
            print("   piece is NOT Eulerian, skipped. Degrees:", sorted(dict(P.degree()).values()))
            continue
        stroke, used, max_gap = [], [], 0.0                # NEW 10
        for u, v, key in nx.eulerian_circuit(P, keys=True):          # NEW 10: roads in walking order
            if (u, v, key) in roads:                       # NEW 10: find this road's ordered points
                path = roads[(u, v, key)][0]               # NEW 10
            else:                                          # NEW 10
                path = roads[(v, u, key)][0]               # NEW 10
            ux, uy = G.nodes[u]["pos"]                     # NEW 10: where we are leaving from
            d_start = np.hypot(path[0][0] - ux, path[0][1] - uy)         # NEW 10
            d_end = np.hypot(path[-1][0] - ux, path[-1][1] - uy)         # NEW 10
            if d_end < d_start:                            # NEW 10: stored backwards, so flip it
                path = path[::-1]                          # NEW 10
            if stroke:                                     # NEW 10: gap between the last road and this one
                gap = np.hypot(stroke[-1][0] - path[0][0], stroke[-1][1] - path[0][1])
                max_gap = max(max_gap, float(gap))         # NEW 10
            stroke.extend(path)                            # NEW 10: glue it on
            used.append(P[u][v][key]["seg"])               # NEW 10
        once = sorted(used) == sorted(d["seg"] for _, _, d in P.edges(data=True))   # NEW 10: every road exactly once?
        strokes.append(stroke)                             # NEW 10
        report.append((len(used), P.number_of_edges(), once, max_gap))   # NEW 10
    return strokes, report                                 # NEW 10


if __name__ == "__main__":                                 # NEW 8: check EVERY road of each image
    for name in ["k01.png", "k02.png", "k03.png", "k04.png"]:
        print(name)
        result = build_graph(name)
        if result is None:
            continue
        G, slab, jlab = result
        roads = order_all_roads(G, slab)                   # NEW 8
        bad = 0                                            # NEW 8: roads with a jump or lost pixels
        for (u, v, key), (path, total) in roads.items():   # NEW 8
            jumps = sum(1 for (x1, y1), (x2, y2) in zip(path, path[1:])
                        if max(abs(x1 - x2), abs(y1 - y2)) > 1)
            if jumps > 0 or len(path) != total:            # NEW 8
                bad += 1                                   # NEW 8
                print("   CHECK THIS ROAD:", u, v, "key", key, "| pixels in road", total,
                      "| pixels in path", len(path), "| jumps", jumps)   # NEW 8
        print("   ALL ROADS TEST: roads", len(roads), "| roads with a problem", bad)   # NEW 8
        print("   shortest road", min(len(p) for p, t in roads.values()),
              "pixels | longest road", max(len(p) for p, t in roads.values()), "pixels")   # NEW 8

        strokes, report = build_strokes(G, roads)          # NEW 11: join the roads into strokes
        print("   STROKE TEST: strokes", len(strokes), "(pieces in the graph:", nx.number_connected_components(G), ")")   # NEW 11
        for i, (st, (n_used, n_edges, once, max_gap)) in enumerate(zip(strokes, report)):   # NEW 11
            print("   stroke", i + 1, "| points", len(st), "| roads used", n_used, "of", n_edges,
                  "| each road exactly once", once, "| biggest gap between roads", round(max_gap, 1), "px")   # NEW 11
