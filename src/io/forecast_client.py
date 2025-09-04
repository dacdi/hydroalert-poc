#src/io/forecast_client.py

from __future__ import annotations
from typing import Dict, Any
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config.config import FORECAST_API_URL, FORECAST_HTTP_TIMEOUT_S
from src.utils.utils_logger import get_logger

logger = get_logger()

# Gemeinsame Session mit Retries/Backoff
_session = requests.Session()
_retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(["GET"]),
    raise_on_status=False,
)
_session.mount("https://", HTTPAdapter(max_retries=_retries))
_session.headers.update({"User-Agent": "HydroAlert/forecast-client"})


def _validate_hourly_payload(data: Dict[str, Any]) -> None:
    if "hourly" not in data or not isinstance(data["hourly"], dict):
        raise ValueError("Antwort enthält kein gültiges 'hourly'-Objekt.")
    hourly = data["hourly"]
    if "time" not in hourly or "precipitation" not in hourly:
        raise ValueError("'hourly.time' oder 'hourly.precipitation' fehlt.")
    if not isinstance(hourly["time"], list) or not isinstance(hourly["precipitation"], list):
        raise ValueError("'hourly.time'/'hourly.precipitation' sind nicht vom Typ Liste.")


def fetch_forecast_24h(lat: float, lon: float) -> Dict[str, Any]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "precipitation",
        "forecast_days": 1,
        "timezone": "UTC",
    }

    logger.debug("GET %s params=%s timeout=%ss", FORECAST_API_URL, params, FORECAST_HTTP_TIMEOUT_S)

    try:
        resp = _session.get(FORECAST_API_URL, params=params, timeout=FORECAST_HTTP_TIMEOUT_S)
        logger.debug(
            "Response status=%s (reason=%s) url=%s",
            resp.status_code, getattr(resp, "reason", "?"), resp.url
        )

        if resp.status_code == 429:
            logger.debug("429 Too Many Requests – kurzer Backoff 1.0s")
            time.sleep(1.0)

        resp.raise_for_status()
        data = resp.json()

        _validate_hourly_payload(data)
        times = data["hourly"]["time"]
        precip = data["hourly"]["precipitation"]

        logger.debug(
            "OK hourly.time=%d, hourly.precipitation=%d | first=%s / %s | last=%s / %s",
            len(times), len(precip),
            times[0] if times else "—", precip[0] if precip else "—",
            times[-1] if times else "—", precip[-1] if precip else "—"
        )

        return data

    except requests.Timeout as e:
        logger.exception("Timeout nach %ss bei %s", FORECAST_HTTP_TIMEOUT_S, FORECAST_API_URL)
        raise TimeoutError(f"Timeout nach {FORECAST_HTTP_TIMEOUT_S}s für {FORECAST_API_URL}") from e

    except requests.RequestException as e:
        logger.exception("HTTP-/Netzfehler: %s", e)
        raise RuntimeError(f"HTTP-/Netzfehler: {e}") from e

    except ValueError as e:
        logger.exception("Ungültige Antwortstruktur: %s", e)
        raise
