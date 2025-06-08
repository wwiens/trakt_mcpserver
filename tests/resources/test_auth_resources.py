import pytest
from unittest.mock import patch
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from server import get_auth_status

@pytest.mark.asyncio
async def test_get_auth_status_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        mock_client.get_token_expiry.return_value = int(time.time()) + 3600  # 1 hour from now
        
        result = await get_auth_status()
        
        assert "# Authentication Status" in result
        assert "You are authenticated with Trakt" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_token_expiry.assert_called_once()

@pytest.mark.asyncio
async def test_get_auth_status_not_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        result = await get_auth_status()
        
        assert "# Authentication Status" in result
        assert "You are not authenticated with Trakt" in result
        assert "start_device_auth" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_token_expiry.assert_not_called()
