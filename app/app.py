import os                                                    # NEW 1
import sys                                                   # NEW 1
import cv2                                                   # NEW 2
import numpy as np                                           # NEW 2
import streamlit as st                                       # NEW 3

APP = os.path.dirname(os.path.abspath(__file__))             # NEW 4: the app folder
ROOT = os.path.dirname(APP)                                  # NEW 4: the project folder
sys.path.insert(0, os.path.join(ROOT, "src"))                # NEW 5: so we can import from src

from pipeline import run_pipeline                            # NEW 6
from build_graph import RES                                  # NEW 6

os.makedirs(RES, exist_ok=True)                              # NEW 7: results folder must exist
UP = os.path.join(ROOT, "uploads")                           # NEW 7
os.makedirs(UP, exist_ok=True)                               # NEW 7: separate folder, so our input is never overwritten

st.title("Kolam AI")                                         # NEW 8
st.write("Upload a clean, top-down dot kolam. I will show you how to draw it.")   # NEW 8

file = st.file_uploader("Pick a picture", type=["png", "jpg", "jpeg"])   # NEW 9
speed = st.slider("Speed (higher = faster)", 5, 40, 15)      # NEW 10

if file is not None:                                         # NEW 11
    data = np.frombuffer(file.read(), np.uint8)              # NEW 12
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)               # NEW 12
    if img is None:                                          # NEW 13
        st.error("This file is not a picture I can open.")   # NEW 13
        st.stop()                                            # NEW 13
    h, w = img.shape[:2]                                     # NEW 14
    img = cv2.resize(img, (500, int(h * 500 / w)))           # NEW 14: always 500 wide
    path = os.path.join(UP, "upload.png")                    # NEW 15
    cv2.imwrite(path, img)                                   # NEW 15
    st.image(path, caption="Your picture")                   # NEW 16

    if st.button("Show me how to draw it"):                  # NEW 17
        try:                                                 # NEW 18
            with st.spinner("Working... please wait"):       # NEW 18
                out = run_pipeline(path, speed=speed)        # NEW 18
        except ValueError as e:                              # NEW 19: our friendly sentences
            st.error(str(e))                                 # NEW 19
            st.stop()                                        # NEW 19
        except Exception:                                    # NEW 20: anything unexpected
            st.error("Sorry, something went wrong with this picture. Try a clearer one.")   # NEW 20
            st.stop()                                        # NEW 20
        st.success(f"Dots: {out['n_dots']} | Strands: {out['n_strands']}")   # NEW 21
        st.subheader("1. Dots found")                        # NEW 22
        st.image(out["dots_img"])                            # NEW 22
        st.subheader("2. Skeleton")                          # NEW 23
        st.image(out["skel_img"])                            # NEW 23
        st.subheader("3. Drawing animation")                 # NEW 24
        st.image(out["gif"])                                 # NEW 24