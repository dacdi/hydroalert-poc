# src/analysis/flood_overlay.py

import numpy as np
from PIL import Image
from shapely.ops import substring
from shapely.geometry import LineString
from typing import Dict, List, Optional, Tuple
from src.utils.utils_logger import get_logger

logger = get_logger()

#ToDo: PRüfne, sollte das in das config?
COLOR_TO_DEPTH: Dict[Tuple[int, int, int], str] = {
    (255, 255, 255): "<5 cm",        # Weiß (Hintergrund)
    (189, 215, 238): "5–10 cm",      # Hellblau
    (47, 117, 181): "10–30 cm",      # Mittelblau
    (0, 0, 255): "30–50 cm",         # Blau
    (255, 0, 255): "50–100 cm",      # Magenta
    (234, 125, 185): "100–200 cm",   # Rosa
    (204, 0, 153): "200–400 cm",     # Dunkelrosa/Lila
    (128, 0, 128): ">=400 cm",       # Dunkellila
}


def load_png_as_array(png_path: str) -> np.ndarray:
    """Load the flood layer PNG and convert it into an RGBA array."""
    img = Image.open(png_path).convert("RGBA")
    return np.array(img)


def utm_to_pixel(
    x_utm: float,
    y_utm: float,
    bbox_utm: Tuple[float, float, float, float],
    raster_size: Tuple[int, int],
) -> Tuple[int, int]:
    """Convert UTM coordinates to pixel indices within the raster.

    Stellt sicher, dass die zurückgegebenen Pixelindizes immer innerhalb
    der gültigen Rastergrenzen (0 <= px < width, 0 <= py < height) liegen.
    Dies verhindert Off-by-One-Fehler, die auftreten, wenn Koordinaten
    exakt auf der max-Kante der BBOX liegen.
    """
    x_min, y_min, x_max, y_max = bbox_utm
    width_px, height_px = raster_size

    # Berechnung
    px_float = (x_utm - x_min) / (x_max - x_min) * width_px
    py_float = (y_max - y_utm) / (y_max - y_min) * height_px

    # Clamp auf gültigen Bereich
    px = min(width_px - 1, max(0, int(px_float)))
    py = min(height_px - 1, max(0, int(py_float)))

    return px, py



def depth_from_color(r: int, g: int, b: int, a: int) -> Optional[str]:
    """Map an RGBA color to a depth category, ignoring transparent pixels."""
    if a == 0:
        return None
    return COLOR_TO_DEPTH.get((r, g, b))


def collect_depths_along_line(
    geom: LineString,
    arr: np.ndarray,
    bbox_utm: Tuple[float, float, float, float],
    raster_size: Tuple[int, int],
    sample_distance_m: float,
) -> List[str]:
    """Sample depth categories along a street geometry."""
    max_depths: List[str] = []
    length = geom.length
    for d in np.arange(0, length, sample_distance_m):
        x_utm, y_utm = substring(geom, d, d).coords[0]
        px, py = utm_to_pixel(x_utm, y_utm, bbox_utm, raster_size)
        width_px, height_px = raster_size
        if not (0 <= px < width_px and 0 <= py < height_px):
            continue
        r, g, b, a = arr[py, px]
        depth = depth_from_color(r, g, b, a)
        if depth:
            max_depths.append(depth)
    return max_depths


def pick_deepest_depth(depths: List[str]) -> Optional[str]:
    """Choose the deepest flood depth from a list of categories."""
    if not depths:
        return None
    palette = list(COLOR_TO_DEPTH.values())
    return sorted(depths, key=lambda t: palette.index(t))[-1]


def detect_street_depths(
    gdf_edges,
    png_path: str,
    bbox_utm: Tuple[float, float, float, float],
    raster_size: Tuple[int, int],
    sample_distance_m: float = 5.0,
) -> Dict[str, str]:
    """Determine the flood depth for each street in the graph."""
    arr = load_png_as_array(png_path)
    street_depths: Dict[str, str] = {}
    for _, row in gdf_edges.iterrows():
        geom: LineString = row.geometry
        name = row.get("name") if isinstance(row.get("name"), str) else "<unbenannt>"
        depths = collect_depths_along_line(
            geom,
            arr,
            bbox_utm=bbox_utm,
            raster_size=raster_size,
            sample_distance_m=sample_distance_m,
        )
        chosen = pick_deepest_depth(depths)
        if chosen:
            street_depths[name] = chosen
    logger.info(f"🔹 Detektierte Tiefen für {len(street_depths)} Straßen")
    return street_depths
