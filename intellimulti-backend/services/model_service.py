from fastapi import HTTPException
from langchain.chat_models import init_chat_model
import os

async def build_deepseek_model():
    """构建 DeepSeek 模型实例（封装模型初始化逻辑）"""
    try:
        '''
            构建并返回一个deepseek模型实例。
            统一配置模型参数，方便全局复用。
            :return:
            '''
        return init_chat_model(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY")
        )
    except Exception as e:
        raise Exception(f"模型初始化失败：{str(e)}")

async def get_chat_model():
    '''
    阿里多模态Qwen-Omni模型实例。
    Qwen-Omni 模型能够接收文本、图片、音频、视频等多种模态的组合输入，并生成文本或语音形式的回复，
    提供多种拟人音色，支持多语言和方言的语音输出，可应用于文本创作、视觉识别、语音
    这里将openai设置服务商，因为百炼兼容且必须设置
    :return: BaseChatModel 实例
    '''
    try:
        model = init_chat_model(
            model="qwen3-omni-flash",
            model_provider="openai",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
        )
        return model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型初始化失败: {str(e)}")

async def build_dashscope_model():
    '''
    构建并返回一个百炼模型实例。
    统一配置模型参数，方便全局复用。
    这里将openai设置服务商，因为百炼兼容且必须设置
    :return: BaseChatModel 实例
    '''
    return init_chat_model(
        model="qwen-max",  # 百炼模型名（qwen-turbo/qwen-plus/qwen-max）
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 百炼兼容OpenAI的固定地址
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # 你的百炼API_KEY环境变量
        model_provider="openai"  # 关键：显式指定提供商（必加，否则报错）
    )

