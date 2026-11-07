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


if __name__ == "__main__":                                 # NEW 5: test on the first road of each image
    for name in ["k01.png", "k02.png", "k03.png", "k04.png"]:
        print(name)
        result = build_graph(name)
        if result is None:
            continue
        G, slab, jlab = result
        u, v, key, d = next(iter(G.edges(keys=True, data=True)))
        path, total = order_road(slab, d["seg"])
        jumps = sum(1 for (x1, y1), (x2, y2) in zip(path, path[1:])
                    if max(abs(x1 - x2), abs(y1 - y2)) > 1)      # NEW 5: a jump = two points not touching
        print("   ORDER TEST: road", u, v, "seg", d["seg"], "| pixels in road", total,
              "| pixels in path", len(path), "| jumps", jumps)
        print("   first point", path[0], "| last point", path[-1])

        out = np.zeros(slab.shape + (3,), np.uint8)        # NEW 6: picture, blue = start, red = end
        for i, (x, y) in enumerate(path):                  # NEW 6
            shade = np.uint8([[int(255 * i / max(1, len(path) - 1))]])   # NEW 6
            out[y, x] = cv2.applyColorMap(shade, cv2.COLORMAP_JET)[0, 0]  # NEW 6
        out = cv2.dilate(out, np.ones((3, 3), np.uint8))   # NEW 6: thicker so you can see it
        cv2.imwrite(os.path.join(RES, "order_" + name), out)   # NEW 6
