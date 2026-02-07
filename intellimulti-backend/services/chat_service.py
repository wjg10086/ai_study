import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, List, Dict, Any
from fastapi import HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from langchain_core.messages import BaseMessage, AIMessage
from schema.schemas import MessageRequest, MessageResponse
from schema.tool_schemas import WeatherInfo
from services.message_service import convert_history_to_messages, create_multimodal_message, \
    extract_references_from_content
from services.model_service import get_chat_model, build_deepseek_model, build_dashscope_model
from utils.mcp_tools import get_weather_by_ip, get_weather_by_city
from utils.pdf_utils import PDFProcessor


async def generate_streaming_response(
        messages: List[BaseMessage],
        pdf_chunks: List[Dict[str, Any]] = None
) -> AsyncGenerator[str, None]:
    """
        生成流式响应
        采用 SSE（text/event-stream），可以理解成：可流式传输的HTTP
            - 基于HTTP协议
            - 流式输出
            - 单向通信（服务端发送给客户端）
            - 自动重连
        数据格式为 data: {JSON字符串}\n\n，客户端会按 \n\n 分割，逐行解析 data
    """
    try:
        model = await get_chat_model()
        # 创建流式响应
        full_response = ""

        chunk_count = 0
        # model.astream内部也是利用yield异步生成器，async for 会逐次获取模型的输出块
        async for chunk in model.astream(messages):
            chunk_count += 1
            if hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                full_response += content

                # 把当前块包装成 SSE 格式，通过 yield 推送给前端
                data = {
                    "type": "content_delta",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        # 提取引用信息
        references = extract_references_from_content(full_response, pdf_chunks) if pdf_chunks else []

        # 发送完成信号
        final_data = {
            "type": "message_complete",
            "full_content": full_response,
            "timestamp": datetime.now().isoformat(),
            "references": references
        }
        yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
    except Exception as e:
        error_data = {
            "type": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"


async def handle_chat_sync(request: MessageRequest) -> MessageResponse:
    """处理同步聊天请求"""
    try:
        messages = convert_history_to_messages(request.history)
        current_message = create_multimodal_message(request, None, None)
        messages.append(current_message)

        model = await get_chat_model()
        response = await model.ainvoke(messages)

        return MessageResponse(
            content=response.content,
            role="assistant",
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_chat_stream(
        image_file: UploadFile | None = File(None),
        content_blocks: str = Form(default="[]"),
        history: str = Form(default="[]"),
        audio_file: UploadFile | None = File(None),
        pdf_file: UploadFile | None = File(None)
):
    """流式聊天接口（支持多模态）"""
    try:
        # 解析 JSON 字符串
        try:
            content_blocks_data = json.loads(content_blocks)
            history_data = json.loads(history)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"JSON 解析错误: {str(e)}")

        if pdf_file:
            pdf_processor = PDFProcessor()
            pdf_content = await pdf_file.read()
            pdf_chunks = await pdf_processor.process_pdf(file_content=pdf_content, filename=pdf_file.filename)
            request_data = MessageRequest(content_blocks=content_blocks_data, history=history_data,
                                          pdf_chunks=pdf_chunks)
        else:
            # 创建请求对象（用于传递给其他函数）
            request_data = MessageRequest(content_blocks=content_blocks_data, history=history_data)

        # 转换消息历史
        messages = convert_history_to_messages(request_data.history)

        # 添加当前用户消息（支持多模态）
        current_message = create_multimodal_message(request_data, image_file=image_file, audio_file=audio_file)
        messages.append(current_message)
        print(messages)

        # 返回流式响应
        return StreamingResponse(
            generate_streaming_response(messages, pdf_chunks if pdf_file is not None else None),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_current_weather() -> WeatherInfo:
    agent = create_agent(
        model=await build_deepseek_model(),
        tools=[get_weather_by_ip, get_weather_by_city],
        response_format=ToolStrategy(WeatherInfo),
        system_prompt='''
        你是一个专业的天气助手，可调用以下两个工具获取天气，严格按规则执行：
        1. 工具分工：
           - get_weather_by_ip：无需传参，根据用户的IP地址获取其所在地的天气（用户未指定具体城市时调用）；
           - get_weather_by_city：必须传参（城市名/经纬度），获取指定城市的天气（用户明确指定城市时调用）；
        2. 调用规则：    
           - 如果用户提问包含具体城市名（如南京、北京、上海），直接调用get_weather_by_city，传参为该城市名；
           - 如果用户仅问"今天天气怎么样"、"本地天气"等未指定城市的问题，则调用get_weather_by_ip返回实际经纬度，直接将经纬度传参给get_weather_by_city获取天气。
      
             '''
    )

    result = agent.invoke(
        {'messages': [{'role': 'user', 'content': '天气怎么样?'}]
    })
    print(type(result['structured_response']))
    # 要用deepseek模型，qwen不能输出自定义响应结构
    return result['structured_response']

# if __name__ == "__main__":
#     asyncio.run(get_current_weather())
