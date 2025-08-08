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
import csv
import os
from typing import Dict, Tuple

from osmnx import graph_from_point, graph_to_gdfs
from simplekml import Kml

from src.analysis.flood_overlay import detect_street_depths
from src.io.load_locations import get_default_location
from src.utils.utils_logger import get_logger
from src.config.config import WMS_LAYERS_DIR, CACHE_DIR

logger = get_logger()

LAYERS = {
    "SRI7": os.path.join(WMS_LAYERS_DIR, "Wassertiefe_SRI7_1h.png"),
    "SRI10": os.path.join(WMS_LAYERS_DIR, "Wassertiefe_SRI10_1h.png"),
    "SRI10_4h": os.path.join(WMS_LAYERS_DIR, "Wassertiefe_SRI10_4h.png"),
}

BBOX_UTM: Tuple[float, float, float, float] = (432000, 5461000, 452000, 5481000)
RASTER_SIZE: Tuple[int, int] = (2000, 2000)


def prepare_street_graph(radius_m: float) -> Tuple[object, object]:
    """Build street graph around the default location and return UTM and WGS84 edges."""
    lat, lon = get_default_location()
    logger.info(f"📍 Standardort: lat={lat}, lon={lon}")
    G = graph_from_point((lat, lon), dist=radius_m, network_type="drive", simplify=True)
    gdf_edges = graph_to_gdfs(G, nodes=False, edges=True)
    return gdf_edges.to_crs(epsg=25832), gdf_edges.to_crs(epsg=4326)


def compute_depths(gdf_utm, png_path: str, sample_distance_m: float) -> Dict[str, str]:
    """Run street depth detection for a single layer."""
    return detect_street_depths(
        gdf_utm,
        png_path=png_path,
        bbox_utm=BBOX_UTM,
        raster_size=RASTER_SIZE,
        sample_distance_m=sample_distance_m,
    )


def write_depths_csv(depths: Dict[str, str], path: str) -> None:
    """Write detected depths to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["street", "depth"])
        for street, depth in depths.items():
            writer.writerow([street, depth])
    logger.info(f"✅ CSV-Cache geschrieben: {path}")


def choose_street_name(names, depths: Dict[str, str]) -> str | None:
    """Return a matching street name from OSM attributes."""
    if isinstance(names, list):
        for n in names:
            if n in depths:
                return n
        return None
    if isinstance(names, str) and names in depths:
        return names
    return None


def write_depths_kml(depths: Dict[str, str], gdf_edges_wgs, path: str) -> None:
    """Write detected depths to a KML file."""
    kml = Kml()
    for _, row in gdf_edges_wgs.iterrows():
        street_name = choose_street_name(row.get("name"), depths)
        if not street_name:
            continue
        geom = row.geometry
        if geom.is_empty:
            continue
        midpoint = geom.interpolate(0.5, normalized=True)
        lon_mid, lat_mid = midpoint.x, midpoint.y
        p = kml.newpoint(name=street_name, coords=[(lon_mid, lat_mid)])
        p.description = f"Tiefe: {depths[street_name]}"
    kml.save(path)
    logger.info(f"✅ KML-Cache geschrieben: {path}")


def process_layer(
    key: str,
    png_path: str,
    gdf_utm,
    gdf_wgs,
    cache_dir: str,
    sample_distance_m: float,
) -> None:
    """Compute depths for a layer and write CSV and KML outputs."""
    logger.info(f"🔄 Berechne Cache für: {key}")
    depths = compute_depths(gdf_utm, png_path, sample_distance_m)
    write_depths_csv(depths, os.path.join(cache_dir, f"flood_{key}.csv"))
    write_depths_kml(depths, gdf_wgs, os.path.join(cache_dir, f"flood_{key}.kml"))


def generate_csv_cache(radius_m: float = 200.0, sample_distance_m: float = 5.0) -> None:
    """Erzeugt für jeden Layer eine CSV und eine KML-Datei mit Tiefendaten."""
    cache_dir = os.path.abspath(CACHE_DIR)
    os.makedirs(cache_dir, exist_ok=True)

    gdf_utm, gdf_wgs = prepare_street_graph(radius_m)

    for key, png_path in LAYERS.items():
        process_layer(key, png_path, gdf_utm, gdf_wgs, cache_dir, sample_distance_m)

if __name__ == "__main__":
    generate_csv_cache()
