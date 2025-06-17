import pytest
from unittest.mock import AsyncMock, patch
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.service.config.config_service import ConfigService
from app.config.config import settings

@pytest.mark.asyncio
async def test_refresh_external_key():
    settings.EXTERNAL_KEY_URL = "https://example.com/key"
    settings.EXTERNAL_KEY_SERVICE_TOKEN = "svc-token"
    settings.EXTERNAL_KEY_JWT_SECRET = "secret"

    mock_response = AsyncMock()
    mock_response.text = "encoded_jwt"
    mock_response.raise_for_status = AsyncMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    async def mock_update_config(data):
        settings.API_KEYS = data["API_KEYS"]
        return data

    with patch("app.service.key.external_key_service.httpx.AsyncClient") as mock_ac:
        mock_ac.return_value.__aenter__.return_value = mock_client
        with patch("app.service.key.external_key_service.jwt.decode", return_value={"key": "real_key"}):
            with patch.object(ConfigService, "update_config", side_effect=mock_update_config):
                key = await ConfigService.refresh_external_key()

    assert key == "real_key"
    assert settings.API_KEYS == ["real_key"]
