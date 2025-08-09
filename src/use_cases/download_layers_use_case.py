from argparse import Namespace
from logging import Logger
from typing import Iterable

from src.analysis.generate_layers import download_all_wms_layers, download_selected_layers
from src.utils.utils_logger import get_logger
from src.io.wms_client import BBox

logger: Logger = get_logger()

def run_download_layers_use_case(args: Namespace) -> None:
    """
    Orchestriert den Download-Use-Case.
    Optional unterstützt:
      - args.layers: Liste voller Layernamen (nur diese laden)
      - args.width/args.height: Bildgröße
      - args.minx/miny/maxx/maxy: BBox-Override
    """
    logger.info("🌐 Lade WMS-Layer …")

    selected: Iterable[str] | None = getattr(args, "layers", None)
    width = getattr(args, "width", None)
    height = getattr(args, "height", None)
    bbox_vals = tuple(getattr(args, k, None) for k in ("minx", "miny", "maxx", "maxy"))

    kwargs = {}
    if width and height:
        kwargs["size"] = (int(width), int(height))
    if all(v is not None for v in bbox_vals):
        kwargs["bbox"] = BBox(*(int(v) for v in bbox_vals))  # type: ignore[arg-type]

    if selected:
        download_selected_layers(selected, **kwargs)
    else:
        download_all_wms_layers(**kwargs)

    logger.info("✅ WMS-Layer wurden erfolgreich heruntergeladen.")
