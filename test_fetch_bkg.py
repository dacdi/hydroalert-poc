import logging
from pathlib import Path
from src.fetch_bkg_wms import fetch_starkregenkarte_bkg

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # Testgebiet irgendwo in Rheinland-Pfalz oder NRW
    bbox = (7.0, 50.0, 7.1, 50.1)
    layer = "tiefe_extrem"

    img = fetch_starkregenkarte_bkg(layer, bbox)

    if img:
        output_path = Path("output/starkregenkarte_bkg.png")
        output_path.parent.mkdir(exist_ok=True)
        img.save(output_path)
        print(f"✅ Karte gespeichert unter: {output_path}")
    else:
        print("❌ Karte konnte nicht geladen werden.")

