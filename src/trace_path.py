import os
import json                                                 # NEW 22
import cv2
import numpy as np
import networkx as nx                                       # NEW 9
from build_graph import build_graph, RES                   # NEW 1: reuse the graph code

APART = 40                                                  # NEW 46: two strands must start at least 40 pixels apart


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


def _unit(v):                                              # NEW 14: shrink a direction to length 1
    v = np.asarray(v, dtype=float)                         # NEW 14
    n = np.hypot(v[0], v[1])                               # NEW 14
    return v / n if n > 1e-9 else np.zeros(2)              # NEW 14


def _turn(d1, d2):                                         # NEW 14: angle between two directions, 0 = straight on
    c = float(np.clip(np.dot(d1, d2), -1.0, 1.0))          # NEW 14
    return float(np.degrees(np.arccos(c)))                 # NEW 14


def road_ends(G, roads):                                   # NEW 15
    """Every road has 2 ends. For each end: which junction it touches, and which way it points INTO that junction."""
    ends = {}                                              # NEW 15
    for (u, v, key), (path, total) in roads.items():       # NEW 15
        k = min(15, len(path) - 1)                         # NEW 15: look about 15 pixels along to get the direction
        d_first = _unit(np.subtract(path[0], path[k]))     # NEW 15: at the first end, the road points into the junction like this
        d_last = _unit(np.subtract(path[-1], path[-1 - k]))   # NEW 15: same at the last end
        if u == v:                                         # NEW 15: loop road, both ends touch the same junction
            j_first, j_last = u, u                         # NEW 15
        else:                                              # NEW 15: which end is near u and which near v?
            pu, pv = G.nodes[u]["pos"], G.nodes[v]["pos"]  # NEW 15
            a = np.hypot(path[0][0] - pu[0], path[0][1] - pu[1]) + np.hypot(path[-1][0] - pv[0], path[-1][1] - pv[1])
            b = np.hypot(path[0][0] - pv[0], path[0][1] - pv[1]) + np.hypot(path[-1][0] - pu[0], path[-1][1] - pu[1])
            j_first, j_last = (u, v) if a <= b else (v, u)  # NEW 15
        ends[((u, v, key), 0)] = (j_first, d_first)        # NEW 15: end 0 = first point of the road
        ends[((u, v, key), 1)] = (j_last, d_last)          # NEW 15: end 1 = last point of the road
    return ends                                            # NEW 15


def pair_ends(ends):                                       # NEW 16
    """At every junction, pair the road ends that are most opposite (a straight pass). Returns {end: partner end}."""
    by_junction = {}                                       # NEW 16
    for e, (j, d) in ends.items():                         # NEW 16
        by_junction.setdefault(j, []).append(e)            # NEW 16
    partner = {}                                           # NEW 16
    for j, todo in by_junction.items():                    # NEW 16
        todo = list(todo)                                  # NEW 16
        while len(todo) >= 2:                              # NEW 16
            best = None                                    # NEW 16
            for a in range(len(todo)):                     # NEW 16
                for b in range(a + 1, len(todo)):          # NEW 16
                    score = float(np.dot(ends[todo[a]][1], ends[todo[b]][1]))   # NEW 16: -1 = exactly opposite = straight through
                    if best is None or score < best[0]:    # NEW 16
                        best = (score, todo[a], todo[b])   # NEW 16
            _, e1, e2 = best                               # NEW 16
            partner[e1], partner[e2] = e2, e1              # NEW 16
            todo.remove(e1)                                # NEW 16
            todo.remove(e2)                                # NEW 16
    return partner                                         # NEW 16


def bridge(a, c, b):                                       # NEW 17
    """Points that go from a to the junction centre c, then on towards b (no gap, one pixel steps)."""
    pts = []                                               # NEW 17
    for (p, q, include_last) in ((a, c, True), (c, b, False)):   # NEW 17
        n = int(max(abs(q[0] - p[0]), abs(q[1] - p[1])))   # NEW 17
        stop = n + 1 if include_last else n                # NEW 17
        for t in range(1, stop):                           # NEW 17
            pts.append((int(round(p[0] + (q[0] - p[0]) * t / n)), int(round(p[1] + (q[1] - p[1]) * t / n))))   # NEW 17
    return pts                                             # NEW 17


