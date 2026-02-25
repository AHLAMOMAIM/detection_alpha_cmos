import struct
import numpy as np
import matplotlib.pyplot as plt

RAW_FILE = "events.raw"  

events = []

with open(RAW_FILE, "rb") as f:
    while True:
        data = f.read(20)
        if not data:
            break
        x, y, k, mu, sigma = struct.unpack("iifff", data)
        events.append([x, y, k])

events = np.array(events)

if len(events) == 0:
    print("Aucun événement trouvé.")
    exit()

x_vals = events[:, 0]
y_vals = events[:, 1]
k_vals = events[:, 2]

# Histogramme de k
plt.figure()
plt.hist(k_vals, bins=30)
plt.xlabel("Valeur de k")
plt.title("Distribution des valeurs de k")
plt.savefig("hist_k.png")
plt.close()

# Carte spatiale
plt.figure()
plt.scatter(x_vals, y_vals, s=8)
plt.xlabel("Position x (pixels)")
plt.ylabel("Position y (pixels)")
plt.title("Carte spatiale des événements")
plt.gca().invert_yaxis()
plt.savefig("map_xy.png")
plt.close()

print("Graphes sauvegardés : hist_k.png et map_xy.png")
