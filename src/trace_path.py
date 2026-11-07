import os
import cv2
import numpy as np
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
