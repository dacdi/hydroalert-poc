# src/io/forecast_client.py
from typing import Dict, Any, Tuple, List
import requests

def fetch_forecast_24h(lat: float, lon: float) -> Dict[str, Any]:
    """
    Holt 24h-Nowcast/Forecast (stundenweise) von einer API.
    Rückgabe: Roh-JSON (keine Aufbereitung).
    """
    # Beispiel Open-Meteo (falls schon genutzt; ggf. anpassen):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "precipitation",
        "forecast_days": 1,
        "timezone": "UTC",
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()
