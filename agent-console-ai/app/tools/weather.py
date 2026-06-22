import requests
from app.tools.registry import registry

WEATHER_API_URL = "https://wttr.in/{city}?format=%C+%t+%p"

def get_weather(city: str) -> str:
    """查询指定城市当前天气。"""
    try:
        url = WEATHER_API_URL.format(city=city)
        resp = requests.get(url, timeout=10)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            return f"天气查询失败，HTTP状态码：{resp.status_code}"
        return f"{city}当前天气：{resp.text.strip()}"
    except Exception as e:
        return f"天气查询异常：{str(e)}"

registry.register("get_weather", get_weather)
