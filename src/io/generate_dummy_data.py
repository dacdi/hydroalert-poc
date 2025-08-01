import csv
import os
from typing import List
from src.utils.utils_logger import get_logger

logger = get_logger(__name__)


def generate_dummy_rain_data(
        output_path: str = "output/rain_grid_24h.csv",
        variant: str = "SRI7"
) -> None:
    """Generate dummy precipitation data for testing flood stage evaluation.

    Args:
        output_path (str): Path to the target CSV file to overwrite.
        variant (str): Either 'SRI7' or 'SRI10', defines the rain severity.

    Returns:
        None
    """
    if not os.path.exists(output_path):
        logger.error(f"❌ File not found: {output_path}")
        return

    logger.info(f"🧪 Overwriting CSV with dummy data: variant={variant}")

    with open(output_path, "r", newline="") as f:
        reader = list(csv.reader(f))
        header, rows = reader[0], reader[1:]

    # Determine dummy value based on variant
    dummy_value = 8.0 if variant == "SRI7" else 16.0  # mm/h
#ToDo: auch die Möglichkeit für keinen Regen und die anderen Regenklassen einbauen
    # Replace rain values (columns after lat/lon)
    updated_rows: List[List[str]] = []
    for row in rows:
        lat, lon = row[:2]
        new_row = [lat, lon] + [str(dummy_value)] * (len(row) - 2)
        updated_rows.append(new_row)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(updated_rows)

    logger.info(f"✅ Dummy data written to: {output_path}")
