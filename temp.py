#!/usr/bin/env python3
"""
temp_flood_demo.py

Lädt OSM-Straßen im 200 m-Radius um einen festen Punkt,
lädt eine WMS-Flutkarte als PNG und gibt eine Liste
der überfluteten Straßennamen zurück.
"""

import logging
from typing import List, Tuple

import numpy as np
import osmnx as ox
from PIL import Image
from shapely.ops import substring
from shapely.geometry import LineString
from pyproj import Transformer

# -------------------------
# Konfiguration
# -------------------------
LATITUDE = 49.3501
LONGITUDE = 8.1376
RADIUS_METERS = 200

PNG_PATH = "data/wms_layers/Wassertiefe_SRI7_1h.png"
BBOX_UTM: Tuple[float, float, float, float] = (
    432000.0,
    5461000.0,
    452000.0,
    5481000.0,
)
RASTER_SIZE: Tuple[int, int] = (2000, 2000)
SAMPLE_DISTANCE_M = 5.0

# -------------------------
# Logging
# -------------------------
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_streets(lat: float, lon: float, radius: float):
    """Lädt das Straßennetz um (lat, lon) im gegebenen Radius (Meter)."""
    logger.info(f"Lade OSM-Straßen um ({lat}, {lon}) mit Radius {radius} m …")
    graph = ox.graph_from_point(
        (lat, lon),
        dist=radius,
        network_type="drive",
        simplify=True,
    )
    return graph


def detect_flooded_streets(
    gdf_edges,
    png_path: str,
    bbox_utm: Tuple[float, float, float, float],
    raster_size: Tuple[int, int],
    sample_distance: float,
) -> List[str]:
    """
    Ermittelt, welche Straßenabschnitte von der Flutmaske getroffen werden.
    """
    # Bild laden und Alphamaske erzeugen
    img = Image.open(png_path).convert("RGBA")
    arr = np.array(img)
    mask = arr[:, :, 3] > 0  # True = überflutet

    width_px, height_px = raster_size
    x_min, y_min, x_max, y_max = bbox_utm

    flooded = set()
    for _, row in gdf_edges.iterrows():
        geom: LineString = row.geometry

        # Nur Strings als Namen akzeptieren
        raw_name = row.get("name")
        if isinstance(raw_name, str):
            name = raw_name
        else:
            name = "<unbenannt>"

        length = geom.length
        distances = np.arange(0, length, sample_distance)
        for d in distances:
            point = substring(geom, d, d).coords[0]
            x_utm, y_utm = point

            px = int((x_utm - x_min) / (x_max - x_min) * width_px)
            py = int((y_max - y_utm) / (y_max - y_min) * height_px)

            if 0 <= px < width_px and 0 <= py < height_px and mask[py, px]:
                flooded.add(name)
                break

    logger.info(f"🔹 Gefundene überflutete Straßen: {len(flooded)}")
    return sorted(flooded)


if __name__ == "__main__":
    # 1) OSM-Straßen laden und projizieren
    graph = load_streets(LATITUDE, LONGITUDE, RADIUS_METERS)
    gdf_edges = ox.graph_to_gdfs(graph, nodes=False, edges=True).to_crs(epsg=25832)

    # 2) Überflutete Straßen ermitteln
    flooded_streets = detect_flooded_streets(
        gdf_edges,
        PNG_PATH,
        BBOX_UTM,
        RASTER_SIZE,
        SAMPLE_DISTANCE_M,
    )

    # 3) Ausgabe
    if flooded_streets:
        logger.info("🚨 Überflutete Straßen:")
        for street in flooded_streets:
            print(f"- {street}")
    else:
        logger.info("✅ Keine überfluteten Straßen gefunden.")
