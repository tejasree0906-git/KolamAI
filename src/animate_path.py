import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")                                       # NEW 31: draw without a window, we save a GIF
import matplotlib.pyplot as plt                             # NEW 31
from matplotlib.animation import FuncAnimation, PillowWriter   # NEW 32: FuncAnimation = "call update once per frame"
from matplotlib.patches import Circle                       # NEW 33: round shapes for dots and start marker

RES = "results"                                             # NEW 34: same folder as the other scripts


def load_path_data(name):                                   # NEW 35
    """Read the data card made by trace_path.py (for example results/path_k01.json)."""
    with open(os.path.join(RES, "path_" + name + ".json")) as f:   # NEW 35
        return json.load(f)                                 # NEW 35


def pick_label_spot(sx, sy, tw, th, all_pts, dots, w, h, enough=12):   # NEW 52
    """Try 24 directions around a start ring, close first, then farther away.
    Keep a spot where the label box is at least `enough` px from every line and dot. If none, use the best one found."""
    best = None                                             # NEW 52
    for reach in (34, 48, 64):                              # NEW 52: close to the ring first, then a bit farther
        for k in range(24):                                 # NEW 52: 315 (up-right) first, then every 15 degrees round
            deg = (315 + 15 * k) % 360                      # NEW 52
            c, s_ = np.cos(np.radians(deg)), np.sin(np.radians(deg))   # NEW 52
            ax_, ay_ = sx + reach * c, sy + reach * s_      # NEW 52: where the label touches the ring side
            ha = "right" if c < -0.3 else ("left" if c > 0.3 else "center")   # NEW 52
            va = "bottom" if s_ < -0.3 else ("top" if s_ > 0.3 else "center")  # NEW 52: y goes DOWN, so "bottom" = text above the point
            x0 = ax_ - tw if ha == "right" else (ax_ if ha == "left" else ax_ - tw / 2)   # NEW 52: the label box
            x1 = x0 + tw                                    # NEW 52
            y0 = ay_ - th if va == "bottom" else (ay_ if va == "top" else ay_ - th / 2)   # NEW 52
            y1 = y0 + th                                    # NEW 52
            if x0 < 0 or y0 < 0 or x1 > w or y1 > h:        # NEW 52: box would leave the picture
                continue                                    # NEW 52
            dx = np.maximum(np.maximum(x0 - all_pts[:, 0], 0), all_pts[:, 0] - x1)   # NEW 53: distance from every line point to the box
            dy = np.maximum(np.maximum(y0 - all_pts[:, 1], 0), all_pts[:, 1] - y1)   # NEW 53
            gap = float(np.hypot(dx, dy).min())             # NEW 53: closest line point
            for (x, y, r) in dots:                          # NEW 53: dots count too (real size is r - 8)
                ddx = max(x0 - x, 0, x - x1)                # NEW 53
                ddy = max(y0 - y, 0, y - y1)                # NEW 53
                gap = min(gap, float(np.hypot(ddx, ddy)) - (r - 8))   # NEW 53
            if best is None or gap > best[0]:               # NEW 54: strictly better wins, so ties keep the earlier choice
                best = (gap, ax_, ay_, ha, va)              # NEW 54
        if best is not None and best[0] >= enough:          # NEW 54: good enough at this distance, stop here
            return best                                     # NEW 54
    if best is None:                                        # NEW 54: nothing fitted at all, use up-right
        return (0.0, sx + 24, sy - 24, "left", "bottom")    # NEW 54
    return best                                             # NEW 54


