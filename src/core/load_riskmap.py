from src.utils_logger import get_logger

logger = get_logger(__name__)

def get_flood_depth(rain_mm_per_hour):
    logger.debug(f"Calculating flood depth for {rain_mm_per_hour} mm/h")
    if rain_mm_per_hour >= 40:
        return 0.7
    elif rain_mm_per_hour >= 30:
        return 0.5
    elif rain_mm_per_hour >= 20:
        return 0.3
    elif rain_mm_per_hour >= 10:
        return 0.1
    else:
        return 0.0
