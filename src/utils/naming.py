import os
from src.config.config import CACHE_DIR

def geo_cache_subdir_from_latlon(lat: float, lon: float) -> str:
    # 2 Dezimalstellen => konsistent mit deinem bestehenden Cache
    return f"lat{lat:.2f}_lon{lon:.2f}"

def cache_path_for_latlon(lat: float, lon: float) -> str:
    """Voller Pfad zu data/cache/lat{:.2f}_lon{:.2f}/"""
    return os.path.join(CACHE_DIR, geo_cache_subdir_from_latlon(lat, lon))
