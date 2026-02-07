from langchain_core.tools import tool

from schema.tool_schemas import WeatherInfo
from utils.ip_utils import IpUtils
from utils.weatherapi_utils import WeatherUtils


@tool
def get_weather_by_city(city: str) -> WeatherInfo:
    """
    根据指定城市名称获取天气信息
    """
    return WeatherUtils.get_weather_by_city(city)

@tool
def get_weather_by_ip() -> str:
    """
    根据ip先获取经纬度元组结构后转成字符串返回，作为get_weather_by_city(经纬度字符串)传参获取天气信息
    例如返回的是'123.12, 123.13'，则调get_weather_by_city(123.12, 123.13)获取天气信息
    注意：此经纬度是mock，请获取真实值传递。
    """
    ip = IpUtils.get_location_ip()
    return f"{ip[0]},{ip[1]}" if ip else None
