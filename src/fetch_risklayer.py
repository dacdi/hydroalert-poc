from owslib.wms import WebMapService
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def fetch_starkregenkarte_bkg(layer, bbox, width=800, height=600):
    """
    Holt eine Starkregenkarte vom BKG-WMS-Dienst.
    :param layer: Layer-Name, z. B. 'bkg:Starkregen_Stufe3'
    :param bbox: (minx, miny, maxx, maxy) – geografischer Ausschnitt
    :return: PIL.Image oder None
    """
    wms_url = "https://sgx.geodatenzentrum.de/wms_starkregen"
    try:
        logger.debug(f"[WMS] Verbinde mit {wms_url}")
        wms = WebMapService(wms_url, version='1.3.0')
        logger.debug(f"[WMS] Verfügbare Layer: {list(wms.contents.keys())}")

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
