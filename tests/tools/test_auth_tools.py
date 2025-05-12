import pytest
import asyncio
from unittest.mock import patch, MagicMock
import time
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from server import (
    start_device_auth, check_auth_status, clear_auth
)
from models import FormatHelper
from trakt_client import TraktClient

@pytest.mark.asyncio
async def test_start_device_auth():
    device_code_response = {
        "device_code": "device_code_123",
        "user_code": "USER123",
        "verification_url": "https://trakt.tv/activate",
        "expires_in": 600,
        "interval": 5
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {}):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        future = asyncio.Future()
        future.set_result(MagicMock(
            device_code="device_code_123",
            user_code="USER123",
            verification_url="https://trakt.tv/activate",
            expires_in=600,
            interval=5
        ))
        mock_client.get_device_code.return_value = future
        
        result = await start_device_auth()
        
        assert "# Trakt Authentication Required" in result
        assert "USER123" in result
        assert "https://trakt.tv/activate" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_code.assert_called_once()

@pytest.mark.asyncio
async def test_start_device_auth_already_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        result = await start_device_auth()
        
        assert "You are already authenticated with Trakt" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_code.assert_not_called()

@pytest.mark.asyncio
async def test_check_auth_status_authenticated():
    with patch('server.TraktClient') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        result = await check_auth_status()
        
        assert "# Authentication Successful" in result
        assert "You are now authenticated with Trakt" in result
        
        mock_client.is_authenticated.assert_called_once()

@pytest.mark.asyncio
async def test_check_auth_status_no_active_flow():
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {}):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        result = await check_auth_status()
        
        assert "No active authentication flow" in result
        assert "start_device_auth" in result
        
        mock_client.is_authenticated.assert_called_once()

@pytest.mark.asyncio
async def test_check_auth_status_expired_flow():
    expired_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) - 100,  # Expired 100 seconds ago
        "interval": 5,
        "last_poll": 0
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', expired_flow):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        result = await check_auth_status()
        
        assert "Authentication flow expired" in result
        assert "start a new one" in result
        
        mock_client.is_authenticated.assert_called_once()

@pytest.mark.asyncio
async def test_check_auth_status_pending_authorization():
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time()) - 10  # Last polled 10 seconds ago
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', active_flow):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        none_future = asyncio.Future()
        none_future.set_result(None)
        mock_client.get_device_token.return_value = none_future
        
        result = await check_auth_status()
        
        assert "# Authorization Pending" in result
        assert "I don't see that you've completed the authorization yet" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_token.assert_called_once_with("device_code_123")

@pytest.mark.asyncio
async def test_check_auth_status_authorization_complete():
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time()) - 10  # Last polled 10 seconds ago
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', active_flow):
        
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        future = asyncio.Future()
        future.set_result(MagicMock(
            access_token="access_token_123",
            refresh_token="refresh_token_123"
        ))
        mock_client.get_device_token.return_value = future
        
        result = await check_auth_status()
        
        assert "# Authentication Successful" in result
        assert "You have successfully authorized" in result
        
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_token.assert_called_once_with("device_code_123")

@pytest.mark.asyncio
async def test_clear_auth():
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {"device_code": "device_code_123"}):
        
        mock_client = mock_client_class.return_value
        mock_client.clear_auth_token.return_value = True
        
        result = await clear_auth()
        
        assert "You have been successfully logged out of Trakt" in result
        
        mock_client.clear_auth_token.assert_called_once()
        
        from server import active_auth_flow
        assert active_auth_flow == {}

@pytest.mark.asyncio
async def test_clear_auth_not_authenticated():
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {}):
        
        mock_client = mock_client_class.return_value
        mock_client.clear_auth_token.return_value = False
        
        result = await clear_auth()
        
        assert "You were not authenticated with Trakt" in result
        
        mock_client.clear_auth_token.assert_called_once()
import pytest
import asyncio
from unittest.mock import patch, MagicMock
import time
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from server import (
    start_device_auth, check_auth_status, clear_auth
)
from models import FormatHelper
from trakt_client import TraktClient

@pytest.mark.asyncio
async def test_start_device_auth():
    """Test starting the device authentication flow."""
    # Mock device code response
    device_code_response = {
        "device_code": "device_code_123",
        "user_code": "USER123",
        "verification_url": "https://trakt.tv/activate",
        "expires_in": 600,
        "interval": 5
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {}):
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Create awaitable result for get_device_code
        future = asyncio.Future()
        future.set_result(MagicMock(
            device_code="device_code_123",
            user_code="USER123",
            verification_url="https://trakt.tv/activate",
            expires_in=600,
            interval=5
        ))
        mock_client.get_device_code.return_value = future
        
        # Call the tool function
        result = await start_device_auth()
        
        # Verify the result
        assert "# Trakt Authentication Required" in result
        assert "USER123" in result
        assert "https://trakt.tv/activate" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_code.assert_called_once()

