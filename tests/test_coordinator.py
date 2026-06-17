"""Tests pour le module coordinator.py."""

from unittest.mock import MagicMock

import pytest

from custom_components.hubeau_water_data.coordinator import HubeauThemeCoordinator


@pytest.mark.unit
def test_pick_latest_with_date_field():
    """Test la sélection de la ligne la plus récente avec champ date."""
    rows = [
        {"date": "2024-01-01", "value": 10},
        {"date": "2024-01-03", "value": 30},
        {"date": "2024-01-02", "value": 20},
    ]

    result = HubeauThemeCoordinator._pick_latest(rows, "date")

    assert result["value"] == 30


@pytest.mark.unit
def test_pick_latest_without_date_field():
    """Test la sélection sans champ date (première ligne)."""
    rows = [
        {"value": 10},
        {"value": 20},
        {"value": 30},
    ]

    result = HubeauThemeCoordinator._pick_latest(rows, None)

    assert result["value"] == 10


@pytest.mark.unit
def test_pick_latest_empty_list():
    """Test avec une liste vide."""
    result = HubeauThemeCoordinator._pick_latest([], "date")

    assert result is None


@pytest.mark.unit
def test_pick_latest_with_missing_date():
    """Test avec des dates manquantes."""
    rows = [
        {"value": 10},
        {"date": "2024-01-01", "value": 20},
        {"value": 30},
    ]

    result = HubeauThemeCoordinator._pick_latest(rows, "date")

    assert result["value"] == 20
