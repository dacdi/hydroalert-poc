from owslib.wms import WebMapService
import logging

logger = logging.getLogger(__name__)

def query_flood_depth(lat, lon, layer="rlp_sri07", time=""):
    wms_url = "https://wasserportal.rlp-umwelt.de/cgi-bin/mapserv?map=/www/data/umn/visdom/visdom.map"
    try:
        logger.debug(f"[WMS] Verbinde mit {wms_url}")
        wms = WebMapService(wms_url, version="1.3.0")
        bbox = (lon - 0.0005, lat - 0.0005, lon + 0.0005, lat + 0.0005)  # sehr kleiner Ausschnitt
        width, height = 101, 101
        i, j = width // 2, height // 2

        logger.debug(f"[WMS] Hole FeatureInfo für Koordinate ({lat}, {lon})")

        response = wms.getfeatureinfo(
            layers=[layer],
            srs='EPSG:4326',
            bbox=bbox,
            width=width,
            height=height,
            query_layers=[layer],
            info_format='text/plain',
            xy=(i, j)
        )
        content = response.read().decode("utf-8")
        logger.info(f"[WMS] Ergebnis für ({lat}, {lon}): {content.strip()}")
        return content.strip()
    except Exception as e:
        logger.error(f"[WMS] Fehler bei Abfrage: {e}")
        return None
