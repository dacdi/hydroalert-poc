from unittest.mock import patch
from src.analysis.forecast_area import get_rain_area


@patch("src.forecast_area.get_rain_forecast")
def test_rain_area_with_mock(mock_get_rain_forecast):
    # Simuliere: 40 % der Gitterpunkte haben "Starkregen" ≥ 5 mm/h
    def mock_forecast(lat, lon):
        # Jede 3. Koordinate hat Regen ≥ 5
        return 7.0 if int(lat * 1000) % 3 == 0 else 2.0

    mock_get_rain_forecast.side_effect = mock_forecast

    area_km2, hits, total = get_rain_area(min_rain_threshold=5.0, delay=0.0)

    assert total > 0
    assert hits > 0
    assert hits < total
    assert area_km2 == hits * 4  # bei 2×2 km Gitterzellen

    print(f"✅ get_rain_area(): {hits}/{total} Treffer, Fläche: {area_km2} km²")
