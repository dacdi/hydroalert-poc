# src/utils/naming.py
import os
from src.config.config import CACHE_DIR

def geo_cache_subdir_from_latlon(lat: float, lon: float) -> str:
    """Ordnername im Cache für eine Geo-Position (2 Dezimalstellen)."""
    return f"lat{lat:.2f}_lon{lon:.2f}"

def cache_path_for_latlon(lat: float, lon: float) -> str:
    """Voller Pfad: data/cache/latXX.XX_lonYY.YY/"""
    return os.path.join(CACHE_DIR, geo_cache_subdir_from_latlon(lat, lon))

def rain_grid_csv_name(lat: float, lon: float) -> str:
    """Dateiname: rain_grid_latXX.XX_lonYY.YY.csv (2 Nachkommastellen)."""
    return f"rain_grid_lat{lat:.2f}_lon{lon:.2f}.csv"
