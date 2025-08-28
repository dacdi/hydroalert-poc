# src/io/load_locations.py

import pandas as pd
from typing import Tuple

from src.config.config import TESTORTE_CSV
from src.utils.utils_logger import get_logger

logger = get_logger()

# ToDo: Noch notwenidg?

def get_default_location() -> Tuple[float, float]:
    """
    Load the first test location (lat, lon) from the test location CSV.

    Returns:
        Tuple[float, float]: Latitude and longitude from the first row.
    """
    df = pd.read_csv(TESTORTE_CSV)
    if df.empty or "lat" not in df or "lon" not in df:
        raise ValueError(f"No valid test locations found in {TESTORTE_CSV}")
    first = df.iloc[0]
    return first["lat"], first["lon"]
