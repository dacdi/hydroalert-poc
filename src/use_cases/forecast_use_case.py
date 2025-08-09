# src/use_cases/forecast_use_case.py
from argparse import Namespace
from src.services.forecast_area import save_forecast_grid_to_cache

def run_forecast_use_case(args: Namespace) -> None:
    save_forecast_grid_to_cache(args.lat, args.lon)
