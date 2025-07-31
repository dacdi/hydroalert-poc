from src.utils.geo_utils import generate_grid


def test_generate_grid_default():
    # Standardwerte: Radius 10 km, Schrittweite 2 km
    grid = generate_grid(49.35, 8.15)

    # Erwartet: Gitter von -10 bis +10 km in 2er-Schritten → 11 × 11 Punkte
    assert isinstance(grid, list)
    assert len(grid) == 121
    assert all(isinstance(coord, tuple) and len(coord) == 2 for coord in grid)


def test_generate_grid_custom_params():
    grid = generate_grid(49.0, 8.0, radius_km=4, step_km=2)
    # Gitter: -4, -2, 0, 2, 4 → 5 × 5 = 25 Punkte
    assert len(grid) == 25


def test_grid_coordinates_are_distinct():
    grid = generate_grid(49.35, 8.15)
    coord_set = set(grid)
    assert len(coord_set) == len(grid)  # keine Duplikate