def build_strands(G, roads):                               # NEW 18
    """Straight-through drawing. Returns (strands, report). A strand is one closed line with no sharp turns."""
    ends = road_ends(G, roads)                             # NEW 18
    partner = pair_ends(ends)                              # NEW 18
    pieces = [G.subgraph(c).copy() for c in nx.connected_components(G)]       # NEW 18
    pieces.sort(key=lambda P: min(G.nodes[n]["pos"][0] for n in P))           # NEW 18: left to right
    strands, report = [], []                               # NEW 18
    for P in pieces:                                       # NEW 18
        piece_roads = [rid for rid in roads if rid[0] in P.nodes]             # NEW 18
        used = set()                                       # NEW 18
        while len(used) < len(piece_roads):                # NEW 18: one strand per round
            free = [(rid, e) for rid in piece_roads if rid not in used for e in (0, 1)]   # NEW 18
            xy = lambda re: roads[re[0]][0][0 if re[1] == 0 else -1]   # NEW 47: (x, y) of a road end
            apart = [re for re in free
                     if all(np.hypot(xy(re)[0] - s0[0][0], xy(re)[1] - s0[0][1]) > APART for s0 in strands)]   # NEW 48: ends far from every start so far
            pool = apart if apart else free                # NEW 49: if nothing is far enough, use any free end
            start = min(pool, key=lambda re: (xy(re)[1], xy(re)[0]))   # NEW 18: top-most end among the allowed ones
            rid, e = start                                 # NEW 18
            strand, count, max_turn, prev_dir, first_dir, closed = [], 0, 0.0, None, None, False   # NEW 18
            junction = None                                # NEW 18
            while True:                                    # NEW 18: follow the line, always straight through
                path = roads[rid][0]                       # NEW 18
                pts = path if e == 0 else path[::-1]       # NEW 18: walk the road from the end we entered
                k = min(15, len(pts) - 1)                  # NEW 18
                d_out = _unit(np.subtract(pts[k], pts[0]))   # NEW 18: direction we leave this road's start in
                if strand:                                 # NEW 18: pass THROUGH the junction centre
                    strand.extend(bridge(strand[-1], G.nodes[junction]["pos"], pts[0]))   # NEW 18
                    max_turn = max(max_turn, _turn(prev_dir, d_out))   # NEW 18: how sharp was the turn?
                else:                                      # NEW 18
                    first_dir = d_out                      # NEW 18
                strand.extend(pts)                         # NEW 18
                used.add(rid)                              # NEW 18
                count += 1                                 # NEW 18
                prev_dir = _unit(np.subtract(pts[-1], pts[-1 - k]))   # NEW 18: direction we arrive in
                junction = ends[(rid, 1 - e)][0]           # NEW 18: junction at the far end of this road
                nxt = partner.get((rid, 1 - e))            # NEW 18: the road end that continues straight
                if nxt is None:                            # NEW 18: nothing to continue with, line ends here
                    break
                if nxt == start:                           # NEW 18: back at the start, the line is closed
                    closed = True                          # NEW 18
                    strand.extend(bridge(strand[-1], G.nodes[junction]["pos"], strand[0]))   # NEW 18
                    max_turn = max(max_turn, _turn(prev_dir, first_dir))   # NEW 18
                    break
                if nxt[0] in used:                         # NEW 18: safety, should not happen
                    break
                rid, e = nxt                               # NEW 18: continue on the partner road
            strands.append(strand)                         # NEW 18
            report.append((count, closed, max_turn, len(piece_roads)))   # NEW 18
    return strands, report                                 # NEW 18


