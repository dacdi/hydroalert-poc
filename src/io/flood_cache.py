import os
import csv
from osmnx import graph_from_point, graph_to_gdfs
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
    Erzeugt für jeden Layer (SRI7, SRI10, SRI10_4h) eine CSV mit
    überfluteten Straßen und Tiefen, und speichert in data/cache.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)

    lat, lon = get_default_location()
    logger.info(f"📍 Standardort: lat={lat}, lon={lon}")
    # Straßen einmal laden
    G = graph_from_point((lat, lon), dist=radius_m, network_type="drive", simplify=True)
    gdf_edges = graph_to_gdfs(G, nodes=False, edges=True).to_crs(epsg=25832)

    for key, png_path in LAYERS.items():
        logger.info(f"🔄 Berechne Cache für: {key}")
        depths = detect_street_depths(
            gdf_edges,
            png_path=png_path,
            bbox_utm=(432000, 5461000, 452000, 5481000),
            raster_size=(2000, 2000),
            sample_distance_m=sample_distance_m,
        )
        out_path = os.path.join(CACHE_DIR, f"flood_{key}.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["street", "depth"])
            for street, depth in depths.items():
                writer.writerow([street, depth])
        logger.info(f"✅ CSV-Cache geschrieben: {out_path}")
