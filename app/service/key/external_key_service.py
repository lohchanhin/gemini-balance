import httpx
import jwt

from app.config.config import settings
from app.log.logger import get_external_key_logger

logger = get_external_key_logger()


async def fetch_external_key() -> str:
    """從外部服務取得並解密 Gemini API Key"""
    if not settings.EXTERNAL_KEY_URL:
        logger.error("EXTERNAL_KEY_URL 未設定")
        raise ValueError("EXTERNAL_KEY_URL not set")

    headers = {}
    if settings.EXTERNAL_KEY_SERVICE_TOKEN:
        headers["x-service-token"] = settings.EXTERNAL_KEY_SERVICE_TOKEN

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.EXTERNAL_KEY_URL, headers=headers)
            response.raise_for_status()
            encoded = response.text
    except Exception as e:
        logger.error(f"取得外部 Key 失敗: {e}")
        raise

    try:
        decoded = jwt.decode(
            encoded,
            settings.EXTERNAL_KEY_JWT_SECRET,
            algorithms=["HS256"],
        )
        if isinstance(decoded, dict):
            return decoded.get("key", "")
        return decoded
    except Exception as e:
        logger.error(f"解密外部 Key 失敗: {e}")
        raise
