import geopandas as gpd
import json
from tests.conftest import make_mini_tile
from src.analysis.flood_overlay import detect_street_depths

def test_synthetic_one_street_one_depth(tmp_path):
    """
    Testziel:
    ---------
    Prüft, ob bei einer synthetischen Testkachel genau eine Straße erkannt
    und mit der korrekten Tiefenklasse verknüpft wird.

    Ablauf:
    -------
    1. Erzeugt Mini-Kachel (10x10 px) mit Wasser in definierter Farbe.
    2. Erstellt einfache Straße, die durchs Wasser verläuft.
    3. Führt detect_street_depths aus.
    4. Erwartung: Genau eine Straße, Tiefe enthält '10'.

    Nutzen:
    -------
    - Isoliertest ohne Internet oder echte WMS-Daten.
    - Deckt Farb-Mapping, Geometrie-Mapping und Sampling-Abstand ab.
    """

    base = make_mini_tile(tmp_path)
    streets = gpd.read_file(base / "streets.gpkg", layer="streets")

    # meta.json auslesen
    meta = json.loads((base / "meta.json").read_text())
    bbox = (
        meta["bbox_utm"]["minx"],
        meta["bbox_utm"]["miny"],
        meta["bbox_utm"]["maxx"],
        meta["bbox_utm"]["maxy"]
    )
    raster_size = (
        meta["raster_size"]["width"],
        meta["raster_size"]["height"]
    )

    result = detect_street_depths(
        streets,
        png_path=str(base / "Wassertiefe_SRI10_1h.png"),
        bbox_utm=bbox,
        raster_size=raster_size,
        sample_distance_m=5.0,
    )

    assert len(result) == 1, "Es sollte genau eine Straße gefunden werden."
    depth = list(result.values())[0]
    assert "10" in depth, f"Erwartete Tiefe ~10 cm, bekam: {depth}"
