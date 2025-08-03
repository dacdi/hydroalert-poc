import requests
from datetime import datetime, timedelta
import pytz
from src.utils.utils_logger import get_logger

logger = get_logger()


def _dummy_forecast(lat: float, lon: float) -> dict:
    """Generates a 24h forecast with zero precipitation as fallback."""
    now = datetime.now(pytz.timezone("Europe/Berlin")).replace(minute=0, second=0, microsecond=0)
    times = [(now + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00") for i in range(24)]
    return {"hourly": {"time": times, "precipitation": [0.0] * 24}}


def fetch_forecast_data(lat: float, lon: float) -> dict:
    """
    Ruft stündliche Niederschlagsvorhersage für 24 Stunden von Open-Meteo ab.

    Args:
        lat (float): Breitengrad
        lon (float): Längengrad

    Returns:
        dict: Wetterdaten oder Dummy-Daten bei Fehler
    """
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&hourly=precipitation"
        "&forecast_days=2"
        "&timezone=Europe/Berlin"
    )
    logger.debug(f"[Request] URL: {url}")

    try:
        response = requests.get(url)
        logger.debug(f"[Response] Status Code: {response.status_code}")

        if response.status_code != 200:
            logger.warning(
                f"⚠️ Anfrage fehlgeschlagen für ({lat}, {lon}): {response.status_code}"
            )
            return _dummy_forecast(lat, lon)

        return response.json()

    except Exception:
        logger.exception(f"❌ Fehler bei API-Anfrage für ({lat}, {lon})")
        return _dummy_forecast(lat, lon)


def log_precipitation_series(data: dict) -> None:
    """
    Gibt alle stündlichen Regenwerte im Log aus.

    Args:
        data (dict): Wetterdaten
    """
    times = data.get("hourly", {}).get("time", [])
    values = data.get("hourly", {}).get("precipitation", [])

    logger.debug("🔄 Vorhersageverlauf:")
    for t, v in zip(times, values):
        logger.debug(f"  {t} → {v} mm/h")


def get_current_precipitation(data: dict) -> float | None:
    """
    Gibt den Niederschlagswert zur aktuellen Stunde zurück.

    Args:
        data (dict): Wetterdaten

    Returns:
        float | None: Regenwert in mm/h oder None, wenn nicht vorhanden
    """
    times = data.get("hourly", {}).get("time", [])
    values = data.get("hourly", {}).get("precipitation", [])

    now = datetime.now(pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%dT%H:00")
    logger.debug(f"🔍 Jetztzeit: {now}")

    try:
        index = times.index(now)
        rain = values[index]
        logger.info(f"☔ Regen zur aktuellen Zeit ({now}): {rain} mm/h")
        return rain
    except ValueError:
        logger.warning(f"⚠️ Kein Eintrag für aktuelle Zeit ({now}) in API-Daten")
        return None


def get_rain_forecast(lat: float, lon: float) -> float | None:
    """
    Kombinierte Funktion: Holt Vorhersage und gibt aktuellen Regenwert zurück.

    Args:
        lat (float): Breitengrad
        lon (float): Längengrad

    Returns:
        float | None: Regenwert zur aktuellen Stunde oder None
    """
    data = fetch_forecast_data(lat, lon)
    if data is None:
        return None

    log_precipitation_series(data)
    return get_current_precipitation(data)
