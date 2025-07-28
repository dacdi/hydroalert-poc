import requests

url = "https://geodienste-wasser.rlp-umwelt.de/geoserver/Sturzflut/wms"
params = {
    "service": "WMS",
    "version": "1.3.0",
    "request": "GetMap",
    "layers": "Visdom_SRI10_1h_WaterDepth",
    "bbox": "441000,5470000,443000,5472000",  # Beispiel für Neustadt, EPSG:25832
    "width": 800,
    "height": 800,
    "crs": "EPSG:25832",
    "format": "image/png"
}

r = requests.get(url, params=params)
with open("waterdepth_test.png", "wb") as f:
    f.write(r.content)
