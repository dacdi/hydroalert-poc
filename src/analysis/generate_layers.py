import os
from typing import List, Optional
from src.io.wms_client import build_wms_params, fetch_wms_png, BBox
from src.io.file_io import ensure_dir, save_png
from src.config.config import (
    WMS_LAYERS_DIR, WMS_BASE_URL, DEFAULT_BBOX, DEFAULT_SIZE, DEFAULT_LAYERS
)
from src.utils.utils_logger import get_logger

from src.services.wms_downloader import download_all_wms_layers  # re-export


logger = get_logger()

def download_all_wms_layers(bbox: Optional[BBox] = None, target_dir: Optional[str] = None) -> List[str]:
    """
    Lädt alle vordefinierten WMS-Layer.
    - Standard: speichert nach WMS_LAYERS_DIR
    - Wenn target_dir gesetzt: speichert dorthin (z. B. data/cache/latXX_lonYY/)
    """
    outdir_base = target_dir if target_dir else WMS_LAYERS_DIR
    outdir = ensure_dir(outdir_base)

    w, h = DEFAULT_SIZE
    use_bbox = bbox or DEFAULT_BBOX
    saved: List[str] = []

    for full_layer, short_name in DEFAULT_LAYERS.items():
        logger.info("⬇️ Downloading layer: %s", full_layer)
        params = build_wms_params(full_layer, use_bbox, w, h)
        content = fetch_wms_png(WMS_BASE_URL, params)
        saved.append(save_png(content, outdir, short_name))

    logger.info("✅ %d Layer gespeichert in %s", len(saved), outdir)
    return saved
