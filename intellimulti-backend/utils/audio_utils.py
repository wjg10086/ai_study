import base64

from fastapi import UploadFile, HTTPException


class AudioProcessor:
    """音频处理工具类"""

    @staticmethod
    def audio_to_base64(audio_file: UploadFile) -> str:
        try:
            # 验证文件类型
            if not AudioProcessor.is_valid_audio_type(audio_file.content_type, audio_file.filename):
                raise HTTPException(
                    status_code=400,
                    detail="不支持的音频格式，支持的格式有: MP3, WAV, OGG, M4A, FLAC"
                )

            # 读取文件内容
            contents = audio_file.file.read()

            # 验证文件大小（可选：限制为10MB）
            max_size = 10 * 1024 * 1024  # 10MB
            if len(contents) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"音频文件过大，最大支持 {max_size // 1024 // 1024}MB"
                )

            base64_encoded = base64.b64encode(contents).decode('utf-8')
            return base64_encoded

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"音频编码失败: {str(e)}")

    @staticmethod
    def get_audio_mime_type(filename: str) -> str:
        extension = filename.split('.')[-1].lower()
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'm4a': 'audio/mp4',
        }
        return mime_types.get(extension, 'audio/mpeg')  # 默认为MP3

    @staticmethod
    def is_valid_audio_type(content_type: str, filename: str) -> bool:
        # 获取支持的MIME类型列表
        supported_mimes = {
            'audio/mpeg', 'audio/wav', 'audio/mp4'
        }

        # 检查content_type
        if content_type and content_type in supported_mimes:
            return True

        # 检查文件扩展名
        file_extension = filename.split('.')[-1].lower()
        supported_extensions = {'mp3', 'wav', 'm4a'}

        return file_extension in supported_extensions
