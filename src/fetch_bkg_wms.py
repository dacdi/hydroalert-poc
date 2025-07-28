from owslib.wms import WebMapService
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def fetch_starkregenkarte_bkg(layer, bbox, width=800, height=600):
    wms_url = "https://sgx.geodatenzentrum.de/wms_starkregen"

    try:
        logger.debug(f"[WMS] Verbinde mit {wms_url}")
        wms = WebMapService(wms_url, version='1.3.0')

        logger.debug(f"[WMS] Verfügbare Layer: {list(wms.contents.keys())}")
        if layer not in wms.contents:
            logger.error(f"[WMS] Layer '{layer}' nicht verfügbar.")
            return None

        response = wms.getmap(
            layers=[layer],
            srs='EPSG:4326',
            bbox=bbox,
            width=width,
            height=height,
            format='image/png',
            transparent=True
        )

        img = Image.open(BytesIO(response.read()))
        logger.info(f"[WMS] Bild erfolgreich geladen: {img.size}")
        return img

    except Exception as e:
        logger.error(f"[WMS] Fehler beim Abrufen der Karte: {e}")
        return None

