# Kolam AI: failures.md update (updated 15 Nov 2026, 21:18 IST)

HOW TO USE: In `docs/failures.md`, REPLACE rows 13 to 19 with the rows below, then ADD rows 20 to 27. Rows 1 to 12 stay as they are (not changed here).
Only real obstructions are listed: what went wrong, the proof, the fix, the result.

## Run history (25 pictures, 500 px wide, speed 40)

| Run | Change | Dots correct | Pipeline OK | Verdict |
| --- | --- | --- | --- | --- |
| baseline | dot area 150 to 4000 | not recorded | 18 = 72% | below the 80% gate |
| after_fix1 | min area 150 to 100 | 24 = 96% | 23 = 92% (strict 22 = 88%) | k17 to k20 fixed. k10 found 10 of 9 (false pass) |
| after_fix2 | max area 4000 to 300 | 21 = 84% | 19 = 76% | BACKFIRED (a guess) |
| after_fix3 | min 120, max back to 4000 | 24 = 96% | 21 = 84% | k10 dots right, k19 broke |
| after_fix4 | spur prune, 15 px | 24 = 96% | 23 = 92% | k22 and k24 fixed |
| after_fix5 | speck drop, 50 px | 24 = 96% | 24 = 96% | k10 passes Lock 1 |
| after_fix6 | min area 100 + duplicate-dot rule | 25 = 100% | 25 = 100% | k19 fixed, k10 dot count right |
| after_fix8 | glue split crossings (5 px) | 25 = 100% | 25 = 100% | k10 path fixed (by eye) |

(There is no after_fix7 in this table: jobs 1 and 2, speed and dot size, were animation polish and did not change detection.)

## Rows 13 to 27

| # | Picture and stage | What went wrong | Cause (and proof) | Fix | Result |
| --- | --- | --- | --- | --- | --- |
| 13 | k17 to k20, dot detection | "No dots found" | Dots were 138 to 145 px, minimum area was 150. `dot_diag k17` showed every dot rejected only by the area test | Fix 1: min area 150 to 100 | k17 to k20 found 12 of 12. Side effect: k10 (row 14) |
| 14 | k10, dot detection | Found 10 dots instead of 9, and the script still said OK | Fix 1 let in a 108 px shape (id 9). `dot_centres k10`: id 9 sits 0 to 1 px from the big centre dot id 6 (649 px), so it is the same dot counted twice | Fix 6: duplicate rule, a small shape whose centre is inside a bigger dot is ignored | 9 of 9 dots, and the extra shape no longer leaves a stray mark |
| 15 | k22, graph (Lock 1) | "Loose line end", stopped | 4 tiny tails at the sharp tips. `spur_diag k22`: walks of 4, 4, 5 and 3 px, each reaching a junction | Fix 4: `prune_spurs`, cut dead-end tails of 15 px or less | Passes. 4 tails cut (log) |
| 16 | k24, graph (Lock 1) | "Loose line end", stopped | 2 tiny tails (top tip, corner hook). `spur_diag k24`: walks of 6 and 2 px | Fix 4: `prune_spurs` | Passes. 2 tails cut (log) |
| 17 | all 25, dot detection | Fix 2 made things worse (pipeline 23 to 19, 3x3 dots 14 to 11) | I guessed that the 649 px shape was a blob and set max area 300. It is the real centre dot, so centre dots were thrown out. `dot_diag` was not run on the other pictures first | Reverted in fix 3. Kept in `docs/proof/` as an honest failed attempt | Lesson: measure on ALL affected pictures before changing a number |
| 18 | k10, dot detection | False pass in fix 1 | See row 14 (10 dots, script counted OK) | Strict count 22 of 25 = 88% instead of 23 | Fixed by row 14 |
| 19 | k19, dot detection (after fix 3) | 0 of 12 dots, "no dots" | Min 120 was above the dots. `dot_diag k19`: 12 shapes of 106 to 112 px, 12x12, roundness 0.94 to 0.99, each rejected only by the area test | Fix 6: min area 100 | 12 of 12. Same size as the k10 false dot (108 px), so size alone cannot tell them apart. Position can (row 14) |
| 20 | k10, skeleton (Lock 1) | "Loose line end", stopped | A stray 2 px skeleton piece floating in the centre. `piece_diag k10`: one piece of 3256 px and one of 2 px. Smallest real piece anywhere is 813 px (k06). The prune cut 0 because the piece is not a tail on a line | Fix 5: `drop_specks`, erase separate skeleton pieces under 50 px | Passes. Only k10 dropped a speck (log line 94) |
| 21 | k10, drawing path | Passes both locks, but the path looked wrong at 2 crossings (under dot 2 of row 1, and the mirror under the centre dot) | Each crossing was split into two junctions 14 px apart, joined by a road of 1 px (`junction_diag k10`: J2 and J3, J8 and J9; the 247 px road between them is the top or bottom loop). In `trace_path.py` a 1 px road gives `k = 0`, so its direction is (0, 0) and `pair_ends` pairs the wrong road ends. `MERGE = 9` does not glue pairs that far apart | Fix 8: `glue_close_junctions`, join two junctions linked by a road of 5 px or less into one junction (degree 6) | Teju watched the k10 animation: good. Log: `junctions merged: 2`, all other 24 pictures 0 |
| 22 | whole pipeline | Locks cannot see a bad path | Lock 1 checks odd degrees and Lock 2 checks closed loops. k10 passed both while the path was wrong | Finger test by eye on the animation | Rule: `closed True` is not the same as right to the eye |
| 23 | Animation | Too fast for a teacher to follow | Default speed was 15 points per frame at 25 fps | Default speed 5, app slider 2 to 20 | Confirmed by Teju (15 Nov): calm. Laptop time to build the GIF for k04 (6835 points): 20.9 s. Cloud: k05 and k10 under 20 s. k04 not timed on the cloud |
| 24 | Animation | Dots had different sizes | Each dot circle used its own measured radius (k10 centre dot 40 px, others 16 px, k19 dots 12 px) | `DOT_R = 9` for every dot (every picture is 500 px wide) | Confirmed by Teju (15 Nov): all dots the same size |
| 25 | Log reading | I read k11's detail block as k10's | `run_all` prints a picture's detail lines BEFORE its `kNN.png OK` line | Read the block that comes before the label | Lesson: check which line a block belongs to |
| 26 | `dot_diag.py` | Prints "Limits: area 150..4000" (old) | The limits are hard-coded in `dot_diag.py` and were not updated | Not fixed yet (low priority). The detector itself is `detect_dots.py`, MIN_DOT = 100 | OPEN |
| 27 | Whole project | The 25 pictures are both test set and tuning set | Dot area, spur 15, speck 50 and glue 5 were chosen on the same 25 pictures | Each choice came from a measurement. The honest statement goes in the report | 100% is not a fair estimate for new pictures |
