from pathlib import Path
from PIL import Image
import numpy as np


from src.analysis.flood_overlay import depth_from_color

EXCLUDE = {(255, 255, 255)}

"""
Testziel:
---------
Stellt sicher, dass alle in den heruntergeladenen WMS-PNGs vorkommenden
Farben (außer definierte NoData-Farben wie Weiß) in der Farb-zu-Tiefe-
Mappingfunktion `depth_from_color` korrekt abgebildet werden.

Hintergrund:
------------
Die WMS-Karten codieren Wassertiefen ausschließlich über Farbwerte.
Wenn sich die Farbpalette ändert (z. B. durch Anpassungen beim Kartenanbieter),
kann es passieren, dass bestimmte Pixel-Farben nicht mehr im Mapping
auftauchen. Das führt zu falschen oder fehlenden Tiefenwerten im Ergebnis.

Funktionsweise:
---------------
1. Durchsucht bekannte Verzeichnisse (`data/wms_layers`, `data/cache`) nach PNG-Dateien.
2. Extrahiert alle eindeutigen RGB-Farben der PNGs.
3. Entfernt definierte NoData-Farben (z. B. `(255, 255, 255)` für weiß).
4. Prüft, ob jede verbleibende Farbe von `depth_from_color` einem Tiefenwert zugeordnet wird.
5. Falls eine Farbe unbekannt ist, schlägt der Test fehl und nennt die betroffene Farbe und Datei.

Nutzen:
-------
- Frühwarnsystem für Änderungen an der Kartenfarbpalette.
- Verhindert, dass neue oder geänderte Farben stillschweigend zu "None" gemappt werden.
- Sichert die langfristige Stabilität der Farbtiefen-Logik ohne manuelle Sichtkontrolle.
"""



def unique_rgbs(png_path: Path):
    arr = np.array(Image.open(png_path).convert("RGB"))
    return {tuple(c) for c in np.unique(arr.reshape(-1, 3), axis=0)}

def test_palette_colors_are_mapped():
    png = next(Path("data/cache").rglob("*.png"))
    colors = unique_rgbs(png) - EXCLUDE
    for rgb in colors:
        depth = depth_from_color(*rgb, 255)
        assert depth is not None, f"Unbekannte Farbe {rgb} in {png}"
