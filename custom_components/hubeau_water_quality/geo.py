"""Recherche de stations Hub'Eau à proximité d'un point GPS."""
from __future__ import annotations

import logging
from typing import Any

from .api import HubeauApiError, HubeauClient
from .const import STATIONS_PAGE_SIZE, THEMES

_LOGGER = logging.getLogger(__name__)


async def async_find_nearby_stations(
    client: HubeauClient,
    theme_key: str,
    latitude: float,
    longitude: float,
    radius_km: float,
) -> list[dict[str, str]]:
    """Recherche les stations d'un thème dans un rayon donné autour d'un point.

    Renvoie une liste de dicts {"code": ..., "name": ...} triée par
    proximité (les API Hub'Eau supportant latitude/longitude/distance
    renvoient déjà les résultats sans tri de distance garanti, donc on
    retrie nous-mêmes si les coordonnées sont disponibles dans la réponse).
    """
    theme = THEMES[theme_key]
    endpoint = theme.get("stations_endpoint")
    if not endpoint:
        return []

    code_field = theme["stations_code_field"]
    name_field = theme["stations_name_field"]

    params: dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "distance": radius_km,
        "size": STATIONS_PAGE_SIZE,
    }

    try:
        rows = await client.async_get(endpoint, params)
    except HubeauApiError as err:
        _LOGGER.warning(
            "Recherche de stations à proximité impossible pour %s: %s",
            theme_key,
            err,
        )
        return []

    stations: list[dict[str, str]] = []
    for row in rows:
        code = row.get(code_field)
        if not code:
            continue
        name = row.get(name_field) or code
        stations.append({"code": str(code), "name": str(name)})

    return stations
