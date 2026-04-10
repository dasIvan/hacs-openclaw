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
        OpenClawTokensInSensor(coordinator, entry),
        OpenClawTokensOutSensor(coordinator, entry),
        OpenClawModelSensor(coordinator, entry),
        OpenClawLastUpdatedSensor(coordinator, entry),
    ])


class OpenClawBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: OpenClawCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "OpenClaw",
            "manufacturer": "OpenClaw",
            "model": "AI Gateway",
        }


class OpenClawStatusSensor(OpenClawBaseSensor):
    _attr_name = "OpenClaw Status"
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
            "queue": d.get("queue"),
            "context_pct": d.get("context_pct"),
            "last_updated": d.get("last_updated"),
        }


class OpenClawTokensInSensor(OpenClawBaseSensor):
    _attr_name = "OpenClaw Tokens In"
    _attr_icon = "mdi:transfer-down"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "tokens"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_tokens_in"

    @property
    def native_value(self):
        return self.coordinator.data.get("tokens_in", 0)


class OpenClawTokensOutSensor(OpenClawBaseSensor):
    _attr_name = "OpenClaw Tokens Out"
    _attr_icon = "mdi:transfer-up"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "tokens"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_tokens_out"

    @property
    def native_value(self):
        return self.coordinator.data.get("tokens_out", 0)


class OpenClawModelSensor(OpenClawBaseSensor):
    _attr_name = "OpenClaw Model"
    _attr_icon = "mdi:brain"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_model"

    @property
    def native_value(self):
        return self.coordinator.data.get("model", "unknown")


class OpenClawLastUpdatedSensor(OpenClawBaseSensor):
    _attr_name = "OpenClaw Last Active"
    _attr_icon = "mdi:clock-outline"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_last_updated"

    @property
    def native_value(self):
        return self.coordinator.data.get("last_updated", "unknown")
