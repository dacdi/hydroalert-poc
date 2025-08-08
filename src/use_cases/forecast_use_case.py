from argparse import Namespace
from logging import Logger
import csv
import os
import sys

from osmnx import graph_from_point, graph_to_gdfs

from src.analysis.forecast_area import RainGridForecaster
from src.config.config import CACHE_DIR, WMS_LAYERS_DIR
from src.io.flood_cache import compute_depths, write_depths_csv, write_depths_kml
from src.utils.utils_logger import get_logger

logger: Logger = get_logger()
DEFAULT_LAYER = os.path.join(WMS_LAYERS_DIR, "Wassertiefe_SRI10_1h.png")


def save_forecast_grid_to_cache(lat: float, lon: float) -> None:
    """Save the 24h forecast grid for the location to the cache directory."""
    cache_dir = os.path.join(CACHE_DIR, f"lat{lat}_lon{lon}")
    output_path = os.path.join(cache_dir, "forecast_24h.csv")
    forecaster = RainGridForecaster(center_lat=lat, center_lon=lon)
    forecaster.save_full_rain_forecast_grid(output_path=output_path)
    logger.info(f"✅ Vorhersage gespeichert: {output_path}")


def save_street_depths_to_cache(lat: float, lon: float) -> None:
    """Save detected street depths for the location to the cache directory."""
    cache_dir = os.path.join(CACHE_DIR, f"lat{lat}_lon{lon}")
    csv_path = os.path.join(cache_dir, "street_depths.csv")

    logger.info("🌧 Analysiere Straßentiefen …")
    G = graph_from_point((lat, lon), dist=200, network_type="drive", simplify=True)
    gdf_edges = graph_to_gdfs(G, nodes=False, edges=True)
    gdf_utm = gdf_edges.to_crs(epsg=25832)

    depths = compute_depths(gdf_utm, DEFAULT_LAYER, sample_distance_m=5.0)
    write_depths_csv(depths, csv_path)


def build_kml_for_location(lat: float, lon: float) -> None:
    """Build a KML overlay for the location and store it in the cache."""
    cache_dir = os.path.join(CACHE_DIR, f"lat{lat}_lon{lon}")
    csv_path = os.path.join(cache_dir, "street_depths.csv")
    kml_path = os.path.join(cache_dir, "flutkarte.kml")

    if not os.path.isfile(csv_path):
        logger.warning("⚠️ Keine Straßentiefen gefunden, KML wird übersprungen")
        return

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        depths = {row["street"]: row["depth"] for row in reader}

    G = graph_from_point((lat, lon), dist=200, network_type="drive", simplify=True)
    gdf_edges = graph_to_gdfs(G, nodes=False, edges=True)
    gdf_wgs = gdf_edges.to_crs(epsg=4326)

    write_depths_kml(depths, gdf_wgs, kml_path)


def run_forecast_use_case(args: Namespace) -> None:
    """Generate forecast and KML for given coordinates."""
    if args.lat is None or args.lon is None:
        logger.error(
            "❌ Bitte gib sowohl --lat als auch --lon an, z. B. --lat 49.45 --lon 8.18"
        )
        sys.exit(1)

    lat = round(args.lat, 4)
    lon = round(args.lon, 4)
    logger.info(f"📍 Standort: lat={lat}, lon={lon}")

    prepare_location_if_needed(lat, lon)
    logger.info("✅ Standortdaten vorbereitet.")


def prepare_location_if_needed(lat: float, lon: float) -> None:
    """Ensure forecast and KML data for the location exist in the cache."""
    cache_dir = os.path.join(CACHE_DIR, f"lat{lat}_lon{lon}")
    forecast_path = os.path.join(cache_dir, "forecast_24h.csv")
    kml_path = os.path.join(cache_dir, "flutkarte.kml")

    if os.path.isfile(forecast_path) and os.path.isfile(kml_path):
        logger.info("✅ Daten bereits vorhanden")
        return

    logger.info("🔄 Erzeuge neue Standortdaten …")
    os.makedirs(cache_dir, exist_ok=True)
    save_forecast_grid_to_cache(lat, lon)
    save_street_depths_to_cache(lat, lon)
    build_kml_for_location(lat, lon)
