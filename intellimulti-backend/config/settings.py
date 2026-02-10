
class AppSettings:
    """应用配置"""
    APP_TITLE: str = "多模态 RAG 工作台 API"
    APP_DESCRIPTION: str = "基于 LangChain 1.0 的智能对话 API"
    APP_VERSION: str = "1.0.0"
    HOST: str = "localhost"
    PORT: int = 8000

class CorsSettings:
    """跨域配置"""
    ALLOW_ORIGINS: list = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]

# 实例化配置（供其他模块调用）
app_settings = AppSettings()
cors_settings = CorsSettings()


import os
from dotenv import load_dotenv

# 加载.env环境变量（开发环境），生产环境通过服务器环境变量配置
load_dotenv(override=True)

class Config:
    # ===== MySQL配置 =====
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
    MYSQL_CHARSET = "utf8mb4"
    # MySQL连接池配置（企业级核心）
    MYSQL_POOL_SIZE = int(os.getenv("MYSQL_POOL_SIZE", 10))  # 连接池大小
    MYSQL_POOL_PRE_PING = True  # 每次获取连接前检查是否可用
    MYSQL_POOL_RECYCLE = 3600   # 连接回收时间（1小时）

    # ===== Redis配置 =====
    REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_ENCODING = "utf-8"
    # Redis连接池配置
    REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", 20))

# 实例化配置
settings = Config()