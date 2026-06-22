from app.tools.calculator import calculate

def test_calculate_add():
    assert "5" in calculate("2 + 3")

def test_calculate_invalid():
    assert "非法字符" in calculate("__import__('os').system('ls')")
