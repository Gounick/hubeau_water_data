"""Configuration pytest pour les tests asynchrones."""

import pytest


@pytest.fixture
def enable_event_loop_debug():
    """Fixture vide pour éviter les erreurs pytest-asyncio."""
    pass
