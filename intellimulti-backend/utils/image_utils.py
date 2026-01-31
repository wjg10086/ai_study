import base64
from fastapi import UploadFile, HTTPException


class ImageProcessor:
    """图像处理工具类"""

    @staticmethod
    def image_to_base64(image_file: UploadFile) -> str:
        try:
            # 读取文件内容
            with image_file.file as f:
                contents = f.read()
            # 进行base64编码
            base64_encoded = base64.b64encode(contents).decode('utf-8')
            return base64_encoded
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"图像编码失败: {str(e)}")

    @staticmethod
    def get_image_mime_type(filename: str) -> str:
        extension = filename.split('.')[-1].lower()
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp'
        }
        return mime_types.get(extension, 'image/jpeg')
