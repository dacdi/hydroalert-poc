from owslib.wms import WebMapService

url = "https://sgx.geodatenzentrum.de/wms_starkregen"
wms = WebMapService(url, version="1.3.0")

print("\nVerfügbare Layer:")
for layer in wms.contents:
    print("-", layer)
