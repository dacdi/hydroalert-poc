import os
import requests

from src.utils.utils_logger import get_logger
from src.config.config import WMS_LAYERS_DIR

logger = get_logger()


def download_all_wms_layers() -> None:
    """Downloads predefined WMS layers from the RLP geoserver and saves them as PNG files."""
    # Zielverzeichnis aus der Konfiguration laden
    output_dir = os.path.abspath(WMS_LAYERS_DIR)
    os.makedirs(output_dir, exist_ok=True)
    logger.info("📂 Zielverzeichnis: %s", output_dir)

    # Bounding Box für ca. 20x20 km² – Region Neustadt (EPSG:25832)
    bbox = "432000,5461000,452000,5481000"
    width, height = 2000, 2000

    # Liste der Layer
    layers = {
        "Visdom_SRI07_1h_WaterDepth": "Wassertiefe_SRI7_1h",
        "Visdom_SRI10_1h_WaterDepth": "Wassertiefe_SRI10_1h",
        "Visdom_SRI10_4h_WaterDepth": "Wassertiefe_SRI10_4h",
        "Visdom_SRI07_1h_FlowVelocity": "Fließgeschw_SRI7_1h",
        "Visdom_SRI10_1h_FlowVelocity": "Fließgeschw_SRI10_1h",
        "Visdom_SRI10_4h_FlowVelocity": "Fließgeschw_SRI10_4h",
        "Visdom_Schummerung": "Schummerung",
        "Visdom_Sinkpolygons": "Sinkpolygone"
    }

    # WMS-Basiskonfiguration
    base_url = "https://geodienste-wasser.rlp-umwelt.de/geoserver/Sturzflut/wms"

    for layer_name, short_name in layers.items():
        logger.info("⬇️ Lade Layer: %s", layer_name)

        params = {
            "service": "WMS",
            "version": "1.3.0",
            "request": "GetMap",
            "layers": layer_name,
            "bbox": bbox,
            "width": width,
            "height": height,
            "crs": "EPSG:25832",
            "format": "image/png"
        }

        try:
            response = requests.get(base_url, params=params)
            logger.debug("🌐 Request-URL: %s", response.url)
            logger.debug("📦 Antwort-Code: %s", response.status_code)
            logger.debug(
                "📦 Content-Type: %s",
                response.headers.get("Content-Type", "unbekannt"),
            )
            logger.debug("📏 Bildgröße (Bytes): %s", len(response.content))

            if response.status_code == 200 and response.headers.get("Content-Type") == "image/png":
                filename = os.path.join(output_dir, f"{short_name}.png")
                with open(filename, "wb") as file:
                    file.write(response.content)

                if os.path.isfile(filename):
                    logger.info("✅ Gespeichert: %s", filename)
                else:
                    logger.warning("⚠️ Datei wurde nicht geschrieben: %s", filename)
            else:
                logger.error("❌ Fehlerhafte Antwort oder kein PNG – Layer: %s", layer_name)

        except Exception:
            logger.exception("❌ Ausnahme beim Laden von %s", layer_name)


if __name__ == "__main__":
    download_all_wms_layers()
