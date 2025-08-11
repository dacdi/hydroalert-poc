# src/services/cache_generation_service.py

import os
import json
from glob import glob
from typing import Dict, Tuple, Optional, List

from osmnx import graph_from_point, graph_to_gdfs

from src.analysis.flood_overlay import detect_street_depths
from src.io.cache_store import write_depths_csv, write_depths_kml
from src.utils.naming import cache_path_for_latlon
from src.utils.utils_logger import get_logger
from src.config.config import WMS_LAYERS_DIR, DEFAULT_LAYERS  # {full: short}

logger = get_logger()


def _prepare_street_graph(lat: float, lon: float, radius_m: float):
    """OSM-Straßennetz um (lat, lon) laden und in benötigte CRS projizieren."""
    logger.info("📍 Ort: lat=%.6f, lon=%.6f, radius=%.1f m", lat, lon, radius_m)
    G = graph_from_point((lat, lon), dist=radius_m, network_type="drive", simplify=True)
    gdf_edges = graph_to_gdfs(G, nodes=False, edges=True)
    # Analyse erwartet UTM32 (EPSG:25832) und für KML WGS84 (EPSG:4326)
    return gdf_edges.to_crs(epsg=25832), gdf_edges.to_crs(epsg=4326)


def _resolve_png_path(layer_short: str, cache_dir: str) -> Optional[str]:
    """
    Bevorzugt WMS-PNG im Geo-Cache-Ordner, sonst globales WMS_LAYERS_DIR.
    Akzeptiert exakte und 'enthält'-Treffer (für flexible Dateinamen).
    """
    # 1) Geo-Cache: exakter Name
    cand = os.path.join(cache_dir, f"{layer_short}.png")
    if os.path.exists(cand):
        return cand
    # 2) Geo-Cache: fuzzy
    hits = glob(os.path.join(cache_dir, f"*{layer_short}*.png"))
    if hits:
        hits.sort(key=lambda p: (os.path.basename(p) != f"{layer_short}.png", len(os.path.basename(p))))
        return hits[0]
    # 3) Global: exakter Name
    cand = os.path.join(WMS_LAYERS_DIR, f"{layer_short}.png")
    if os.path.exists(cand):
        return cand
    # 4) Global: fuzzy
    hits = glob(os.path.join(WMS_LAYERS_DIR, f"*{layer_short}*.png"))
    if hits:
        hits.sort(key=lambda p: (os.path.basename(p) != f"{layer_short}.png", len(os.path.basename(p))))
        return hits[0]
    return None


def _load_meta_file(cache_dir: str) -> Tuple[Tuple[int, int, int, int], Tuple[int, int]]:
    """
    Liest meta.json im Geo-Ordner und liefert (bbox_utm, raster_size).
    meta.json Format:
    {
      "bbox_utm": [minx, miny, maxx, maxy],
      "raster_size": [width, height],
      "crs": "EPSG:25832"
    }
    """
    meta_path = os.path.join(cache_dir, "meta.json")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Meta-Datei fehlt: {meta_path}. Bitte zuerst 'download-layers' ausführen.")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    bbox_vals: List[int] = meta["bbox_utm"]
    raster_vals: List[int] = meta["raster_size"]
    if len(bbox_vals) != 4 or len(raster_vals) != 2:
        raise ValueError(f"Ungültiges meta.json Format: {meta_path}")
    bbox_utm = (int(bbox_vals[0]), int(bbox_vals[1]), int(bbox_vals[2]), int(bbox_vals[3]))
    raster_size = (int(raster_vals[0]), int(raster_vals[1]))
    logger.debug("🧭 meta.json geladen: bbox_utm=%s, raster_size=%s", bbox_utm, raster_size)
    return bbox_utm, raster_size


def generate_cache_for_location(
    lat: float,
    lon: float,
    *,
    radius_m: float = 4000.0,
    sample_distance_m: float = 2.5,
    layers: Optional[list[str]] = None,  # z. B. ["Wassertiefe_SRI7_1h", ...]
) -> Dict[str, str]:
    """
    Erzeugt je Layer CSV + KML im Geo-Cache-Ordner.
    Rückgabe: {layer_short: "ok" | "empty" | "missing_png"}
    """
    # Welche Layer?
    if layers is None:
        layers = list(DEFAULT_LAYERS.values())

    # Geo-Ordner + Metadaten laden
    cache_dir = cache_path_for_latlon(lat, lon)
    os.makedirs(cache_dir, exist_ok=True)
    logger.info("🗂️ Cache-Ordner: %s", cache_dir)

    bbox_utm, raster_size = _load_meta_file(cache_dir)

    # Straßen vorbereiten
    gdf_utm, gdf_wgs = _prepare_street_graph(lat, lon, radius_m)
    logger.debug("Anzahl Straßen: %s",len(gdf_utm))

    status: Dict[str, str] = {}
    for layer_short in layers:
        png_path = _resolve_png_path(layer_short, cache_dir)
        if not png_path:
            logger.warning("⚠️ PNG nicht gefunden (Geo-Cache & global): %s", layer_short)
            status[layer_short] = "missing_png"
            continue

        logger.info("🔄 Layer: %s  |  PNG: %s", layer_short, os.path.relpath(png_path))
        depths = detect_street_depths(
            gdf_utm,
            png_path=png_path,
            bbox_utm=bbox_utm,
            raster_size=raster_size,
            sample_distance_m=sample_distance_m,
        )

        csv_out = os.path.join(cache_dir, f"flood_{layer_short}.csv")
        kml_out = os.path.join(cache_dir, f"flood_{layer_short}.kml")
        write_depths_csv(depths, csv_out)
        write_depths_kml(depths, gdf_wgs, kml_out)

        status[layer_short] = "ok" if depths else "empty"

    logger.info("✅ Generate-Cache fertig: %s", status)
    return status
