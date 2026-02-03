import base64
import io
import fitz  # PyMuPDF
from PIL import Image
from typing import List, Dict, Any, Iterator
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    @staticmethod
    async def extract_pdf_pages_as_images(file_content: bytes, max_pages: int = 5) -> List[str]:
        """
        因为上传的pdf有时候会是扫描件，无法直接读取文字，通常需要将文档的每页作为图片提取出来并作OCR处理
        """
        try:
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            total_pages = len(pdf_document)
            pages_to_extract = min(max_pages, total_pages)

            images = []
            for page_num in range(pages_to_extract):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
                images.append(base64_image)

            pdf_document.close()
            return images

        except Exception as e:
            raise

    @staticmethod
    def read_pdf_pages(pdf_path):
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            print(f"错误：文件 '{pdf_path}' 不存在")
            return {}

    async def process_pdf(self, file_content: bytes, filename: str):
        """
        流式处理PDF文档
        返回处理进度和结果
        """
        try:
            # Step 1: 保存临时文件
            print('保存临时文件')

            # 创建临时文件
            temp = r'temp'
            # 先创建 temp 目录（如果不存在）, exist_ok=True 表示如果目录已存在，不会报错
            os.makedirs(temp, exist_ok=True)
            tmp_file_path = os.path.join(temp, filename)
            with open(tmp_file_path, 'wb') as f:
                f.write(file_content)

            full_text = ""
            doc = fitz.open(tmp_file_path)
            # 存储每页内容
            pages_content = {}
            # 逐页读取内容
            for page_num in range(len(doc)):
                page = doc[page_num]
                # 提取文本
                text = page.get_text()
                full_text += text
                # 存储页面内容
                pages_content[page_num + 1] = text
            print(f"合并后文本长度: {len(full_text)} 字符")

            # 调试：输出前200个字符看看提取到了什么
            preview = full_text[:200] if full_text else "空内容"
            print(f"文本预览: {repr(preview)}")

            # 使用RecursiveCharacterTextSplitter进行智能分块
            text_chunks = self.text_splitter.split_text(full_text)
            print(f"文本分块完成，共 {len(text_chunks)} 个块")

            # Step 4: 构建文档块
            print(f"正在构建 {len(text_chunks)} 个文档块...")

            # 构建带元数据的文档块（包含页码信息）
            document_chunks = []
            for i, chunk in enumerate(text_chunks):
                if chunk.strip():  # 过滤空块
                    # 尝试从原始文档块中获取页码信息
                    page_number = 1  # 默认页码
                    sorted_keys = sorted(pages_content.keys())
                    for page_number in sorted_keys:
                        if chunk.strip()[:50] in pages_content[page_number]:
                            break

                    doc_chunk = {
                        "id": f"{filename}_{i}",
                        "content": chunk.strip(),
                        "metadata": {
                            "source": filename,
                            "chunk_id": i,
                            "chunk_size": len(chunk),
                            "total_chunks": len(text_chunks),
                            "page_number": page_number,
                            "reference_id": f"[{i + 1}]",
                            "source_info": f"{filename} - 第{page_number}页"
                        }
                    }
                    document_chunks.append(doc_chunk)

            print(document_chunks)

            # Step 5: 完成处理
            print(f"处理完成！共生成 {len(document_chunks)} 个文档块")

            # 返回处理结果
            return document_chunks
        except Exception as e:
            print(f"PDF处理失败: {str(e)}")
            return {
                "type": "error",
                "error": f"PDF处理失败: {str(e)}"
            }

