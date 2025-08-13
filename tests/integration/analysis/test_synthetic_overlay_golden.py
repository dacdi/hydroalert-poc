import json
import pandas as pd
import pytest
import geopandas as gpd
from pathlib import Path
from src.analysis.flood_overlay import detect_street_depths
from tests.conftest import make_mini_tile

GOLDEN_PATH = Path("tests/golden/synthetic_result.csv")

@pytest.mark.integration
def test_synthetic_overlay_golden(tmp_path, request):
    """
    Testziel:
    ---------
    Vergleicht die Ausgabe des synthetischen Mini-Tiles mit einer
    gespeicherten Golden-Version. Erkennt ungewollte Änderungen
    am Overlay-Algorithmus sofort.

    Ablauf:
    -------
    1. Mini-Tile erzeugen.
    2. detect_street_depths ausführen.
    3. Ergebnis als DataFrame speichern.
    4. Mit gespeicherter Golden-Datei vergleichen.
       - Falls --update-golden gesetzt ist → Golden-Datei überschreiben.

    Nutzen:
    -------
    - Regressionstest für Overlay-Logik.
    - Stabil auch bei Refactorings, solange Verhalten gleich bleibt.
    """
    # Testdaten erzeugen
    base = make_mini_tile(tmp_path)
    streets = gpd.read_file(base / "streets.gpkg", layer="streets")
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

    df = pd.DataFrame(list(result.items()), columns=["name", "depth_class"])

    # Optionales Golden-Update
    if request.config.getoption("--update-golden"):
        GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(GOLDEN_PATH, index=False)
        pytest.skip("Golden file updated.")

    # Vergleich mit Golden File
    assert GOLDEN_PATH.exists(), "Golden file fehlt. Mit --update-golden anlegen."
    df_expected = pd.read_csv(GOLDEN_PATH)

    pd.testing.assert_frame_equal(df.sort_index(axis=1), df_expected.sort_index(axis=1))
