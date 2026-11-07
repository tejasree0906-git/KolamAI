import numpy as np
import cv2

def make_dot_grid(n, spacing=100, margin=100, radius=10):
    size = margin * 2 + spacing * (n - 1)
    img = np.full((size, size, 3), 255, dtype=np.uint8)   # white canvas
    for row in range(n):
        for col in range(n):
            x = margin + col * spacing
            y = margin + row * spacing
            cv2.circle(img, (x, y), radius, (0, 0, 0), -1)  # filled black dot
    return img

if __name__ == "__main__":
    img = make_dot_grid(7)
    cv2.imwrite("data/fake_5x5.png", img)
    print("saved. True dot count =", 7* 7)