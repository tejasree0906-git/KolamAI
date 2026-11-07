# Day 1 Journal | Fri 6 Nov 2026

Project: Kolam AI | Course: Societal Based Mini Project (24AIM57) | Student: Tejasree E

## 1. Goal of today

- Set up the project and get a small dataset
- Make a fake generator so I have test pictures with a known answer
- Detect the dots in kolam images and circle them in red

## 2. What I built

- **Setup:** project folder, virtual environment and the libraries from the plan
- **Dataset:** 4 clean digital kolam images (k01 to k04), not the planned 25
- **`fake_generator.py`:** draws a 5x5 dot grid and saves `fake_5x5.png` (true count = 25)
- **`detect_dots.py`:** grey, blur, threshold, find shapes, keep only dot-shaped ones, draw red circles
- **OpenCV notes:** a cheat sheet of every function I used, stage by stage

## 3. How it works in plain words

- First the computer makes the picture grey and blurs it little bit, so the tiny specks goes away
- Then every pixel becomes black or white, Otsu decides the cut-off by itself, I dont have to pick
- I flip the colours so the dots becomes white, because OpenCV can find only white shapes
- Every white shape gets a number, and the computer notes its size and centre
- Each shape has to pass 3 questions: is the size right, is it square-ish, is it round. If any one is "no", it is rejected
- The long kolam curve is too big, so it fails the size test and only the dots are left
- At last a red circle is drawn on every dot and the dots are counted

## 4. What broke and how I fixed it

- **Why flip the colours?** I was confused. Fixed by learning that OpenCV counts white shapes only, and the flip happens on a working copy, so the original stays untouched
- **Only 4 images, not 25:** I was not sure I could trace a big set yet, so I started with 4 clean ones and will add more later
- **Hand-drawn paper photo:** the dots were found, but the lines are thin and uneven, so I will treat paper photos as a limitation
- **Piece 3 (is it a dot?):** I did not understand the code at first. Fixed by learning that every shape has measurements (size, width to height, roundness). If a value is outside its range, the shape is not a dot and the code prints why. If all are inside, its centre point goes into the `dots` list, which piece 4 uses to draw the red circles

## 5. What I would tell a beginner

- Test on a picture where you already know the answer, like a fake 5x5 grid
- Type the code yourself, change one value, and see what changes
- Look at the result with your own eyes, not just the printed number
- Start with a small set of clean images, then add harder ones
- I learned the whole mechanism of dot detection: first find all the shapes, then check each one against ranges to decide dot or not. Printing why a shape was rejected shows me what to fix

## Checkpoints

- Dots found on all 4 digital images: yes
- Fake image correct: yes, 25 dots found on `fake_5x5.png`
- Gate (dot detection on real images): passed. 4 of 4 images, 9 of 9 dots each, so Plan A (OpenCV detection) stays and Plan B (fixed grid) is not needed
- "10 random images match their labels": not done. I changed the plan and decided to test the whole pipeline on only 4 images first. The labeling CSV and more images will come after all stages work
