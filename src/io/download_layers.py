import os
import requests
from typing import Dict

from src.utils.utils_logger import get_logger
from src.config.config import WMS_LAYERS_DIR

logger = get_logger()


def build_wms_params(layer_name: str, bbox: str, width: int, height: int) -> Dict[str, str]:
    """Create WMS request parameters for a single layer."""
    return {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetMap",
        "layers": layer_name,
        "bbox": bbox,
        "width": width,
        "height": height,
        "crs": "EPSG:25832",
        "format": "image/png",
    }


def request_wms_image(base_url: str, params: Dict[str, str]) -> bytes | None:
    """Request a WMS layer and return image bytes on success."""
    try:
        response = requests.get(base_url, params=params)
        logger.debug("🌐 Request-URL: %s", response.url)
        logger.debug("📦 Antwort-Code: %s", response.status_code)
        logger.debug(
            "📦 Content-Type: %s",
            response.headers.get("Content-Type", "unbekannt"),
        )
        if response.status_code == 200 and response.headers.get("Content-Type") == "image/png":
            logger.debug("📏 Bildgröße (Bytes): %s", len(response.content))
            return response.content
        logger.error("❌ Fehlerhafte Antwort oder kein PNG – Layer: %s", params["layers"])
    except Exception:
        logger.exception("❌ Ausnahme beim Laden von %s", params.get("layers"))
    return None


def save_png(content: bytes, output_dir: str, short_name: str) -> None:
    """Persist a PNG image to disk."""
    filename = os.path.join(output_dir, f"{short_name}.png")
    with open(filename, "wb") as file:
        file.write(content)
    if os.path.isfile(filename):
        logger.info("✅ Gespeichert: %s", filename)
    else:
        logger.warning("⚠️ Datei wurde nicht geschrieben: %s", filename)


def download_layer(
    layer_name: str,
    short_name: str,
    base_url: str,
    bbox: str,
    width: int,
    height: int,
    output_dir: str,
) -> None:
    """Download a single WMS layer and save it as PNG."""
    logger.info("⬇️ Lade Layer: %s", layer_name)
    params = build_wms_params(layer_name, bbox, width, height)
    content = request_wms_image(base_url, params)
    if content:
        save_png(content, output_dir, short_name)


def download_all_wms_layers() -> None:
    """Download predefined WMS layers from the RLP geoserver and save them as PNG files."""
    output_dir = os.path.abspath(WMS_LAYERS_DIR)
    os.makedirs(output_dir, exist_ok=True)
    logger.info("📂 Zielverzeichnis: %s", output_dir)

    bbox = "432000,5461000,452000,5481000"  # Region Neustadt (EPSG:25832)
    width, height = 2000, 2000

    layers = {
        "Visdom_SRI07_1h_WaterDepth": "Wassertiefe_SRI7_1h",
        "Visdom_SRI10_1h_WaterDepth": "Wassertiefe_SRI10_1h",
        "Visdom_SRI10_4h_WaterDepth": "Wassertiefe_SRI10_4h",
        "Visdom_SRI07_1h_FlowVelocity": "Fließgeschw_SRI7_1h",
        "Visdom_SRI10_1h_FlowVelocity": "Fließgeschw_SRI10_1h",
        "Visdom_SRI10_4h_FlowVelocity": "Fließgeschw_SRI10_4h",
        "Visdom_Schummerung": "Schummerung",
        "Visdom_Sinkpolygons": "Sinkpolygone",
    }

    base_url = "https://geodienste-wasser.rlp-umwelt.de/geoserver/Sturzflut/wms"
    for layer_name, short_name in layers.items():
        download_layer(layer_name, short_name, base_url, bbox, width, height, output_dir)


if __name__ == "__main__":
    download_all_wms_layers()

