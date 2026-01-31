
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