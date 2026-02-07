from typing import Optional, Dict

import requests


class IpUtils:

    @staticmethod
    def get_location_ip() -> Optional[tuple[str, str]]:
        print("【DEBUG】get_weather_by_ip 工具被调用")
        """
        绕过代理获取真实IP的地理位置（国家/省/市/区）
        返回示例：{"country": "中国", "regionName": "北京", "city": "北京市", "district": "朝阳区"}
        """
        try:
            # 核心：禁用代理，强制走本地网络
            proxies = {
                "http": None,
                "https": None,
                "ftp": None
            }

            # 调用免费IP定位接口（优先用国内可访问的）
            response = requests.get(
                "http://ip-api.com/json/",
                timeout=10,  # 超时时间
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                proxies=proxies,  # 关键：禁用代理
                verify=False  # 可选：忽略SSL验证（部分环境需加）
            )
            response.raise_for_status()  # 捕获HTTP错误
            data = response.json()

            # 接口返回成功（status为success）
            if data.get("status") == "success":
                print(data)
                return data.get('lat'), data.get('lon')
            else:
                print(f"IP定位失败：{data.get('message')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"网络请求错误：{e}")
            return None
        except Exception as e:
            print(f"解析定位数据失败：{e}")
            return None

# 测试调用
# if __name__ == "__main__":
#     location = IpUtils.get_location_ip()
#     ss = ','.join(str(i) for i in location)
#     print(f"{location[0],location[1]}")
