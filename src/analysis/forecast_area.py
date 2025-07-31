from typing import List, Tuple, Optional
from time import sleep
from datetime import datetime, timedelta
import os
import csv
import pytz

from src.utils.geo_utils import generate_grid
from src.io.fetch_weather import fetch_forecast_data
from src.utils.utils_logger import get_logger

logger = get_logger(__name__)


def get_hour_labels(start: datetime, hours: int = 24) -> List[str]:
    """
    Return formatted hourly time labels for the next N hours.

    Args:
        start (datetime): Base time to start generating labels.
        hours (int, optional): Number of hours to generate. Defaults to 24.

    Returns:
        List[str]: List of time strings formatted as YYYY-MM-DDTHH:00.
    """
    return [
        (start + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00")
        for i in range(hours)
    ]


def extract_rain_series(data: dict, hour_labels: List[str]) -> List[Optional[float]]:
    """
    Extract precipitation values matching the given hour labels.

    Args:
        data (dict): API response with 'hourly' key containing 'time' and 'precipitation'.
        hour_labels (List[str]): Time labels to match against `data["hourly"]["time"]`.

    Returns:
        List[Optional[float]]: Rain values aligned with each label or None if missing.
    """
    rain_series: List[Optional[float]] = []
    for label in hour_labels:
        try:
            idx_time = data["hourly"]["time"].index(label)
            rain = data["hourly"]["precipitation"][idx_time]
        except (ValueError, KeyError, TypeError):
            logger.debug(f"No precipitation value for hour {label}.")
            rain = None
        rain_series.append(rain)
    return rain_series


def generate_forecast_grid(
    center_lat: float,
    center_lon: float,
    radius_km: int,
    step_km: int,
    hour_labels: List[str],
    delay: float
) -> List[Tuple[float, float, List[Optional[float]]]]:
    """
    Generate grid points and fetch rain forecast for each location.

    Args:
        center_lat (float): Center latitude of the grid.
        center_lon (float): Center longitude of the grid.
        radius_km (int): Radius in kilometers around center to cover.
        step_km (int): Spacing between grid points.
        hour_labels (List[str]): Time labels to extract precipitation.
        delay (float): Seconds to wait between API calls.

    Returns:
        List[Tuple[float, float, List[Optional[float]]]]: Each tuple: (lat, lon, rain_series).
    """
    grid = generate_grid(center_lat, center_lon, radius_km, step_km)
    results = []
    total_points = len(grid)
    for idx, (lat, lon) in enumerate(grid, start=1):
        logger.debug(f"Processing point {idx}/{total_points}: ({lat:.5f}, {lon:.5f})")
        data = fetch_forecast_data(lat, lon)
        if data is None:
            logger.warning(f"No data for ({lat}, {lon}); filling with None.")
            rain_series: List[Optional[float]] = [None] * len(hour_labels)
        else:
            rain_series = extract_rain_series(data, hour_labels)
        results.append((lat, lon, rain_series))
        if idx % 10 == 0 or idx == total_points:
            logger.info(f"Progress: {idx}/{total_points} points processed.")
        sleep(delay)
    return results


def write_forecast_csv(
    path: str,
    grid_data: List[Tuple[float, float, List[Optional[float]]]],
    hour_labels: List[str]
) -> None:
    """
    Write the precipitation grid data to a CSV file.

    Args:
        path (str): Output file path for the CSV.
        grid_data (List[Tuple[float, float, List[Optional[float]]]]): List of (lat, lon, rain_series).
        hour_labels (List[str]): Time labels for rainfall columns.

    Returns:
        None
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["latitude", "longitude"] + hour_labels
        writer.writerow(header)
        for lat, lon, rain_series in grid_data:
            writer.writerow([f"{lat:.5f}", f"{lon:.5f}"] + rain_series)
    logger.info(f"CSV written to: {path}")


def save_full_rain_forecast_grid(
    output_path: str = "output/rain_grid_24h.csv",
    center_lat: float = 49.35,
    center_lon: float = 8.15,
    radius_km: int = 10,
    step_km: int = 5,
    delay: float = 0.2
) -> None:
    """
    Orchestrate generation of rain forecast grid and CSV export.

    This function generates a raster of geographic points, fetches a
    24-hour rain forecast for each point, and writes the results to a CSV.

    Args:
        output_path (str, optional): CSV file to save results. Defaults to "output/rain_grid_24h.csv".
        center_lat (float, optional): Center latitude for grid generation.
        center_lon (float, optional): Center longitude for grid generation.
        radius_km (int, optional): Radius around center to include points.
        step_km (int, optional): Distance between grid points.
        delay (float, optional): Time to sleep between API requests.

    Returns:
        None
    """
    logger.info(
        f"Starting grid forecast: center=({center_lat}, {center_lon}), "
        f"radius={radius_km} km, step={step_km} km"
    )
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    hour_labels = get_hour_labels(now, 24)
    grid_data = generate_forecast_grid(center_lat, center_lon, radius_km, step_km, hour_labels, delay)
    write_forecast_csv(output_path, grid_data, hour_labels)
