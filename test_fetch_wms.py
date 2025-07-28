# test_fetch_wms.py

from src.fetch_risklayer import fetch_rlp_risk_map
import matplotlib.pyplot as plt

if __name__ == "__main__":
    bbox = (6.570, 49.700, 6.575, 49.705)  # Beispiel: kleine Region bei Konz
    layer = "Sturzflut:Visdom_SRI07_1h_WaterDepth"  # Layer-Name evtl. mit Prefix

    img = fetch_rlp_risk_map(layer, bbox)

    if img:
        plt.imshow(img)
        plt.title("Sturzflutkarte SRI07 – RLP Live via WMS")
        plt.axis("off")
        plt.show()
    else:
        print("❌ Kein Bild erhalten.")
