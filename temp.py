from osmnx import graph_from_point, graph_to_gdfs
from src.analysis.flood_overlay import detect_street_depths

# 1) Straßen laden
G = graph_from_point((49.35, 8.14), dist=400, network_type="drive", simplify=True)
gdf_edges = graph_to_gdfs(G, nodes=False, edges=True).to_crs(epsg=25832)

# 2) Tiefen-Detektion
depths = detect_street_depths(
    gdf_edges,
    png_path="data/wms_layers/Wassertiefe_SRI7_1h.png",
    bbox_utm=(432000, 5461000, 452000, 5481000),
    raster_size=(2000, 2000),
    sample_distance_m=5.0
)

for street, depth in depths.items():
    print(f"{street}: {depth}")
