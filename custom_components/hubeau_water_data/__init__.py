"""Intégration Hub'Eau (13 thématiques)."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HubeauClient
from .const import (
    CONF_CODE_COMMUNE,
    CONF_CODE_DEPARTEMENT,
    CONF_NOM_COMMUNE,
    CONF_SCAN_INTERVAL_HOURS,
    CONF_STATIONS,
    CONF_THEMES,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    LOC_STATION,
    THEMES,
)
from .coordinator import HubeauThemeCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


def _build_location_params(theme_key: str, entry: ConfigEntry) -> tuple[dict, str] | None:
    """Construit les paramètres de requête de localisation pour un thème.

    Renvoie (params, label) où label sert à différencier les coordinators
    d'un même thème (ex. plusieurs stations choisies par l'utilisateur).
    """
    theme = THEMES[theme_key]
    data = entry.data

    if theme["localisation"] == LOC_STATION:
        station = data.get(CONF_STATIONS, {}).get(theme_key)
        if not station:
            return None
        param_name = theme["station_param"]
        return {param_name: station["code"]}, station["code"]

    # Mode commune (ou variantes département / nom de commune)
    code_commune = data.get(CONF_CODE_COMMUNE, "")
    if theme.get("commune_uses_departement"):
        code_dep = data.get(CONF_CODE_DEPARTEMENT) or code_commune[:2]
        return {theme["commune_param"]: code_dep}, code_dep
    if theme.get("commune_uses_name"):
        # L'API Poisson filtre par libelle_commune (nom), pas par code INSEE
        nom_commune = data.get(CONF_NOM_COMMUNE, code_commune)
        return {theme["commune_param"]: nom_commune}, code_commune
    if not code_commune:
        return None
    return {theme["commune_param"]: code_commune}, code_commune


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Initialise l'intégration : un coordinator par thématique sélectionnée."""
    session = async_get_clientsession(hass)
    client = HubeauClient(session)

    scan_interval_hours = entry.options.get(CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS)
    update_interval = timedelta(hours=scan_interval_hours)

    coordinators: dict[str, HubeauThemeCoordinator] = {}

    for theme_key in entry.data.get(CONF_THEMES, []):
        built = _build_location_params(theme_key, entry)
        if built is None:
            _LOGGER.warning("Thème %s ignoré : aucune localisation valide configurée", theme_key)
            continue
        location_params, location_label = built

        coordinator = HubeauThemeCoordinator(
            hass=hass,
            client=client,
            theme_key=theme_key,
            location_params=location_params,
            location_label=location_label,
            update_interval=update_interval,
        )
        await coordinator.async_config_entry_first_refresh()
        coordinators[theme_key] = coordinator

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinators

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