def save_path_data(name, shape, strands, marks):           # NEW 23
    """Save everything the animation needs in one small file: results/path_<name>.json"""
    data = {                                               # NEW 23: a plain dictionary
        "image": name,                                     # NEW 23
        "height": int(shape[0]),                           # NEW 23: picture size
        "width": int(shape[1]),                            # NEW 23
        "crossings": [[int(round(x)), int(round(y))] for x, y in marks],       # NEW 23: crossing centres
        "strands": [[[int(x), int(y)] for x, y in st] for st in strands],      # NEW 23: each strand = list of points
    }
    stem = os.path.splitext(name)[0]                       # NEW 30: "k01"
    dots_file = os.path.join(RES, "dots_" + stem + ".json")   # NEW 30: written by detect_dots.py
    if os.path.exists(dots_file):                          # NEW 30
        with open(dots_file) as f:                         # NEW 30
            data["dots"] = json.load(f)                    # NEW 30: [x, y, radius] per dot
    else:                                                  # NEW 30
        data["dots"] = []                                  # NEW 30
        print("   WARNING: no", dots_file, "- run python src/detect_dots.py first")   # NEW 30
    out = os.path.join(RES, "path_" + stem + ".json")      # NEW 23: path_k01.json
    with open(out, "w") as f:                              # NEW 23
        json.dump(data, f)                                 # NEW 23: write the card
    return out                                             # NEW 23


def draw_strokes(strokes, shape, marks=()):                # NEW 12
    """Picture of the strokes: blue = start, red = end, numbers = point positions."""
    out = np.zeros(shape + (3,), np.uint8)                 # NEW 12: black picture
    for n, st in enumerate(strokes):                       # NEW 12: one stroke at a time
        last = max(1, len(st) - 1)                         # NEW 12
        for i in range(1, len(st)):                        # NEW 12: join each point to the previous one
            shade = np.uint8([[int(255 * i / last)]])      # NEW 12
            color = tuple(int(c) for c in cv2.applyColorMap(shade, cv2.COLORMAP_JET)[0, 0])   # NEW 12
            cv2.line(out, st[i - 1], st[i], color, 2)      # NEW 12
        for i in range(0, len(st), 250):                   # NEW 12: a number every 250 points
            cv2.putText(out, str(i), (st[i][0] + 6, st[i][1] - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)   # NEW 12
        cv2.circle(out, st[0], 9, (0, 255, 0), 2)          # NEW 12: green circle = where the pencil starts
        cv2.putText(out, "start %d" % (n + 1), (st[0][0] + 12, st[0][1] + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)           # NEW 12
    for (mx, my) in marks:                                 # NEW 19: white circle on every crossing
        cv2.circle(out, (int(mx), int(my)), 7, (255, 255, 255), 1)   # NEW 19
    return out                                             # NEW 12


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

        strands, report = build_strands(G, roads)          # NEW 20: straight-through strands
        print("   STRAND TEST: strands", len(strands), "(pieces in the graph:", nx.number_connected_components(G), ")")   # NEW 20
        for i, (st, (n_roads, closed, turn, in_piece)) in enumerate(zip(strands, report)):   # NEW 20
            print("   strand", i + 1, "| points", len(st), "| roads", n_roads, "| closed loop", closed,
                  "| sharpest turn at a crossing", round(turn, 1), "deg", "| starts at", st[0])   # NEW 50: show where it starts
        print("   roads used in all strands", sum(r[0] for r in report), "of", G.number_of_edges())   # NEW 20
        gaps = [float(np.hypot(a[0][0] - b[0][0], a[0][1] - b[0][1])) for i, a in enumerate(strands) for b in strands[i + 1:]]   # NEW 51: distance between every pair of starts
        if gaps:                                           # NEW 51
            print("   START GAP TEST: closest two starts are", round(min(gaps)), "px apart (need more than", APART, ")")   # NEW 51

        marks = [d["pos"] for n, d in G.nodes(data=True) if n.startswith("J")]   # NEW 21: crossing centres
        cv2.imwrite(os.path.join(RES, "path_" + name), draw_strokes(strands, slab.shape, marks))   # NEW 21: save the picture

        saved = save_path_data(name, slab.shape, strands, marks)   # NEW 24: save the data card
        with open(saved) as f:                             # NEW 25: read it back to check
            back = json.load(f)                            # NEW 25
        same = [len(x) for x in back["strands"]] == [len(x) for x in strands]   # NEW 25
        print("   DATA TEST: saved", os.path.basename(saved), "| strands", len(back["strands"]),
              "| points", sum(len(x) for x in back["strands"]), "| crossings", len(back["crossings"]), "| dots", len(back["dots"]),
              "| same as in memory", same)                  # NEW 25