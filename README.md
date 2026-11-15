<div align="center">

<img src="docs/images/banner.svg" alt="Kolam AI" width="100%">

<br>

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-classical%20CV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-graph-2E7D32?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-live%20app-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/status-prototype%20v1-2E7D32?style=flat-square)

**[Live app](https://kolam-ai.streamlit.app)** &nbsp;•&nbsp; **[How it works](#-how-it-works)** &nbsp;•&nbsp; **[Results](#-results)** &nbsp;•&nbsp; **[Run it](#-run-it-locally)** &nbsp;•&nbsp; **[Roadmap](#-roadmap)**

</div>

<br>

## 🪔 The idea

A **kolam** is a South Indian line drawing made around a grid of dots. The line never touches the dots. It loops around them and crosses itself, and it is drawn in one smooth movement.

Learning a kolam from a finished picture is hard. You can see *what* it looks like, but not *how the hand moves*.

**Kolam AI** takes a picture of a clean dot kolam, works out how a hand would draw it, and replays the drawing step by step: dots first, then the line, slowly enough to copy.

<div align="center">

<img src="docs/images/k24/anim_k24.gif" width="380"><br>
<sub>The app's animation for <b>k24</b> (13 dots, grid 1-3-5-3-1). Dots appear first, then the line is drawn.</sub>

</div>

<br>

## 🔍 How it works

No deep learning and nothing is trained. Every stage is classical computer vision, so each step can be seen and explained. All pictures below are **k24**.

```mermaid
flowchart LR
    A[Image] --> B[Dots]
    B --> C[Skeleton]
    C --> D[Graph]
    D --> E[Path]
    E --> F[Animation]
    style A fill:#3b0d1a,color:#fff
    style B fill:#7a1f33,color:#fff
    style C fill:#a8452f,color:#fff
    style D fill:#d98a3d,color:#fff
    style E fill:#2E7D32,color:#fff
    style F fill:#2E7D32,color:#fff
```

<br>

<table>
  <tr>
    <td align="center"><img src="docs/images/k24/k24.png" width="200"></td>
    <td align="center"><img src="docs/images/k24/skel_k24.png" width="200"></td>
    <td align="center"><img src="docs/images/k24/graph_k24.png" width="200"></td>
    <td align="center"><img src="docs/images/k24/path_k24.png" width="200"></td>
  </tr>
  <tr>
    <td align="center"><b>1. Find the dots</b><br><sub>Blur, Otsu threshold, keep only round shapes of the right size. Red rings mark the dots</sub></td>
    <td align="center"><b>2. Thin the lines</b><br><sub>Erase dots, specks and the frame, then shrink every line to 1 pixel</sub></td>
    <td align="center"><b>3. Build the graph</b><br><sub>Green rings are crossings, blue rings are line ends. Lines between them are edges</sub></td>
    <td align="center"><b>4. Trace the path</b><br><sub>Numbers show the drawing order. Green ring = start, white ring = crossing</sub></td>
  </tr>
</table>

<br>

| Stage | What it does | Tools |
| --- | --- | --- |
| **Dots** | Finds every dot. A shape counts only if its area (100 to 4000 px), box shape (width/height 0.6 to 1.5) and roundness (above 0.5) fit. A small shape whose centre sits inside a bigger dot is ignored | `GaussianBlur`, Otsu threshold, `connectedComponentsWithStats` |
| **Skeleton** | Erases the dots, removes specks and the picture frame, thins the line to 1 pixel | `skimage.morphology.skeletonize` |
| **Graph** | Cuts tiny tails (15 px or less) and tiny loose pieces (under 50 px). Counts each pixel's neighbours to find crossings (3 or more) and dead ends (1). Glues crossroad pixels that touch into one junction. Two junctions linked by a road of 5 px or less become one. Roads between them become edges | `filter2D`, `dilate`, NetworkX `MultiGraph` |
| **Path** | At every crossing, pairs the two road ends that point most opposite, so the line goes straight through like a hand. Follows the pairs until the line closes. Saves the points as JSON | dot product of directions |
| **Animation** | Draws the dots, then the line, step by step. Every dot has the same size. Default speed is 5, slider 2 to 20. Saved as a GIF | Matplotlib `FuncAnimation`, Pillow |

**Two safety locks** stop a bad picture before it draws a wrong animation:

| Lock | Stops when |
| --- | --- |
| Lock 1 | a crossing has an odd number of roads (a loose line end) |
| Lock 2 | a drawn strand does not close |

The app then shows a friendly message instead of a broken drawing.

<details>
<summary><b>Why the graph makes one-stroke drawing possible</b></summary>

<br>

Where every crossing has an even number of lines, a connected piece can be traced in one continuous stroke that ends where it started. This is an Eulerian circuit. A plain Eulerian walk can turn sharply at a crossing, which a hand would not do (this failed on our first attempt). So the path stage pairs the most opposite road ends at each crossing and goes straight through.

</details>

<br>

## 📊 Results

Evaluated on a **test set of 25 clean, top-down dot kolams** (k01 to k25). **Nothing is trained.** The correct dot count of every picture was written by hand **before** running the program (`data/labels.csv`). All 25 were marked `clean` by eye.

k05 to k25 were hand-drawn on paper and digitized with ChatGPT.

Every run: 25 pictures, resized to 500 px wide, speed 40.

| Run | Change | Dots correct | Whole pipeline OK |
| --- | --- | :---: | :---: |
| baseline | dot area 150 to 4000 | not recorded | 18 / 25 (72%) |
| after fix 1 | min dot area 150 to 100 | 24 / 25 | 23 / 25 (strict count 22) |
| after fix 2 | max dot area 4000 to 300 *(a guess, it backfired)* | 21 / 25 | 19 / 25 |
| after fix 3 | min 120, max back to 4000 | 24 / 25 | 21 / 25 |
| after fix 4 | cut tiny tails (15 px) | 24 / 25 | 23 / 25 |
| after fix 5 | drop tiny skeleton pieces (50 px) | 24 / 25 | 24 / 25 |
| after fix 6 | min 100 + duplicate-dot rule | 25 / 25 | 25 / 25 |
| **after fix 8** | glue split crossings (5 px) | **25 / 25** | **25 / 25** |

Groups after fix 8:

| Group | Pictures | Dots and pipeline OK |
| --- | :---: | :---: |
| 3x3 dots (9) | 15 | 15 / 15 |
| 2-4-4-2 dots (12) | 5 | 5 / 5 |
| 1-3-5-3-1 dots (13) | 5 | 5 / 5 |

Every fix came from measuring first (small diagnostic scripts), then changing one thing, then re-running all 25. The proof for each fix is in [`docs/failures.md`](docs/failures.md).

**Checked by eye (finger test, following the animation like a pencil):** k01 to k04, k05, k10, k16, k19, k21, k22 and k24. All pass. The other 14 pictures are not yet checked by eye.

**App tests**

| Test | Result |
| --- | --- |
| Public link on 2 phones | worked on both |
| k05 and k10 on the public link | both under 20 seconds |
| Longest picture k04 (6835 points) on the laptop | 20.9 seconds (not timed on the cloud) |
| Bad input (14 Nov): blurry picture, huge picture (4000 px), text file renamed `.png`, blank picture | no crash. Blurry stopped by Lock 1 with a friendly message. These tests were run before fixes 4 to 8 and not repeated since |

<br>

## ⚙️ Run it locally

```bash
git clone https://github.com/tejasree0906-git/KolamAI.git
cd KolamAI

python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

streamlit run app/app.py                    # the app
python src/pipeline.py data/real/k03.png    # one picture, no app
python run_all.py my_run                    # all 25 pictures, saves a csv and a log
```

Run all commands from the project root. Input pictures go in `data/real/`, outputs are saved in `results/`. `requirements.txt` uses `opencv-python-headless`, which the cloud server needs.

<details>
<summary><b>Project layout</b></summary>

```
KolamAI/
├── src/
│   ├── fake_generator.py  fake dot pictures with a known answer
│   ├── detect_dots.py     dots, curve cleanup, skeleton
│   ├── build_graph.py     tail cut, speck drop, graph
│   ├── trace_path.py      straight-through strands
│   ├── animate_path.py    path to GIF
│   └── pipeline.py        all stages + the two locks
├── app/app.py             Streamlit app
├── run_all.py             run all 25 pictures
├── *_diag.py              small measuring scripts
├── data/                  real/ pictures, labels.csv
├── results/               pictures, GIFs, run csv files
├── docs/                  journals, failure log, images
└── requirements.txt
```

</details>

<br>

## ⚠️ Honest limitations

- Works on **clean, top-down dot kolams** only. Street photos with shadows, tilt or faded powder are not supported.
- The sizes (min dot 100 px, tail 15 px, speck 50 px, glue 5 px) were chosen on the **same 25 pictures** used to test. So 100% is **not** a fair estimate for new pictures.
- A real tail shorter than 15 px would be cut. A real dot smaller than 100 px would be missed.
- The locks check the result, not the blur itself. A blurry picture that still gives clean even crossings would pass.
- 100% means every strand closes. It does not prove the path looks right: k10 passed both locks and was still wrong until the eye caught it. Only 11 of 25 pictures were checked by eye.
- The 21 newest pictures are hand-drawn and redrawn by ChatGPT, not photos.
- Every upload is saved under one file name, so two people at the same time could overwrite each other. Fine for a demo.

<br>

## 🗺️ Roadmap

| | Step |
| :---: | --- |
| ✅ | Dot detection, skeleton, graph |
| ✅ | Straight-through drawing path |
| ✅ | Step-by-step animation, equal dots, speed slider (2 to 20) |
| ✅ | Streamlit app deployed on Streamlit Community Cloud, tested on 2 phones |
| ✅ | Two safety locks and bad-input tests |
| ✅ | 25-picture test set with hand-written labels, 7 failures found and fixed with proof |
| 🔜 | Test on fresh pictures the settings were not tuned on |
| 🔜 | Check the remaining 14 pictures by eye, and an automatic check that the path looks right |
| 🔜 | Lock 3: blur score at the start |
| 🔜 | Tail and speck sizes relative to image size |
| 🔜 | Photos taken in the street (shadows, tilt) |
| 🔜 | Symmetry analysis and motif extraction |

<br>

<div align="center">

**Tejasree E** &nbsp;•&nbsp; B.E. AI & ML, New Horizon College of Engineering, Bangalore
<br>
<sub>Societal Based Mini Project (24AIM57)</sub>

</div>
