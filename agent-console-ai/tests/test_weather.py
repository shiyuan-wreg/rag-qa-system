from app.tools.weather import get_weather

def test_get_weather():
    result = get_weather("北京")
    assert "北京" in result