@pytest.mark.asyncio
async def test_start_device_auth_already_authenticated():
    """Test starting device auth when already authenticated."""
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        # Call the tool function
        result = await start_device_auth()
        
        # Verify the result
        assert "You are already authenticated with Trakt" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_code.assert_not_called()

@pytest.mark.asyncio
async def test_check_auth_status_authenticated():
    """Test checking auth status when already authenticated."""
    with patch('server.TraktClient') as mock_client_class:
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = True
        
        # Call the tool function
        result = await check_auth_status()
        
        # Verify the result
        assert "# Authentication Successful" in result
        assert "You are now authenticated with Trakt" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()

@pytest.mark.asyncio
async def test_check_auth_status_no_active_flow():
    """Test checking auth status with no active flow."""
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {}):
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Call the tool function
        result = await check_auth_status()
        
        # Verify the result
        assert "No active authentication flow" in result
        assert "start_device_auth" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()

@pytest.mark.asyncio
async def test_check_auth_status_expired_flow():
    """Test checking auth status with expired flow."""
    # Create an expired auth flow
    expired_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) - 100,  # Expired 100 seconds ago
        "interval": 5,
        "last_poll": 0
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', expired_flow):
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Call the tool function
        result = await check_auth_status()
        
        # Verify the result
        assert "Authentication flow expired" in result
        assert "start a new one" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()

@pytest.mark.asyncio
async def test_check_auth_status_pending_authorization():
    """Test checking auth status with pending authorization."""
    # Create an active auth flow
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time()) - 10  # Last polled 10 seconds ago
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', active_flow):
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Create a Future that resolves to None instead of returning None directly
        none_future = asyncio.Future()
        none_future.set_result(None)
        mock_client.get_device_token.return_value = none_future
        
        # Call the tool function
        result = await check_auth_status()
        
        # Verify the result
        assert "# Authorization Pending" in result
        assert "I don't see that you've completed the authorization yet" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_token.assert_called_once_with("device_code_123")

@pytest.mark.asyncio
async def test_check_auth_status_authorization_complete():
    """Test checking auth status when authorization is complete."""
    # Create an active auth flow
    active_flow = {
        "device_code": "device_code_123",
        "expires_at": int(time.time()) + 500,  # Expires in 500 seconds
        "interval": 5,
        "last_poll": int(time.time()) - 10  # Last polled 10 seconds ago
    }
    
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', active_flow):
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.is_authenticated.return_value = False
        
        # Create awaitable result for get_device_token
        future = asyncio.Future()
        future.set_result(MagicMock(
            access_token="access_token_123",
            refresh_token="refresh_token_123"
        ))
        mock_client.get_device_token.return_value = future
        
        # Call the tool function
        result = await check_auth_status()
        
        # Verify the result
        assert "# Authentication Successful" in result
        assert "You have successfully authorized" in result
        
        # Verify the client methods were called
        mock_client.is_authenticated.assert_called_once()
        mock_client.get_device_token.assert_called_once_with("device_code_123")

@pytest.mark.asyncio
async def test_clear_auth():
    """Test clearing authentication."""
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {"device_code": "device_code_123"}):
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.clear_auth_token.return_value = True
        
        # Call the tool function
        result = await clear_auth()
        
        # Verify the result
        assert "You have been successfully logged out of Trakt" in result
        
        # Verify the client methods were called
        mock_client.clear_auth_token.assert_called_once()
        
        # Verify active_auth_flow was cleared
        from server import active_auth_flow
        assert active_auth_flow == {}

@pytest.mark.asyncio
async def test_clear_auth_not_authenticated():
    """Test clearing authentication when not authenticated."""
    with patch('server.TraktClient') as mock_client_class, \
         patch('server.active_auth_flow', {}):
        
        # Configure the mock
        mock_client = mock_client_class.return_value
        mock_client.clear_auth_token.return_value = False
        
        # Call the tool function
        result = await clear_auth()
        
        # Verify the result
        assert "You were not authenticated with Trakt" in result
        
        # Verify the client methods were called
        mock_client.clear_auth_token.assert_called_once()
