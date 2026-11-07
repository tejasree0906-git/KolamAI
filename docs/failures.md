# Failure Log

Kolam AI | One row per failure: image, stage, what went wrong, what fixed it.
Add a row only when something really breaks. This is the answer bank for questions C5 and H2.

| # | Image | Stage | What went wrong | What fixed it |
| --- | --- | --- | --- | --- |
| 1 | Hand-drawn paper photo | Skeleton | Hand-drawn lines were uneven and thin, so the pixel-by-pixel steps failed | Made the test images digitally, so lines are clean and even. Hand-drawn photos stay a limitation |
| 2 | k01, k04 | Graph | Junction count too high (k01 showed 12, real 8; k04 showed 20, real 10), because one crossing leaves many junction pixels close together | Merged close junction pixels into one junction (MERGE = 9). Counts then matched the pictures |
