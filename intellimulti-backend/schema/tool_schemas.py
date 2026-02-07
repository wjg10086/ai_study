from pydantic import Field, BaseModel


class WeatherInfo(BaseModel):
    """获取天气信息最终返回的结构体"""
    city: str = Field(description="城市名称，如果返回的是英文，则转成对应中文返回")
    temperature: float = Field(description="温度（℃）")
    feels_like: float = Field(description="体感温度")
    weather: str = Field(description="天气信息")
    humidity: float = Field(description="湿度")
    update_time: str = Field(description="更新时间")

class IpInfo(BaseModel):
    ip: str = Field(description="ip address")