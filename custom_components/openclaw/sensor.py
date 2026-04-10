"""Sensor platform for OpenClaw."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OpenClawCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OpenClawCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        OpenClawStatusSensor(coordinator, entry),
        OpenClawModelSensor(coordinator, entry),
        OpenClawTokensInSensor(coordinator, entry),
        OpenClawTokensOutSensor(coordinator, entry),
        OpenClawLastUpdatedSensor(coordinator, entry),
        OpenClawCostSensor(coordinator, entry),
    ])


class OpenClawBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: OpenClawCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "OpenClaw AI",
            "manufacturer": "OpenClaw",
            "model": "AI Gateway",
        }


class OpenClawStatusSensor(OpenClawBaseSensor):
    _attr_translation_key = "status"
    _attr_icon = "mdi:robot"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_status"

    @property
    def native_value(self):
        return self.coordinator.data.get("state", "unknown")

    @property
    def extra_state_attributes(self):
        d = self.coordinator.data or {}
        return {
            "model": d.get("model"),
            "session": d.get("session"),
            "context_pct": d.get("context_pct"),
            "last_updated": d.get("last_updated"),
        }


class OpenClawModelSensor(OpenClawBaseSensor):
    _attr_translation_key = "model"
    _attr_icon = "mdi:brain"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_model"

    @property
    def native_value(self):
        return self.coordinator.data.get("model", "unknown")


class OpenClawTokensInSensor(OpenClawBaseSensor):
    _attr_translation_key = "tokens_in"
    _attr_icon = "mdi:chip"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "tokens"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_tokens_in"

    @property
    def native_value(self):
        return self.coordinator.data.get("tokens_in", 0)


class OpenClawTokensOutSensor(OpenClawBaseSensor):
    _attr_translation_key = "tokens_out"
    _attr_icon = "mdi:chip"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "tokens"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_tokens_out"

    @property
    def native_value(self):
        return self.coordinator.data.get("tokens_out", 0)


class OpenClawLastUpdatedSensor(OpenClawBaseSensor):
    _attr_translation_key = "last_updated"
    _attr_icon = "mdi:clock-outline"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_last_updated"

    @property
    def native_value(self):
        return self.coordinator.data.get("last_updated", "unknown")


class OpenClawCostSensor(OpenClawBaseSensor):
    _attr_translation_key = "cost"
    _attr_icon = "mdi:currency-usd"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "USD"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_cost"

    @property
    def native_value(self):
        return self.coordinator.data.get("estimated_cost_usd", 0.0)
