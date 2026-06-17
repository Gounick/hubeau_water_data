"""Client HTTP générique pour les API Hub'Eau.

Toutes les thématiques Hub'Eau partagent le même modèle de pagination
(page/size) à l'exception de l'opération observations_tr d'hydrométrie qui
utilise un curseur, mais qui se comporte correctement même sans curseur
pour une simple lecture de la page la plus récente (cf. constat empirique :
tri par défaut = date d'observation décroissante).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import API_TIMEOUT_SECONDS

_LOGGER = logging.getLogger(__name__)


class HubeauApiError(Exception):
    """Erreur générique de communication avec une API Hub'Eau."""


class HubeauClient:
    """Wrapper HTTP générique, paramétré par endpoint et query params."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def async_get(self, url: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Effectue une requête GET et renvoie la liste `data` de la réponse."""
        data = await self._request(url, params)
        if not isinstance(data, dict):
            _LOGGER.error("Réponse API invalide: attendu dict, reçu %s", type(data))
            return []
        result = data.get("data", [])
        if not isinstance(result, list):
            _LOGGER.error("Réponse API invalide: attendu list pour 'data', reçu %s", type(result))
            return []
        return result

    async def async_get_raw(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Effectue une requête GET et renvoie la réponse JSON complète."""
        data = await self._request(url, params)
        if not isinstance(data, dict):
            _LOGGER.error("Réponse API invalide: attendu dict, reçu %s", type(data))
            return {}
        return data

    async def _request(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            async with asyncio.timeout(API_TIMEOUT_SECONDS):
                resp = await self._session.get(url, params=params)
                if resp.status == 400:
                    body = await resp.text()
                    raise HubeauApiError(f"Requête invalide ({resp.status}) sur {url}: {body}")
                if resp.status >= 500:
                    raise HubeauApiError(f"Erreur serveur Hub'Eau ({resp.status}) sur {url}")
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as err:
            _LOGGER.exception("Erreur de connexion à Hub'Eau (%s)", url)
            raise HubeauApiError(f"Erreur de connexion à Hub'Eau ({url}): {err}") from err
        except TimeoutError as err:
            _LOGGER.exception("Délai d'attente dépassé en contactant Hub'Eau (%s)", url)
            raise HubeauApiError(f"Délai d'attente dépassé en contactant Hub'Eau ({url})") from err
