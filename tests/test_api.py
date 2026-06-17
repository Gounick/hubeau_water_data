"""Tests pour le module api.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.hubeau_water_data.api import HubeauApiError, HubeauClient


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_get_success():
    """Test que async_get renvoie les données correctes."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"data": [{"test": "value"}]})
    mock_response.raise_for_status = MagicMock()
    mock_session.get = AsyncMock(return_value=mock_response)

    client = HubeauClient(mock_session)
    result = await client.async_get("http://test.com", {"param": "value"})

    assert result == [{"test": "value"}]
    mock_session.get.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_get_invalid_response_structure():
    """Test que async_get gère les réponses avec structure invalide."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"invalid": "structure"})
    mock_response.raise_for_status = MagicMock()
    mock_session.get = AsyncMock(return_value=mock_response)

    client = HubeauClient(mock_session)
    result = await client.async_get("http://test.com", {})

    assert result == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_get_data_not_list():
    """Test que async_get gère quand 'data' n'est pas une liste."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"data": "not a list"})
    mock_response.raise_for_status = MagicMock()
    mock_session.get = AsyncMock(return_value=mock_response)

    client = HubeauClient(mock_session)
    result = await client.async_get("http://test.com", {})

    assert result == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_get_raw_success():
    """Test que async_get_raw renvoie la réponse JSON complète."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"raw": "data"})
    mock_response.raise_for_status = MagicMock()
    mock_session.get = AsyncMock(return_value=mock_response)

    client = HubeauClient(mock_session)
    result = await client.async_get_raw("http://test.com", {})

    assert result == {"raw": "data"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_get_raw_invalid_response():
    """Test que async_get_raw gère les réponses invalides."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value="not a dict")
    mock_response.raise_for_status = MagicMock()
    mock_session.get = AsyncMock(return_value=mock_response)

    client = HubeauClient(mock_session)
    result = await client.async_get_raw("http://test.com", {})

    assert result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_400_error():
    """Test que les erreurs 400 sont gérées correctement."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.text = AsyncMock(return_value="Bad request")
    mock_session.get = AsyncMock(return_value=mock_response)

    client = HubeauClient(mock_session)

    with pytest.raises(HubeauApiError) as exc_info:
        await client._request("http://test.com", {})

    assert "400" in str(exc_info.value)
    assert "Bad request" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_500_error():
    """Test que les erreurs 500 sont gérées correctement."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_session.get = AsyncMock(return_value=mock_response)

    client = HubeauClient(mock_session)

    with pytest.raises(HubeauApiError) as exc_info:
        await client._request("http://test.com", {})

    assert "500" in str(exc_info.value)
    assert "Erreur serveur" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_client_error():
    """Test que les erreurs de connexion sont gérées correctement."""
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(side_effect=aiohttp.ClientError("Connection error"))

    client = HubeauClient(mock_session)

    with pytest.raises(HubeauApiError) as exc_info:
        await client._request("http://test.com", {})

    assert "Erreur de connexion" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_timeout_error():
    """Test que les timeouts sont gérés correctement."""
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(side_effect=TimeoutError("Timeout"))

    client = HubeauClient(mock_session)

    with pytest.raises(HubeauApiError) as exc_info:
        await client._request("http://test.com", {})

    assert "Délai d'attente" in str(exc_info.value)
