# src/services/overlay_service_service.py
from src.analysis.flood_overlay import detect_street_depths
from src.io.file_io import read_raster, read_streets, write_csv

def build_and_save_overlay(raster_path: str, streets_path: str, out_csv: str) -> str:
    raster = read_raster(raster_path)
    streets = read_streets(streets_path)
    result = detect_street_depths(raster, streets)
    write_csv(out_csv, result)
    return out_csv
