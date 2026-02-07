from datetime import datetime
from typing import Any

import requests

from schema.tool_schemas import WeatherInfo

WEATHER_API_KEY = '54a1a50544674a31b6934515260502'  # WeatherAPI的Key
WEATHER_API_URL = "https://api.weatherapi.com/v1/current.json"

class WeatherUtils:

    @staticmethod
    def get_weather_by_city(city: Any) -> WeatherInfo:
        print('查询天气的城市名或经纬度：', city)
        params = {
            "key": WEATHER_API_KEY,
            "q": city,
            "lang": "zh"  # 返回中文结果，适配国内使用
        }
        try:
            response = requests.get(
                WEATHER_API_URL,
                params=params,
                timeout=10,
                proxies={"http": None, "https": None}  # 核心：禁用所有代理
            )
            response.raise_for_status()  # 抛出HTTP错误
            data = response.json()
            # print(data)
            return WeatherInfo(
                city=data["location"]["name"],  # 城市名
                temperature=data["current"]["temp_c"],  # 温度（℃）
                feels_like=data["current"]["feelslike_c"],  # 体感温度
                weather=data["current"]["condition"]["text"],  # 天气状况
                humidity=data["current"]["humidity"],  # 湿度（%）
                update_time=data["current"]["last_updated"],  # 更新时间
            )
        except ConnectionError as e:
            print(f"网络连接失败: {e}")
            raise RuntimeError("天气服务暂时无法访问，请稍后再试") from e
        except Exception as e:
            print(f"请求天气 API 出错: {e}")
            raise



# WeatherUtils.get_weather_by_city(f'39.9072, 116.357')
# WeatherUtils.get_weather_by_city(f'南京')