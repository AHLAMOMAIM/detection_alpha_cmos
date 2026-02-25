import numpy as np
import subprocess
import os
import time

# Paramètres capteur
WIDTH = 4056
HEIGHT = 3040
BIT_DEPTH = 12
MAX_VALUE = 4095

# Paramètre seuil
K_THRESHOLD = 40

# Dossier sauvegarde
SAVE_DIR = "events_raw"
os.makedirs(SAVE_DIR, exist_ok=True)

image_index = 0

while True:

    filename = "frame.raw"

    # 1️⃣ Acquisition image RAW
    cmd = [
        "rpicam-still",
        "--raw",
        "--width", str(WIDTH),
        "--height", str(HEIGHT),
        "--shutter", "800000",
        "--gain", "1",
        "--awbgains", "1,1",
        "--denoise", "off",
        "--nopreview",
        -t 3600000
        "-o", filename
    ]

    subprocess.run(cmd)

    # Lecture fichier RAW (12 bits stocké en 16 bits)
    raw_data = np.fromfile(filename, dtype=np.uint16)
    image = raw_data.reshape((HEIGHT, WIDTH))

    # Calcul moyenne
    mean_intensity = np.mean(image)
    std_intensity = np.std(image)

    # Condition événement
    threshold = mean_intensity + K_THRESHOLD * std_intensity

    if np.max(image) > threshold:

        event_name = os.path.join(SAVE_DIR, f"event_{image_index:04d}.raw")
        image.tofile(event_name)

        print(f"Evénement détecté → sauvegardé : {event_name}")
        image_index += 1

    else:
        print("Pas d'événement détecté")

    time.sleep(1)