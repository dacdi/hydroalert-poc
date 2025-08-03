#!/usr/bin/env python3
"""
flood_cache.py

Erzeugt für jeden Layer (SRI7, SRI10, SRI10_4h):
1. Eine CSV mit überfluteten Straßen und Tiefen
2. Eine KML-Datei mit Punkten auf den Straßen und Tiefenangabe

Speichert beides im Cache-Verzeichnis.

HydroPrompt-Richtlinien:
- Klare Log-Ausgaben
- Einheitliche Struktur und saubere Fehlertexte
- Hauptsteuerung über `main`
"""
import os
import csv
from osmnx import graph_from_point, graph_to_gdfs
from simplekml import Kml
from src.analysis.flood_overlay import detect_street_depths
from src.io.load_locations import get_default_location
from src.utils.utils_logger import get_logger

logger = get_logger()
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cache")
LAYERS = {
    "SRI7":    "data/wms_layers/Wassertiefe_SRI7_1h.png",
    "SRI10":   "data/wms_layers/Wassertiefe_SRI10_1h.png",
    "SRI10_4h":"data/wms_layers/Wassertiefe_SRI10_4h.png",
}

def generate_csv_cache(radius_m: float = 200.0, sample_distance_m: float = 5.0) -> None:
    """
    Erzeugt für jeden Layer eine CSV und eine KML-Datei mit Tiefendaten.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)

    lat, lon = get_default_location()
    logger.info(f"📍 Standardort: lat={lat}, lon={lon}")
    G = graph_from_point((lat, lon), dist=radius_m, network_type="drive", simplify=True)
    gdf_edges = graph_to_gdfs(G, nodes=False, edges=True)
    gdf_utm = gdf_edges.to_crs(epsg=25832)

    for key, png_path in LAYERS.items():
        logger.info(f"🔄 Berechne Cache für: {key}")
        depths = detect_street_depths(
            gdf_utm,
            png_path=png_path,
            bbox_utm=(432000, 5461000, 452000, 5481000),
            raster_size=(2000, 2000),
            sample_distance_m=sample_distance_m,
        )

        # CSV-Ausgabe
        csv_path = os.path.join(CACHE_DIR, f"flood_{key}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["street", "depth"])
            for street, depth in depths.items():
                writer.writerow([street, depth])
        logger.info(f"✅ CSV-Cache geschrieben: {csv_path}")

        # KML-Ausgabe
        edges_wgs = gdf_edges.to_crs(epsg=4326)
        kml = Kml()
        for _, row in edges_wgs.iterrows():
            names = row.get("name")
            if not names:
                continue
            # Falls mehrere Namen vorhanden sind, wähle einen, der im depths-Dict ist
            if isinstance(names, list):
                street_names = [n for n in names if n in depths]
                if not street_names:
                    continue
                street_name = street_names[0]
            else:
                if names not in depths:
                    continue
                street_name = names
            geom = row.geometry
            if geom.is_empty:
                continue
            midpoint = geom.interpolate(0.5, normalized=True)
            lon_mid, lat_mid = midpoint.x, midpoint.y
            p = kml.newpoint(name=street_name, coords=[(lon_mid, lat_mid)])
            p.description = f"Tiefe: {depths[street_name]}"

        kml_path = os.path.join(CACHE_DIR, f"flood_{key}.kml")
        kml.save(kml_path)
        logger.info(f"✅ KML-Cache geschrieben: {kml_path}")

if __name__ == "__main__":
    generate_csv_cache()
