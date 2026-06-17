"""Capteurs Hub'Eau, générés dynamiquement à partir du registre THEMES."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, THEMES
from .coordinator import HubeauThemeCoordinator

_LOGGER = logging.getLogger(__name__)

DEVICE_CLASS_MAP = {
    "ph": SensorDeviceClass.PH,
    "temperature": SensorDeviceClass.TEMPERATURE,
    "monetary": SensorDeviceClass.MONETARY,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Crée les entités capteur pour chaque coordinator (un par thème)."""
    coordinators: dict[str, HubeauThemeCoordinator] = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []
    for theme_key, coordinator in coordinators.items():
        theme = THEMES[theme_key]
        for metric in theme["metrics"]:
            entities.append(HubeauMetricSensor(coordinator, theme_key, metric))
        if "conformity_metric" in theme:
            entities.append(
                HubeauConformitySensor(coordinator, theme_key, theme["conformity_metric"])
            )

    async_add_entities(entities)


class HubeauBaseSensor(CoordinatorEntity[HubeauThemeCoordinator], SensorEntity):
    """Base commune : un appareil par (thème, localisation)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HubeauThemeCoordinator, theme_key: str) -> None:
        super().__init__(coordinator)
        self._theme_key = theme_key
        self._theme = THEMES[theme_key]

    @property
    def device_info(self) -> DeviceInfo:
        safe_label = self.coordinator.safe_location_label
        display_label = self.coordinator.location_label
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._theme_key}_{safe_label}")},
            name=f"{self._theme['name']} - {display_label}",
            manufacturer="Hub'Eau (OFB / BRGM / Ministères)",
            model=self._theme["name"],
            configuration_url="https://hubeau.eaufrance.fr/page/apis",
        )


class HubeauMetricSensor(HubeauBaseSensor):
    """Capteur exposant la dernière valeur connue d'une métrique d'un thème."""

    def __init__(
        self,
        coordinator: HubeauThemeCoordinator,
        theme_key: str,
        metric: dict[str, Any],
    ) -> None:
        super().__init__(coordinator, theme_key)
        self._metric = metric
        label = coordinator.safe_location_label

        self._attr_unique_id = f"{DOMAIN}_{theme_key}_{label}_{metric['key']}"
        self._attr_name = metric["name"]
        self._attr_icon = metric.get("icon")
        device_class = metric.get("device_class")
        if device_class:
            self._attr_device_class = DEVICE_CLASS_MAP.get(device_class)
        # state_class "measurement" uniquement pour les métriques numériques
        # (les métriques textuelles comme la conformité, l'écoulement visuel
        # ou la dernière espèce observée ne sont pas des mesures physiques)
        if metric.get("numeric", True):
            self._attr_state_class = "measurement"

    def _current_result(self) -> dict[str, Any] | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("metrics", {}).get(self._metric["key"])

    @property
    def available(self) -> bool:
        return super().available and self._current_result() is not None

    @property
    def native_value(self) -> Any:
        result = self._current_result()
        if result is None:
            return None
        return result.get(self._metric["value_field"])

    @property
    def native_unit_of_measurement(self) -> str | None:
        if "fixed_unit" in self._metric:
            return self._metric["fixed_unit"]
        unit_field = self._metric.get("unit_field")
        result = self._current_result()
        if unit_field and result:
            return result.get(unit_field)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        result = self._current_result()
        if result is None:
            return {}
        date_field = self._theme.get("date_field")
        attrs: dict[str, Any] = {}
        if date_field and date_field in result:
            attrs["date_mesure"] = result.get(date_field)
        # Quelques champs contextuels utiles, ajoutés s'ils existent
        for field in (
            "nom_commune",
            "libelle_station",
            "nom_station",
            "libelle_cours_eau",
            "nom_reseau",
            "libelle_parametre",
            "code_station",
        ):
            if field in result:
                attrs[field] = result.get(field)
        return attrs


class HubeauConformitySensor(HubeauBaseSensor):
    """Capteur de statut de conformité global (utilisé par l'eau potable)."""

    _attr_icon = "mdi:shield-check-outline"

    def __init__(
        self,
        coordinator: HubeauThemeCoordinator,
        theme_key: str,
        conformity_metric: dict[str, Any],
    ) -> None:
        super().__init__(coordinator, theme_key)
        self._metric = conformity_metric
        label = coordinator.safe_location_label
        self._attr_unique_id = f"{DOMAIN}_{theme_key}_{label}_{conformity_metric['key']}"
        self._attr_name = conformity_metric["name"]

    def _latest(self) -> dict[str, Any] | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("conformity")

    @property
    def available(self) -> bool:
        return super().available and self._latest() is not None

    @property
    def native_value(self) -> str | None:
        result = self._latest()
        if result is None:
            return None
        conclusion = result.get(self._metric["value_field"])
        if conclusion is None:
            return None
        mapping = {"C": "Conforme", "N": "Non conforme"}
        return mapping.get(conclusion, conclusion)

    @property
    def icon(self) -> str:
        value = self.native_value
        if value == "Non conforme":
            return "mdi:shield-alert-outline"
        if value == "Conforme":
            return "mdi:shield-check"
        return "mdi:shield-outline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        result = self._latest()
        if result is None:
            return {}
        date_field = self._theme.get("date_field")
        attrs: dict[str, Any] = {}
        if date_field and date_field in result:
            attrs["date_mesure"] = result.get(date_field)
        for field in (
            "nom_commune",
            "nom_reseau",
            "nom_distributeur",
            "code_prelevement",
            "conformite_limites_bact_prelevement",
            "conformite_limites_pc_prelevement",
            "conformite_references_bact_prelevement",
            "conformite_references_pc_prelevement",
        ):
            if field in result:
                attrs[field] = result.get(field)
        return attrs
