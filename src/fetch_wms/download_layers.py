import os
import requests

# Zielverzeichnis relativ zum Projekt-Hauptverzeichnis
output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "wms_layers")
output_dir = os.path.abspath(output_dir)
os.makedirs(output_dir, exist_ok=True)
print(f"📂 Zielverzeichnis: {output_dir}\n")

# Bounding Box für ca. 20x20 km² – Region Neustadt (EPSG:25832)
bbox = "432000,5461000,452000,5481000"
width, height = 2000, 2000

# Liste der Layer
layers = {
    "Visdom_SRI07_1h_WaterDepth": "Wassertiefe_SRI7_1h",
    "Visdom_SRI10_1h_WaterDepth": "Wassertiefe_SRI10_1h",
    "Visdom_SRI10_4h_WaterDepth": "Wassertiefe_SRI10_4h",
    "Visdom_SRI07_1h_FlowVelocity": "Fließgeschw_SRI7_1h",
    "Visdom_SRI10_1h_FlowVelocity": "Fließgeschw_SRI10_1h",
    "Visdom_SRI10_4h_FlowVelocity": "Fließgeschw_SRI10_4h",
    "Visdom_Schummerung": "Schummerung",
    "Visdom_Sinkpolygons": "Sinkpolygone"
}

# WMS-Basiskonfiguration
url = "https://geodienste-wasser.rlp-umwelt.de/geoserver/Sturzflut/wms"

for layer_name, short_name in layers.items():
    print(f"⬇️ Lade Layer: {layer_name}")

    params = {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetMap",
        "layers": layer_name,
        "bbox": bbox,
        "width": width,
        "height": height,
        "crs": "EPSG:25832",
        "format": "image/png"
    }

    try:
        response = requests.get(url, params=params)
        print(f"🌐 Request-URL: {response.url}")
        print(f"📦 Antwort-Code: {response.status_code}")
        print(f"📦 Content-Type: {response.headers.get('Content-Type', 'unbekannt')}")
        print(f"📏 Bildgröße (Bytes): {len(response.content)}")

        if response.status_code == 200 and response.headers.get("Content-Type") == "image/png":
            filename = os.path.join(output_dir, f"{short_name}.png")
            with open(filename, "wb") as f:
                f.write(response.content)
            if os.path.isfile(filename):
                print(f"✅ Gespeichert: {filename}\n")
            else:
                print(f"⚠️ Datei wurde nicht geschrieben: {filename}\n")
        else:
            print(f"❌ Fehlerhafte Antwort oder kein PNG – Layer: {layer_name}\n")

    except Exception as e:
        print(f"❌ Ausnahme beim Laden von {layer_name}: {e}\n")
