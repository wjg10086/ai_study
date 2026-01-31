"""
intelligentQuestionAnsweringAgent/  # 项目根目录
├── __init__.py                     # 包初始化文件
├── main.py                         # FastAPI 应用入口（路由注册、服务启动）
├── schemas.py                      # 数据模型（Pydantic 类、请求/响应结构）
├── services/                       # 业务逻辑服务层（核心功能实现）
│   ├── __init__.py
│   ├── chat_service.py              # 聊天业务处理（流式/同步）
│   ├── message_service.py           # 消息转换（历史消息、多模态消息处理）
│   └── model_service.py            # 模型初始化与调用（DeepSeek 模型）
├── utils/                          # 工具类（通用辅助函数）
│   ├── __init__.py
│   └── common_utils.py             # 时间、JSON 等通用工具
└── config11/                         # 配置文件（模型参数、服务配置）
    ├── __init__.py
    └── settings.py                  # 全局配置项（如端口、模型名称、跨域配置）
"""