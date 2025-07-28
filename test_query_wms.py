from src.wms_query import query_flood_depth

# Beispiel: Mainz – Koordinaten
wms_url = "https://sgx.geodatenzentrum.de/wms_starkregen"
layer = "bkg:Starkregen_Stufe3"
bbox = (7.1, 50.7, 7.2, 50.8)  # Beispiel: NRW