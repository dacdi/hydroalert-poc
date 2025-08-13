import json
from pathlib import Path
from PIL import Image, ImageDraw
import geopandas as gpd
from shapely.geometry import LineString

def make_mini_tile(root: Path, water_rgb=(47, 117, 181)):
    """
    Erzeugt einen vollständigen Mini-Testdatensatz bestehend aus:
    - meta.json mit definierter BBOX und Rastergröße
    - PNG-Layer (10x10 px) mit Wasserfläche in definierter Farbe
    - GPKG-Datei mit einer Straße, die das Wasser kreuzt

    Args:
        root: Zielverzeichnis für den Mini-Datensatz
        water_rgb: RGB-Tupel für die Wasserfarbe
    """
    root.mkdir(parents=True, exist_ok=True)

    # 1) Meta-Infos
    meta = {
        "bbox_utm": {"minx": 0, "miny": 0, "maxx": 100, "maxy": 100},
        "raster_size": {"width": 10, "height": 10},
        "crs": "EPSG:25832",
        "layer_name": "Wassertiefe_SRI10_1h"
    }
    (root / "meta.json").write_text(json.dumps(meta, indent=2))

    # 2) PNG mit Wasserfläche
    im = Image.new("RGBA", (10, 10), (255, 255, 255, 255))
    draw = ImageDraw.Draw(im)
    draw.rectangle((3, 3, 6, 6), fill=water_rgb + (255,))
    im.save(root / "Wassertiefe_SRI10_1h.png")

    # 3) Teststraße (quert Wasserfläche)
    line = LineString([(40, 50), (60, 50)])  # UTM-Koordinaten
    gdf = gpd.GeoDataFrame({"name": ["Teststraße"]}, geometry=[line], crs="EPSG:25832")
    gdf.to_file(root / "streets.gpkg", layer="streets", driver="GPKG")

    return root

def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        help="Update golden files with current test output."
    )
