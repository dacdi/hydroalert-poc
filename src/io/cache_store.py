# src/io/cache_store.py
import csv
import os
from glob import glob
from typing import Optional, Dict
from simplekml import Kml
from src.utils.utils_logger import get_logger
from src.utils.naming import cache_path_for_latlon

logger = get_logger()

def write_depths_csv(depths: Dict[str, str], path: str) -> str:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["street", "depth_category"])
        for street, depth in depths.items():
            w.writerow([street, depth])
    logger.info("✅ CSV-Cache geschrieben: %s", path)
    return path

def _choose_street_name(names, depths: Dict[str, str]) -> str | None:
    if isinstance(names, list):
        for n in names:
            if n in depths:
                return n
        return None
    if isinstance(names, str) and names in depths:
        return names
    return None

def write_depths_kml(depths: Dict[str, str], gdf_edges_wgs, path: str) -> str:
    kml = Kml()
    for _, row in gdf_edges_wgs.iterrows():
        street = _choose_street_name(row.get("name"), depths)
        if not street:
            continue
        geom = row.geometry
        if geom.is_empty:
            continue
        midpoint = geom.interpolate(0.5, normalized=True)
        p = kml.newpoint(name=street, coords=[(midpoint.x, midpoint.y)])
        p.description = f"Tiefe: {depths[street]}"
    kml.save(path)
    logger.info("✅ KML-Cache geschrieben: %s", path)
    return path


def is_cache_available(lat: float, lon: float) -> bool:
    cache_dir = cache_path_for_latlon(lat, lon)
    return os.path.isdir(cache_dir) and bool(os.listdir(cache_dir))


def find_first_kml_in_cache(lat: float, lon: float) -> Optional[str]:
    """
    Sucht die erste flood_*.kml-Datei im Cache für (lat, lon).
    Gibt den Pfad zurück oder None.
    """
    cache_dir = cache_path_for_latlon(lat, lon)
    matches = sorted(glob(os.path.join(cache_dir, "flood_*.kml")))
    return matches[0] if matches else None
