import os
import osmnx as ox
import geopandas as gpd
from src.io.load_locations import get_default_location
from src.utils.utils_logger import get_logger

logger = get_logger()


def download_osm_streets_from_location(buffer_km: float = 0.1) -> str:
    """
    Lädt OSM-Straßen um den Standard-Standort (aus TESTORTE_CSV) und speichert als GeoJSON.

    Args:
        buffer_km (float): Puffer um das Zentrum in km (ergibt Quadrat).

    Returns:
        str: Pfad zur gespeicherten GeoJSON-Datei.
    """
    lat, lon = get_default_location()
    logger.info(f"📍 Lade OSM-Straßen rund um: lat={lat}, lon={lon} (+/- {buffer_km} km)")

    # Bounding Box berechnen
    north = lat + buffer_km / 111
    south = lat - buffer_km / 111
    east = lon + buffer_km / (111 * abs(lat))
    west = lon - buffer_km / (111 * abs(lat))

    # Straßen als Graph laden
    bbox = (north, south, east, west)
    G = ox.graph_from_bbox(bbox=bbox, network_type="all")
    gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

    # Nur benannte Straßen
    gdf_named = gdf_edges[gdf_edges["name"].notnull()].copy()
    gdf_named = gdf_named.to_crs(epsg=25832)

    # Pfad definieren

    output_path: str = "data/wms_layers/streets.geojson"

    gdf_named.to_file(output_path, driver="GeoJSON")
    logger.info(f"✅ OSM-Straßen gespeichert unter: {output_path} ({len(gdf_named)} Abschnitte)")

    return output_path
