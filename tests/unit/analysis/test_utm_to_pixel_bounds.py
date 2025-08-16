import pytest
from src.analysis.flood_overlay import utm_to_pixel

def test_bounds_and_center():
    """
    Testziel:
    ---------
    Prüft, ob utm_to_pixel für Ecken und Mittelpunkt der BBOX gültige
    Pixelkoordinaten innerhalb des Rasters zurückgibt.

    Ablauf:
    -------
    - Definiert kleine BBOX (0,0)-(100,100) und Rastergröße (10,10).
    - Prüft:
        1. Jede Ecke der BBOX landet im gültigen Pixelbereich.
        2. Mittelpunkt landet ungefähr in der Mitte des Rasters.

    Nutzen:
    -------
    - Erkennt Georeferenzierungsfehler (falsche Achsen, Off-by-One).
    - Sichert, dass Overlay-Berechnungen nicht außerhalb des Rasters landen.
    """
    bbox = (0, 0, 100, 100)  # (minx, miny, maxx, maxy)
    raster_size = (10, 10)   # (width, height)

    # Ecken + Mitte
    cases = [
        ((0, 0), (0, 9)),      # untere linke Ecke
        ((100, 100), (9, 0)),  # obere rechte Ecke
        ((0, 100), (0, 0)),    # obere linke Ecke
        ((100, 0), (9, 9)),    # untere rechte Ecke
        ((50, 50), (5, 5)),    # ungefähr Mitte
    ]

    for (x, y), (exp_px, exp_py) in cases:
        px, py = utm_to_pixel(x, y, bbox, raster_size)
        assert 0 <= px < raster_size[0]
        assert 0 <= py < raster_size[1]
        # Grober Positions-Check (Toleranz wegen Rundung)
        assert abs(px - exp_px) <= 1
        assert abs(py - exp_py) <= 1
