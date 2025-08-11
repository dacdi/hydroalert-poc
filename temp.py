from PIL import Image
img = Image.open("data/cache/lat50.00_lon8.10/Wassertiefe_SRI7_1h.png").convert("RGB")
colors = set(img.getdata())
print(len(colors), list(colors)[:20])  # Anzahl und erste 20 Farben
