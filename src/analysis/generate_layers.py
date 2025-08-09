from typing import Mapping, Iterable
from src.io.wms_client import build_wms_params, fetch_wms_png, BBox
from src.io.file_io import ensure_dir, save_png
from src.config.config import (
    WMS_LAYERS_DIR, WMS_BASE_URL, DEFAULT_BBOX, DEFAULT_SIZE, DEFAULT_LAYERS
)
from src.utils.utils_logger import get_logger

logger = get_logger()

def download_all_wms_layers(
    layers: Mapping[str, str] | None = None,
    bbox: BBox = DEFAULT_BBOX,
    size: tuple[int, int] = DEFAULT_SIZE,
    base_url: str = WMS_BASE_URL,
    outdir: str = WMS_LAYERS_DIR,
) -> list[str]:
    """Lädt alle vordefinierten WMS-Layer und speichert sie als PNG. Gibt die Pfade zurück."""
    layers = layers or DEFAULT_LAYERS
    outpath = ensure_dir(outdir)
    w, h = size
    saved: list[str] = []

    for full_layer, short_name in layers.items():
        logger.info("⬇️ Downloading layer: %s", full_layer)
        params = build_wms_params(full_layer, bbox, w, h)
        content = fetch_wms_png(base_url, params)
        saved.append(save_png(content, outpath, short_name))

    logger.info("✅ %d Layer gespeichert in %s", len(saved), outpath)
    return saved

def download_selected_layers(
    selected: Iterable[str],
    layers: Mapping[str, str] | None = None,
    **kwargs,
) -> list[str]:
    """Lädt nur ausgewählte Layer (Keys = volle Layernamen)."""
    layers = layers or DEFAULT_LAYERS
    submap = {k: layers[k] for k in selected if k in layers}
    return download_all_wms_layers(layers=submap, **kwargs)