def make_animation(data, speed=20, hold=15, verbose=False):   # NEW 36, NEW 55: verbose=True prints the label gaps
    """speed = points drawn per frame (bigger = faster). hold = frames to pause at the start and the end."""
    w, h = data["width"], data["height"]                    # NEW 36: picture size
    strands = [np.array(s) for s in data["strands"]]        # NEW 36: each strand = array of (x, y) points

    fig, ax = plt.subplots(figsize=(6, 6 * h / w), dpi=70)  # NEW 37: empty drawing sheet
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)   # NEW 37: no empty border
    ax.set_xlim(0, w)                                       # NEW 37
    ax.set_ylim(h, 0)                                       # NEW 37: y goes DOWN in a picture, so flip it
    ax.set_aspect("equal")                                  # NEW 37: circles stay round
    ax.axis("off")                                          # NEW 37: no axes, like a clean paper
    all_pts = np.vstack(strands)                            # NEW 56: every line point, so labels can keep away from them
    unit = w / (fig.get_figwidth() * fig.dpi)               # NEW 56: picture pixels per screen pixel
    label_size = 14                                         # NEW 56: font size of the labels

    for x, y, r in data["dots"]:                            # NEW 38: dots are ALWAYS there, from frame 1
        ax.add_patch(Circle((x, y), r - 8, color="black"))  # NEW 38: r - 8 = the real dot size (r had +8 for the red ring)

    lines = [ax.plot([], [], color="royalblue", lw=2.5, solid_capstyle="round")[0] for _ in strands]   # NEW 39: one empty line per strand
    starts = []                                             # NEW 40
    for i, st in enumerate(strands):                        # NEW 40: one green start marker per strand, hidden for now
        ring = Circle((st[0][0], st[0][1]), 10, fill=False, ec="green", lw=2.5, visible=False)   # NEW 40
        ax.add_patch(ring)                                  # NEW 40
        text = str(i + 1) if len(strands) > 1 else "start"   # NEW 57: the label text
        tw = 0.65 * label_size * fig.dpi / 72 * len(text) * unit   # NEW 57: label width in picture pixels (a guess, a bit generous)
        th = 1.3 * label_size * fig.dpi / 72 * unit         # NEW 57: label height in picture pixels
        gap, lx, ly, ha, va = pick_label_spot(st[0][0], st[0][1], tw, th, all_pts, data["dots"], w, h)   # NEW 58: best free spot
        if verbose:                                         # NEW 58
            print("   label", text, "| closest line or dot is", round(gap), "px away")   # NEW 58
        label = ax.text(lx, ly, text, color="green", fontsize=label_size, weight="bold", visible=False, ha=ha, va=va)   # NEW 59
        starts.append((ring, label))                        # NEW 40

    total = sum(len(s) for s in strands)                    # NEW 41: all points of all strands
    n_frames = hold + int(np.ceil(total / speed)) + 1 + hold   # NEW 41: pause, draw, pause

    def update(frame):                                      # NEW 42: called once for every frame
        left = max(0, min((frame - hold) * speed, total))   # NEW 42: points drawn so far (0 during the first pause)
        for i, st in enumerate(strands):                    # NEW 42: fill strand 1 first, then strand 2 ...
            k = int(min(left, len(st)))                     # NEW 42: how many points of THIS strand are drawn
            left -= k                                       # NEW 42
            lines[i].set_data(st[:k, 0], st[:k, 1])         # NEW 42: draw the first k points
            show = (i == 0) or (k > 0)                      # NEW 42: strand 1 marker from the start, others when their line begins
            starts[i][0].set_visible(show)                  # NEW 42
            starts[i][1].set_visible(show)                  # NEW 42
        return lines                                        # NEW 42

    anim = FuncAnimation(fig, update, frames=n_frames, blit=False)   # NEW 43
    return fig, anim, n_frames                              # NEW 43


if __name__ == "__main__":                                  # NEW 44: python src/animate_path.py k01   (or no name = all four)
    names = sys.argv[1:] or ["k01", "k02", "k03", "k04"]    # NEW 44
    for name in names:                                      # NEW 44
        data = load_path_data(name)                         # NEW 44
        fig, anim, n_frames = make_animation(data, speed=15, verbose=True)   # NEW 44, NEW 55
        out = os.path.join(RES, "anim_" + name + ".gif")    # NEW 44
        anim.save(out, writer=PillowWriter(fps=25))         # NEW 44: write the GIF
        plt.close(fig)                                      # NEW 44
        print(name, "| strands", len(data["strands"]), "| dots", len(data["dots"]),
              "| frames", n_frames, "| about", round(n_frames / 25), "seconds | saved", out)   # NEW 44