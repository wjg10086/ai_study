"""
实战------智能问答智能体
"""
import json
import uvicorn

from typing import List, Dict, Any, AsyncGenerator
from datetime import datetime
from pydantic import BaseModel, Field

from fastapi import HTTPException, FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages import BaseMessage

# 注意：model_utils 是自定义模块，若不存在需先实现，这里先做占位注释
# from model_utils import build_deepseek_model

# 临时实现 build_deepseek_model 避免报错（生产环境替换为你的真实实现）
async def build_deepseek_model():
    """临时占位，替换为你的真实 DeepSeek 模型构建逻辑"""
    # 示例：初始化一个简单的 chat 模型（可替换为 DeepSeek）
    model = init_chat_model(
        model="deepseek-chat",  # 对应你的 DeepSeek 模型名称
        model_kwargs={"temperature": 0.1}
    )
    return model

class ContentBlock(BaseModel):
    type: str = Field(description="内容类型: text, image, audio")
    content: str = Field(description="内容数据")

class MessageRequest(BaseModel):
    content_blocks: List[ContentBlock] = Field(default=[], description="内容块")
    history: List[Dict[str, Any]] = Field(default=[], description="对话历史")

class MessageResponse(BaseModel):
    content: str
    timestamp: str
    role: str

def create_multimodal_message(request: MessageRequest) -> HumanMessage:
    """创建多模态消息"""
    message_content = []

    # 处理内容块
    for i, block in enumerate(request.content_blocks):
        if block.type == "text":
            message_content.append({
                "type": "text",
                "text": block.content
            })

    # 避免空列表报错
    if not message_content:
        return HumanMessage(content="")
    return HumanMessage(content=message_content[0]["text"])

def convert_history_to_messages(history: List[Dict[str, Any]]) -> List[BaseMessage]:
    """将历史记录转换为 LangChain 消息格式，支持多模态内容"""
    messages = []

    # 添加系统消息
    system_prompt = """
    你是一个专业的多模态 RAG 助手，具备与用户对话的能力， 请以专业、准确、友好的方式回答用户所提问题。
    """
    messages.append(SystemMessage(content=system_prompt))

    # 转换历史消息
    for i, msg in enumerate(history):
        content = msg.get("content", "")
        content_blocks = msg.get("content_blocks", [])
        message_content = []
        if msg["role"] == "user":
            for block in content_blocks:
                if block.get("type") == "text":
                    message_content.append({
                        "type": "text",
                        "text": block.get("content", "")
                    })
            messages.append(HumanMessage(content=message_content))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=content))

    return messages

async def generate_streaming_response(
        messages: List[BaseMessage]
) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    try:
        model = await build_deepseek_model()  # 修正：异步函数需 await 调用
        # 创建流式响应
        full_response = ""

        chunk_count = 0
        async for chunk in model.astream(messages):
            chunk_count += 1
            if hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                full_response += content

                # 直接发送每个chunk的内容，避免重复
                data = {
                    "type": "content_delta",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        # 发送完成信号
        final_data = {
            "type": "message_complete",
            "full_content": full_response,
            "timestamp": datetime.now().isoformat(),
        }
        yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
    except Exception as e:
        error_data = {
            "type": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

async def chat_stream_handler(request: MessageRequest):
    """流式聊天接口（支持多模态）- 实际处理函数"""
    try:
        # 转换消息历史
        messages = convert_history_to_messages(request.history)

        # 添加当前用户消息（支持多模态）
        current_message = create_multimodal_message(request)
        messages.append(current_message)

        # 返回流式响应
        return StreamingResponse(
            generate_streaming_response(messages),
            media_type="text/event-stream",  # 修正：流式响应需对应正确的 media_type
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def chat_sync_handler(request: MessageRequest):
    """同步聊天接口（支持多模态）- 实际处理函数"""
    try:
        # 转换消息历史
        messages = convert_history_to_messages(request.history)

        # 添加当前用户消息（支持多模态）
        current_message = create_multimodal_message(request)
        messages.append(current_message)

        # 获取模型响应
        model = await build_deepseek_model()  # 修正：异步函数需 await 调用
        response = await model.ainvoke(messages)

        return MessageResponse(
            content=response.content,
            role="assistant",
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== FastAPI 应用初始化 ==========
app = FastAPI(
    title="多模态 RAG 工作台 API",
    description="基于 LangChain 1.0 的智能对话 API",
    version="1.0.0"
)

# 配置跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 接口路由注册 ==========
@app.post("/api/chat/stream", summary="流式聊天接口")
async def chat_stream_api(request: MessageRequest):
    """流式聊天接口（对外暴露）"""
    return await chat_stream_handler(request)

@app.post("/api/chat", summary="同步聊天接口", response_model=MessageResponse)
async def chat_sync_api(request: MessageRequest):
    """同步聊天接口（对外暴露）"""
    return await chat_sync_handler(request)

# ========== 启动服务 ==========
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="localhost",
        port=8000
    )