# src/analysis/forecast_area.py

import os
import csv
import pytz
from time import sleep
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

from src.utils.geo_utils import generate_grid
from src.io.fetch_weather import fetch_forecast_data
from src.utils.utils_logger import get_logger

logger = get_logger()


class RainGridForecaster:
    def __init__(
        self,
        center_lat: float = 49.35,
        center_lon: float = 8.15,
        radius_km: int = 10,
        step_km: int = 2,
        delay: float = 0.0
    ):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_km = radius_km
        self.step_km = step_km
        self.delay = delay

    def get_hour_labels(self, start: datetime, hours: int = 24) -> List[str]:
        return [
            (start + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00")
            for i in range(hours)
        ]

    def extract_rain_series(self, data: dict, hour_labels: List[str]) -> List[Optional[float]]:
        rain_series: List[Optional[float]] = []
        for label in hour_labels:
            try:
                idx = data["hourly"]["time"].index(label)
                rain = data["hourly"]["precipitation"][idx]
            except (ValueError, KeyError, TypeError):
                logger.debug(f"No precipitation value for hour {label}.")
                rain = None
            rain_series.append(rain)
        return rain_series

    def generate_forecast_grid(
        self, hour_labels: List[str]
    ) -> List[Tuple[float, float, List[Optional[float]]]]:
        grid = generate_grid(self.center_lat, self.center_lon, self.radius_km, self.step_km)
        results = []
        total = len(grid)
        for idx, (lat, lon) in enumerate(grid, start=1):
            logger.debug(f"Processing point {idx}/{total}: ({lat:.5f}, {lon:.5f})")
            data = fetch_forecast_data(lat, lon)
            if data is None:
                logger.warning(f"No data for ({lat}, {lon}); filling with None.")
                rain_series = [None] * len(hour_labels)
            else:
                rain_series = self.extract_rain_series(data, hour_labels)
            results.append((lat, lon, rain_series))
            if idx % 10 == 0 or idx == total:
                logger.info(f"Progress: {idx}/{total} points processed.")
            sleep(self.delay)
        return results

    def write_forecast_csv(
        self, path: str, grid_data: List[Tuple[float, float, List[Optional[float]]]], hour_labels: List[str]
    ) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["latitude", "longitude"] + hour_labels
            writer.writerow(header)
            for lat, lon, rain_series in grid_data:
                writer.writerow([f"{lat:.5f}", f"{lon:.5f}"] + rain_series)
        logger.info(f"CSV written to: {path}")

    def save_full_rain_forecast_grid(self, output_path: str = "output/rain_grid_24h.csv") -> None:
        logger.info(
            f"Starting grid forecast: center=({self.center_lat}, {self.center_lon}), "
            f"radius={self.radius_km} km, step={self.step_km} km"
        )
        now = datetime.now(pytz.timezone("Europe/Berlin"))
        hour_labels = self.get_hour_labels(now, 24)
        grid_data = self.generate_forecast_grid(hour_labels)
        self.write_forecast_csv(output_path, grid_data, hour_labels)
