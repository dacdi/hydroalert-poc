# src/services/cache_generation_service.py
import os
from glob import glob
from typing import Dict, Tuple, Optional
from osmnx import graph_from_point, graph_to_gdfs
from src.analysis.flood_overlay import detect_street_depths
from src.io.cache_store import write_depths_csv, write_depths_kml
from src.utils.naming import cache_path_for_latlon
from src.utils.utils_logger import get_logger
from src.config.config import WMS_LAYERS_DIR, DEFAULT_LAYERS

logger = get_logger()

BBOX_UTM: Tuple[float, float, float, float] = (432000, 5461000, 452000, 5481000)
RASTER_SIZE: Tuple[int, int] = (2000, 2000)

def _prepare_street_graph(lat: float, lon: float, radius_m: float):
    logger.info("📍 Ort: lat=%.6f, lon=%.6f, radius=%.1f m", lat, lon, radius_m)
    G = graph_from_point((lat, lon), dist=radius_m, network_type="drive", simplify=True)
    gdf_edges = graph_to_gdfs(G, nodes=False, edges=True)
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
    # 2) Geo-Cache: fuzzy (z. B. Präfix/Suffix)
    hits = glob(os.path.join(cache_dir, f"*{layer_short}*.png"))
    if hits:
        # nimm den „besten“ Treffer: bevorzugt voller Name am Ende
        hits.sort(key=lambda p: (os.path.basename(p) != f"{layer_short}.png", len(os.path.basename(p))))
        return hits[0]
    # 3) Globaler Ordner: exakter Name
    cand = os.path.join(WMS_LAYERS_DIR, f"{layer_short}.png")
    if os.path.exists(cand):
        return cand
    # 4) Global: fuzzy
    hits = glob(os.path.join(WMS_LAYERS_DIR, f"*{layer_short}*.png"))
    if hits:
        hits.sort(key=lambda p: (os.path.basename(p) != f"{layer_short}.png", len(os.path.basename(p))))
        return hits[0]
    return None

def generate_cache_for_location(
    lat: float,
    lon: float,
    *,
    radius_m: float = 300.0,
    sample_distance_m: float = 5.0,
    layers: Optional[list[str]] = None,  # e.g. ["Wassertiefe_SRI7_1h", ...]
) -> Dict[str, str]:
    if layers is None:
        layers = list(DEFAULT_LAYERS.values())

    cache_dir = cache_path_for_latlon(lat, lon)
    os.makedirs(cache_dir, exist_ok=True)
    logger.info("🗂️ Cache-Ordner: %s", cache_dir)

    gdf_utm, gdf_wgs = _prepare_street_graph(lat, lon, radius_m)

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
            bbox_utm=BBOX_UTM,
            raster_size=RASTER_SIZE,
            sample_distance_m=sample_distance_m,
        )

        csv_out = os.path.join(cache_dir, f"flood_{layer_short}.csv")
        kml_out = os.path.join(cache_dir, f"flood_{layer_short}.kml")
        write_depths_csv(depths, csv_out)
        write_depths_kml(depths, gdf_wgs, kml_out)
        status[layer_short] = "ok" if depths else "empty"

    logger.info("✅ Generate-Cache fertig: %s", status)
    return status
