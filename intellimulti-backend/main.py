import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from schemas import MessageRequest, MessageResponse
from services.chat_service import handle_chat_stream, handle_chat_sync
from config.settings import app_settings, cors_settings

# 初始化 FastAPI 应用
app = FastAPI(
    title=app_settings.APP_TITLE,
    description=app_settings.APP_DESCRIPTION,
    version=app_settings.APP_VERSION
)

# 配置跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.ALLOW_ORIGINS, # 允许哪些前端域名可以访问（可设置为 ["*"] 生产环境慎用）
    allow_credentials=cors_settings.ALLOW_CREDENTIALS,
    allow_methods=cors_settings.ALLOW_METHODS,
    allow_headers=cors_settings.ALLOW_HEADERS,
)

# 注册路由
@app.post("/api/chat/stream", summary="流式聊天接口")
async def chat_stream(
        image_file: UploadFile | None = File(None),
        content_blocks: str = Form(default="[]"),
        history: str = Form(default="[]"),
        audio_file: UploadFile | None = File(None),
        pdf_file: UploadFile | None = File(None)
):
    return await handle_chat_stream(image_file, content_blocks, history, audio_file, pdf_file)

# @app.post("/api/chat", summary="同步聊天接口", response_model=MessageResponse)
# async def chat_sync_api(request: MessageRequest):
#     return await handle_chat_sync(request)

# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        "main:app", # 指向 main.py 中的 app 对象（当在该目录直接运行脚本时）
        # app, # 也可以直接传入 app 对象（当通过其他方式运行时）
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=False  # 生产环境关闭 reload
    )