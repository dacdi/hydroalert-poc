import os
import json

from typing import Tuple

from src.utils.utils_logger import get_logger
from src.domain.models import BBox

logger = get_logger()

def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)

def save_png(content: bytes, output_dir: str, short_name: str) -> str:
    filename = os.path.join(output_dir, f"{short_name}.png")
    with open(filename, "wb") as f:
        f.write(content)
    logger.info("✅ Saved: %s", filename)
    return filename



def load_meta_file(meta_path: str) -> Tuple[BBox, Tuple[int, int]]:
    """Liest meta.json und gibt BBox und Rastergröße zurück."""
    logger.debug(f"📄 Lade Meta-Datei: {meta_path}")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Meta-Datei nicht gefunden: {meta_path}")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    bbox_vals = meta["bbox_utm"]
    raster_size = tuple(meta["raster_size"])
    bbox = BBox(*bbox_vals)
    logger.debug(f"✅ Geladene BBox: {bbox}, Rastergröße: {raster_size}")
    return bbox, raster_size
