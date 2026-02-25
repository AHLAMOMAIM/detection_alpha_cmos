import numpy as np
import rawpy
from skimage.measure import label, regionprops
import subprocess
import struct
import os
import time
from collections import defaultdict



DURATION_S = 10800          
EXPOSURE_US = 800000      
WIDTH = 4056
HEIGHT = 3040

THRESH_K = 35             # seuil physique
MIN_AREA = 2              # cluster minimum

DATA_DIR = "data_raw"
os.makedirs(DATA_DIR, exist_ok=True)

EVENTS_RAW = "events_nuit.raw"

# CAPTURE


def capture_image(path):
    cmd = [
        "rpicam-still",
        "--width", str(WIDTH),
        "--height", str(HEIGHT),
        "--shutter", str(EXPOSURE_US),
        "--gain", "1",
        "--awbgains", "1,1",
        "--denoise", "off",
        "--immediate",
        "--nopreview",
        "--raw",
        "-o", path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)



def main():

    total_events = 0
    frame_id = 0

    
    pixel_counter = defaultdict(int)

    
    with open(EVENTS_RAW, "wb") as f:
        pass

    t0 = time.time()
    t_end = t0 + DURATION_S

    print("=== TEST 15 MIN DÉTECTION FILTRÉE ===")

    while time.time() < t_end:

        frame_id += 1
        filename = f"img_{frame_id:06d}.dng"
        filepath = os.path.join(DATA_DIR, filename)

        capture_image(filepath)

        with rawpy.imread(filepath) as raw:
            raw_img = raw.raw_image.astype(np.float32)

        mu = float(raw_img.mean())
        sigma = float(raw_img.std())
        if sigma < 1e-6:
            sigma = 1e-6

        threshold = mu + THRESH_K * sigma
        mask = raw_img > threshold

        lab = label(mask, connectivity=2)
        regions = regionprops(lab, intensity_image=raw_img)

        events = []

        for r in regions:

            if r.area < MIN_AREA:
                continue

            max_int = float(r.max_intensity)
            cy, cx = r.centroid
            x = int(cx)
            y = int(cy)

            k = (max_int - mu) / sigma

            # filtre pixel chaud (répétition spatiale)
            pixel_counter[(x, y)] += 1
            if pixel_counter[(x, y)] > 3:
                continue

            events.append((x, y, k, mu, sigma))

        if events:
            with open(EVENTS_RAW, "ab") as f:
                for (x, y, k, mu, sigma) in events:
                    f.write(struct.pack("iifff", x, y, k, mu, sigma))
                    total_events += 1
                    print(f"[EVENT] x={x} y={y} k={k:.2f} mu={mu:.2f} sigma={sigma:.2f}")

        else:
            os.remove(filepath)

    duration_s = time.time() - t0
    duration_h = duration_s / 3600.0
    rate = total_events / duration_h if duration_h > 0 else 0.0

    print("\n=== RÉSULTAT FINAL ===")
    print(f"Total events : {total_events}")
    print(f"Rate : {rate:.1f} events/h")
    print("======================")

if __name__ == "__main__":
    main()
