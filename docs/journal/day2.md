# Day 2 Journal | Sat 7 Nov 2026

Project: Kolam AI | Course: Societal Based Mini Project (24AIM57) | Student: Tejasree E

## 1. Goal of today

- Deploy a small hello-world Streamlit app, so deploy problems show up today and not on Monday
- Make the skeleton: only the kolam lines, 1 pixel thin
- Build the graph from the skeleton (junctions, endpoints, edges)

## 2. What I built

- **Hello-world deploy:** `app/app.py` + `requirements.txt`, deployed on Streamlit Community Cloud. Public link opens on laptop and phone
- **Skeleton (3 pieces):** remove the dots, remove specks and the border, then skeletonize
- **`build_graph.py`:** finds endpoints and junctions, merges close junction pixels, cuts out the roads, builds a NetworkX graph, saves a picture with green rings (junctions) and blue rings (endpoints)

Results (4 images):

| Image | Junctions | Endpoints | Edges | Pieces |
| --- | --- | --- | --- | --- |
| k01 | 8 | 0 | 16 | 1 |
| k02 | 16 | 0 | 32 | 1 |
| k03 | 8 | 0 | 16 | 2 |
| k04 | 10 | 0 | 20 | 1 |

## 3. How it works in plain words

- Dot detection already told us where the dots are. Now for the skeleton, first thing is to erase all the dots, because now we only care about the lines
- Then I erase the small specks also, like pencil dust, the border and any other disturbance. Everything except the kolam lines should become black, only the lines stay white
- Last step of skeleton: the line is thick, so I make it thin, only the centre part of the line stays and its just 1 pixel wide
- Why 1 pixel? Because in the next step (graph) the computer has to check the neighbours of every pixel. Is it a dead end (only 1 neighbour)? Is it a crossroad (3 or more neighbours)? This is very easy to count when the line is only 1 pixel wide, with a thick line you cannot count properly
- Junction = the place where lines meet or cross each other. Dead end = endpoint. Both of them are the nodes of the graph
- Edge = the line between two nodes. It joins two crossroads (or a crossroad and a dead end)
- All this is saved as a NetworkX graph, and the next step (drawing path) will use this graph

## 4. What broke and how I fixed it

- **Too many junctions at first:** k01 showed 12 junctions but I can count only 8 by eye, and k04 showed 20 instead of 10. One crossing was giving many junction pixels close together. Fixed by the merge step in `build_graph.py` (`MERGE = 9`), which joins close junction pixels into one junction. After that the counts matched the pictures
- **k03 has 2 pieces:** not a bug. The X shape in k03 is really separate from the rest, so the graph has 2 pieces
- **k04 lost one speck:** the clean step dropped one tiny piece, which is what it should do
- **Checked on 4 images, not 5:** the plan says 5, but I have only 4 images right now
- **Deploy:** nothing broke, the hello-world deploy worked in the first try

## 5. What I would tell a beginner

- Do the deploy early. A tiny hello-world app catches problems when you still have time
- The skeleton step looks boring, but the graph step cannot work without it, so look at the skeleton picture and check the lines are thin and not broken
- Dont trust the printed numbers only. Count the rings on the picture by eye and compare with the printout
- Build one small piece, run it, then commit

## Checkpoints

- Skeleton 1 pixel thin and unbroken: yes, by eye on 4 images (plan asks 5)
- Graph matches the drawing by eye: yes, 4 of 4. All junctions have degree 4 and edges = 2 x junctions
- Public hello-world link opens: yes, on laptop and phone
- Path (finger test): not started, that is Day 3's first block
