"""Tests pour le module geo.py."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.hubeau_water_data.api import HubeauApiError, HubeauClient
from custom_components.hubeau_water_data.geo import async_find_nearby_stations
from custom_components.hubeau_water_data.const import THEME_PIEZOMETRIE, THEME_HYDROMETRIE, THEME_EAU_POTABLE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_find_nearby_stations_success():
    """Test la recherche réussie de stations."""
    mock_client = AsyncMock(spec=HubeauClient)
    mock_client.async_get = AsyncMock(
        return_value=[
            {"code_bss": "001", "libelle_pe": "Station 1"},
            {"code_bss": "002", "libelle_pe": "Station 2"},
        ]
    )

    result = await async_find_nearby_stations(
        client=mock_client,
        theme_key=THEME_PIEZOMETRIE,
        latitude=47.2,
        longitude=-1.5,
        radius_km=10,
    )

    assert len(result) == 2
    assert result[0] == {"code": "001", "name": "Station 1"}
    assert result[1] == {"code": "002", "name": "Station 2"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_find_nearby_stations_no_endpoint():
    """Test avec un thème sans endpoint de stations."""
    mock_client = AsyncMock(spec=HubeauClient)

    result = await async_find_nearby_stations(
        client=mock_client,
        theme_key=THEME_EAU_POTABLE,  # Ce thème n'a pas de stations_endpoint
        latitude=47.2,
        longitude=-1.5,
        radius_km=10,
    )

    assert result == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_find_nearby_stations_api_error():
    """Test la gestion des erreurs API."""
    mock_client = AsyncMock(spec=HubeauClient)
    mock_client.async_get = AsyncMock(
        side_effect=HubeauApiError("API Error")
    )

    result = await async_find_nearby_stations(
        client=mock_client,
        theme_key=THEME_PIEZOMETRIE,
        latitude=47.2,
        longitude=-1.5,
        radius_km=10,
    )

    assert result == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_find_nearby_stations_missing_code():
    """Test le filtrage des stations sans code."""
    mock_client = AsyncMock(spec=HubeauClient)
    mock_client.async_get = AsyncMock(
        return_value=[
            {"libelle_pe": "Station sans code"},
            {"code_bss": "001", "libelle_pe": "Station avec code"},
        ]
    )

    result = await async_find_nearby_stations(
        client=mock_client,
        theme_key=THEME_PIEZOMETRIE,
        latitude=47.2,
        longitude=-1.5,
        radius_km=10,
    )

    assert len(result) == 1
    assert result[0] == {"code": "001", "name": "Station avec code"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_find_nearby_stations_missing_name():
    """Test l'utilisation du code comme nom quand le nom est manquant."""
    mock_client = AsyncMock(spec=HubeauClient)
    mock_client.async_get = AsyncMock(
        return_value=[
            {"code_bss": "001"},
        ]
    )

    result = await async_find_nearby_stations(
        client=mock_client,
        theme_key=THEME_PIEZOMETRIE,
        latitude=47.2,
        longitude=-1.5,
        radius_km=10,
    )

    assert len(result) == 1
    assert result[0] == {"code": "001", "name": "001"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_find_nearby_stations_hydrometrie():
    """Test avec le thème hydrométrie (champs différents)."""
    mock_client = AsyncMock(spec=HubeauClient)
    mock_client.async_get = AsyncMock(
        return_value=[
            {"code_station": "H001", "libelle_station": "Station Hydrométrie 1"},
        ]
    )

    result = await async_find_nearby_stations(
        client=mock_client,
        theme_key=THEME_HYDROMETRIE,
        latitude=47.2,
        longitude=-1.5,
        radius_km=10,
    )

    assert len(result) == 1
    assert result[0] == {"code": "H001", "name": "Station Hydrométrie 1"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_find_nearby_stations_empty_response():
    """Test avec une réponse vide."""
    mock_client = AsyncMock(spec=HubeauClient)
    mock_client.async_get = AsyncMock(return_value=[])

    result = await async_find_nearby_stations(
        client=mock_client,
        theme_key=THEME_PIEZOMETRIE,
        latitude=47.2,
        longitude=-1.5,
        radius_km=10,
    )

    assert result == []
