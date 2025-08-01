from src.analysis.riskmap_interpreter import get_flood_depth

def test_get_flood_depth():
    assert get_flood_depth(5) == 0.0
    assert get_flood_depth(10) == 0.1
    assert get_flood_depth(20) == 0.3
    assert get_flood_depth(30) == 0.5
    assert get_flood_depth(50) == 0.7
