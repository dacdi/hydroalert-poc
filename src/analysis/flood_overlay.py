import numpy as np
from PIL import Image
from shapely.ops import substring
from shapely.geometry import LineString
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# 1) Definiere dein Farb-→Tiefen-Mapping (RGB ohne Alpha)
COLOR_TO_DEPTH: Dict[Tuple[int, int, int], str] = {
    (235, 235, 235): "<5 cm",     # Weiß-Ross, transparent in Maske
    (204, 229, 255): "5–10 cm",   # Hellblau
    (102, 153, 204): "10–30 cm",  # Dunkelblau
    (0, 0, 255):   "30–50 cm",    # Blau
    (255, 0, 255): "50–100 cm",   # Magenta
    (255, 102, 178): "100–200 cm",# Rosa
    (204, 0, 102):  "200–400 cm", # Dunkelrosa
    (102, 0, 51):   ">=400 cm",   # Dunkellila
    # … passe Werte exakt an deine PNG-Palette an
}


def detect_street_depths(
    gdf_edges,
    png_path: str,
    bbox_utm: Tuple[float, float, float, float],
    raster_size: Tuple[int, int],
    sample_distance_m: float = 5.0
) -> Dict[str, str]:
    """
    Für jede Straße die maximale (oder häufigste) Flut-Tiefe ermitteln,
    anhand der Farbwerte in der WMS-PNG.

    Returns:
        Dict[str, str]: Straßenname → Tiefe als Text („50–100 cm“).
    """
    # Bild laden
    img = Image.open(png_path).convert("RGBA")
    arr = np.array(img)
    width_px, height_px = raster_size
    x_min, y_min, x_max, y_max = bbox_utm

    street_depths: Dict[str, List[str]] = {}

    for _, row in gdf_edges.iterrows():
        geom: LineString = row.geometry
        name = row.get("name") if isinstance(row.get("name"), str) else "<unbenannt>"

        # Stichproben entlang der Linie
        max_depths: List[str] = []
        length = geom.length
        for d in np.arange(0, length, sample_distance_m):
            x_utm, y_utm = substring(geom, d, d).coords[0]

            px = int((x_utm - x_min) / (x_max - x_min) * width_px)
            py = int((y_max - y_utm) / (y_max - y_min) * height_px)

            if not (0 <= px < width_px and 0 <= py < height_px):
                continue

            r, g, b, a = arr[py, px]
            if a == 0:
                continue  # kein Wasser hier

            depth = COLOR_TO_DEPTH.get((r, g, b))
            if depth:
                max_depths.append(depth)

        if max_depths:
            # z.B. häufigster Wert oder der max. kategoriale Bereich
            # hier: wir nehmen den „tiefsten“ Bereich, indem wir nach
            # Palette-Reihenfolge sortieren (Index im Dict-Key-List)
            palette = list(COLOR_TO_DEPTH.values())
            chosen = sorted(max_depths, key=lambda t: palette.index(t))[-1]
            street_depths[name] = chosen

    logger.info(f"🔹 Detektierte Tiefen für {len(street_depths)} Straßen")
    return street_depths
