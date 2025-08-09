import os
from src.utils.utils_logger import get_logger

logger = get_logger()

def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)

def save_png(content: bytes, output_dir: str, short_name: str) -> str:
    filename = os.path.join(output_dir, f"{short_name}.png")
    with open(filename, "wb") as f:
        f.write(content)
    logger.info("✅ Saved: %s", filename)
    return filename
