"""External key fetching service."""

import os
import httpx
import jwt


async def fetch_key() -> str:
    """從外部服務獲取金鑰並解碼後返回字串。"""
    url = os.getenv("EXTERNAL_KEY_URL")
    token = os.getenv("EXTERNAL_KEY_SERVICE_TOKEN")
    secret = os.getenv("EXTERNAL_KEY_JWT_SECRET")

    if not url or not token or not secret:
        raise ValueError("Missing external key service configuration")

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"x-service-token": token})
        resp.raise_for_status()
        jwt_text = resp.text.strip()

    payload = jwt.decode(jwt_text, secret, algorithms=["HS256"])
    # 預期payload中包含 'key' 欄位
    key = payload.get("key")
    if not isinstance(key, str):
        raise ValueError("Invalid JWT payload: missing 'key'")
    return key

