"""Coordinator générique Hub'Eau, piloté par le registre THEMES."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HubeauApiError, HubeauClient
from .const import DOMAIN, RESULTS_PAGE_SIZE, THEMES

_LOGGER = logging.getLogger(__name__)


class HubeauThemeCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator générique pour une thématique Hub'Eau donnée.

    `location_params` contient les paramètres de requête déjà résolus pour
    cette thématique (ex. {"code_commune": "44021"} ou {"code_bss": "...">}),
    en fonction du mode de localisation (commune ou station).
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: HubeauClient,
        theme_key: str,
        location_params: dict[str, str],
        location_label: str,
        update_interval: timedelta,
    ) -> None:
        self._client = client
        self.theme_key = theme_key
        self.theme = THEMES[theme_key]
        self.location_params = location_params
        self.location_label = location_label
        # Identifiant sûr pour unique_id (les codes BSS contiennent parfois
        # un "/", ex. "06252X0063/PZ1")
        self.safe_location_label = location_label.replace("/", "-")

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{theme_key}_{location_label}",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Récupère, pour chaque métrique du thème, la mesure la plus récente."""
        theme = self.theme
        endpoint = theme["data_endpoint"]
        date_field = theme.get("date_field")
        sort_param = theme.get("sort_param")

        results_by_metric: dict[str, dict[str, Any] | None] = {}

        for metric in theme["metrics"]:
            params: dict[str, Any] = dict(self.location_params)
            params.update(metric.get("filter", {}))
            params["size"] = RESULTS_PAGE_SIZE
            if sort_param:
                params["sort"] = sort_param

            try:
                rows = await self._client.async_get(endpoint, params)
            except HubeauApiError as err:
                raise UpdateFailed(f"Erreur API Hub'Eau ({theme['name']} / {metric['name']}): {err}") from err

            latest = self._pick_latest(rows, date_field)
            results_by_metric[metric["key"]] = latest

        conformity = None
        if "conformity_metric" in theme:
            # Réutilise le dernier jeu de résultats obtenu (eau potable) pour
            # calculer la conformité globale du dernier prélèvement, sans
            # requête supplémentaire : on relance une requête générique sans
            # filtre code_parametre afin d'obtenir tous les paramètres du
            # dernier prélèvement.
            params = dict(self.location_params)
            params["size"] = RESULTS_PAGE_SIZE
            if sort_param:
                params["sort"] = sort_param
            try:
                rows = await self._client.async_get(endpoint, params)
            except HubeauApiError as err:
                _LOGGER.exception("Erreur API Hub'Eau (%s / conformité)", theme["name"])
                raise UpdateFailed(f"Erreur API Hub'Eau ({theme['name']} / conformité): {err}") from err
            conformity = self._pick_latest(rows, date_field)

        return {
            "metrics": results_by_metric,
            "conformity": conformity,
        }

    @staticmethod
    def _pick_latest(rows: list[dict[str, Any]], date_field: str | None) -> dict[str, Any] | None:
        """Sélectionne la ligne la plus récente d'une liste de résultats.

        Si l'API trie déjà par date décroissante (sort=desc ou ordre par
        défaut), la première ligne est la plus récente ; on vérifie tout de
        même par comparaison de chaînes pour les API sans tri fiable.
        """
        if not rows:
            return None
        if not date_field:
            return rows[0]

        latest = rows[0]
        latest_date = str(latest.get(date_field) or "")
        for row in rows[1:]:
            row_date = str(row.get(date_field) or "")
            if row_date > latest_date:
                latest = row
                latest_date = row_date
        return latest
