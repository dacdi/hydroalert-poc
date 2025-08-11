import numpy as np
from PIL import Image
img = Image.open("data/cache/lat50.00_lon8.10/Wassertiefe_SRI7_1h.png").convert("RGB")
colors = np.unique(np.array(img).reshape(-1,3), axis=0)
print(colors)
