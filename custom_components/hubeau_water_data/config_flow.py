"""Config flow multi-étapes pour Hub'Eau (13 thématiques)."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HubeauApiError, HubeauClient
from .const import (
    ALL_THEMES,
    CONF_CODE_COMMUNE,
    CONF_CODE_DEPARTEMENT,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NOM_COMMUNE,
    CONF_RADIUS_KM,
    CONF_SCAN_INTERVAL_HOURS,
    CONF_STATIONS,
    CONF_THEMES,
    DEFAULT_RADIUS_KM,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    LOC_STATION,
    THEMES,
)
from .geo import async_find_nearby_stations

_LOGGER = logging.getLogger(__name__)

# Endpoint Hub'Eau "communes_udi" utilisé uniquement pour vérifier la
# validité d'un code commune (réutilisé de la v1 eau potable)
VERIF_COMMUNE_URL = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/communes_udi"


def _theme_options() -> list[selector.SelectOptionDict]:
    options = []
    for key in ALL_THEMES:
        theme = THEMES[key]
        label = theme["name"]
        if theme.get("deprecated"):
            label += " (⚠️ API en cours de fermeture par Hub'Eau)"
        options.append(selector.SelectOptionDict(value=key, label=label))
    return options


class HubeauConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère la configuration multi-étapes de l'intégration Hub'Eau."""

    VERSION = 2

    def __init__(self) -> None:
        self._data: dict[str, Any] = {
            CONF_THEMES: [],
            CONF_STATIONS: {},
        }
        self._station_themes_pending: list[str] = []

    # ------------------------------------------------------------------
    # Étape 1 : sélection des thématiques
    # ------------------------------------------------------------------
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            selected = user_input.get(CONF_THEMES, [])
            if not selected:
                errors["base"] = "no_theme_selected"
            else:
                self._data[CONF_THEMES] = selected
                return await self.async_step_location()

        schema = vol.Schema(
            {
                vol.Required(CONF_THEMES): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=_theme_options(),
                        multiple=True,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    # ------------------------------------------------------------------
    # Étape 2 : localisation (commune + coordonnées GPS pour les stations)
    # ------------------------------------------------------------------
    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}
        needs_station_search = any(
            THEMES[t]["localisation"] == LOC_STATION for t in self._data[CONF_THEMES]
        )

        if user_input is not None:
            code_commune = user_input.get(CONF_CODE_COMMUNE, "").strip()
            code_departement = user_input.get(CONF_CODE_DEPARTEMENT, "").strip()

            nom_commune = code_commune
            if code_commune:
                session = async_get_clientsession(self.hass)
                client = HubeauClient(session)
                try:
                    rows = await client.async_get(
                        VERIF_COMMUNE_URL, {"code_commune": code_commune, "size": 1}
                    )
                except HubeauApiError:
                    rows = []
                if rows:
                    nom_commune = rows[0].get("nom_commune", code_commune)

            self._data[CONF_CODE_COMMUNE] = code_commune
            self._data[CONF_NOM_COMMUNE] = nom_commune
            self._data[CONF_CODE_DEPARTEMENT] = code_departement or code_commune[:2]
            self._data[CONF_LATITUDE] = user_input.get(CONF_LATITUDE)
            self._data[CONF_LONGITUDE] = user_input.get(CONF_LONGITUDE)
            self._data[CONF_RADIUS_KM] = user_input.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM)

            if needs_station_search and (
                self._data.get(CONF_LATITUDE) is None
                or self._data.get(CONF_LONGITUDE) is None
            ):
                errors["base"] = "gps_required_for_stations"
            else:
                self._station_themes_pending = [
                    t for t in self._data[CONF_THEMES]
                    if THEMES[t]["localisation"] == LOC_STATION
                ]
                if self._station_themes_pending:
                    return await self.async_step_station()
                return self._finish()

        schema_dict: dict[Any, Any] = {
            vol.Optional(CONF_CODE_COMMUNE, default=""): str,
            vol.Optional(CONF_CODE_DEPARTEMENT, default=""): str,
        }
        lat_selector = selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=-90, max=90, step=0.00001, mode=selector.NumberSelectorMode.BOX
            )
        )
        lon_selector = selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=-180, max=180, step=0.00001, mode=selector.NumberSelectorMode.BOX
            )
        )
        radius_selector = selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1, max=200, step=1, mode=selector.NumberSelectorMode.BOX
            )
        )
        if needs_station_search:
            schema_dict[vol.Required(CONF_LATITUDE)] = lat_selector
            schema_dict[vol.Required(CONF_LONGITUDE)] = lon_selector
            schema_dict[vol.Optional(CONF_RADIUS_KM, default=DEFAULT_RADIUS_KM)] = radius_selector
        else:
            schema_dict[vol.Optional(CONF_LATITUDE)] = lat_selector
            schema_dict[vol.Optional(CONF_LONGITUDE)] = lon_selector
            schema_dict[vol.Optional(CONF_RADIUS_KM, default=DEFAULT_RADIUS_KM)] = radius_selector

        return self.async_show_form(
            step_id="location",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            description_placeholders={"exemple": "75101 (Paris 1er arrondissement)"},
        )

    # ------------------------------------------------------------------
    # Étape 3 : sélection de station pour chaque thème géolocalisé
    # ------------------------------------------------------------------
    async def async_step_station(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}
        current_theme = self._station_themes_pending[0]
        theme = THEMES[current_theme]

        session = async_get_clientsession(self.hass)
        client = HubeauClient(session)
        nearby = await async_find_nearby_stations(
            client,
            current_theme,
            self._data[CONF_LATITUDE],
            self._data[CONF_LONGITUDE],
            self._data[CONF_RADIUS_KM],
        )

        if user_input is not None:
            chosen = user_input.get("station_code", "").strip()
            manual = user_input.get("manual_code", "").strip()
            final_code = manual or chosen

            if not final_code:
                errors["base"] = "station_required"
            else:
                matching_name = next(
                    (s["name"] for s in nearby if s["code"] == final_code),
                    final_code,
                )
                self._data[CONF_STATIONS][current_theme] = {
                    "code": final_code,
                    "name": matching_name,
                }
                self._station_themes_pending = self._station_themes_pending[1:]
                if self._station_themes_pending:
                    return await self.async_step_station()
                return self._finish()

        options = [
            selector.SelectOptionDict(value=s["code"], label=f"{s['name']} ({s['code']})")
            for s in nearby
        ]

        schema_dict: dict[Any, Any] = {}
        if options:
            schema_dict[vol.Optional("station_code")] = selector.SelectSelector(
                selector.SelectSelectorConfig(options=options, mode=selector.SelectSelectorMode.DROPDOWN)
            )
        schema_dict[vol.Optional("manual_code", default="")] = str

        return self.async_show_form(
            step_id="station",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            description_placeholders={
                "theme_name": theme["name"],
                "count": str(len(nearby)),
            },
        )

    # ------------------------------------------------------------------
    def _finish(self) -> config_entries.FlowResult:
        title_bits = []
        if self._data.get(CONF_NOM_COMMUNE):
            title_bits.append(self._data[CONF_NOM_COMMUNE])
        title = "Hub'Eau - " + (title_bits[0] if title_bits else "Mes données")

        return self.async_create_entry(
            title=title,
            data=self._data,
            options={CONF_SCAN_INTERVAL_HOURS: DEFAULT_SCAN_INTERVAL_HOURS},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> HubeauOptionsFlow:
        return HubeauOptionsFlow()


class HubeauOptionsFlow(config_entries.OptionsFlow):
    """Permet de modifier l'intervalle de rafraîchissement."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL_HOURS, default=current): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=168, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
