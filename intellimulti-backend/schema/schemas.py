from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ContentBlock(BaseModel):
    type: str = Field(description="内容类型: text, image, audio")
    content: Optional[str] = Field(description="内容数据")


class MessageRequest(BaseModel):
    content_blocks: List[ContentBlock] = Field(default=[], description="内容块")
    history: List[Dict[str, Any]] = Field(default=[], description="对话历史")
    pdf_chunks: List[Dict[str, Any]] = Field(default=[], description="PDF文档块信息，用于引用溯源")


class MessageResponse(BaseModel):
    content: str
    timestamp: str
    role: str
    references: List[Dict[str, Any]] = [] # PDF的引用
