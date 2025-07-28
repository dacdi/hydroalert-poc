import requests
from datetime import datetime
import pytz
from src.utils_logger import get_logger

logger = get_logger(__name__)

def log_precipitation_series(data):
    times = data.get("hourly", {}).get("time", [])
    values = data.get("hourly", {}).get("precipitation", [])
    logger.debug("🔄 Vorhersageverlauf:")
    for t, v in zip(times, values):
        logger.debug(f"  {t} → {v} mm/h")

def get_current_precipitation(data):
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

def get_rain_forecast(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=precipitation"
        f"&forecast_days=1&timezone=Europe/Berlin"
    )

    logger.debug(f"[Request] URL: {url}")
    try:
        response = requests.get(url)
        logger.debug(f"[Response] Status Code: {response.status_code}")

        if response.status_code != 200:
            logger.warning(f"Non-200 response for ({lat}, {lon}): {response.status_code}")
            return None

        data = response.json()
        logger.debug(f"[Data] Keys: {list(data.keys())}")
        logger.debug(f"[Data] Hourly keys: {list(data.get('hourly', {}).keys())}")

        log_precipitation_series(data)
        return get_current_precipitation(data)

    except Exception as e:
        logger.exception(f"❌ Exception while fetching rain for ({lat}, {lon})")
        return None
