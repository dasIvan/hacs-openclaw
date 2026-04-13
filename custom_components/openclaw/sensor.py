"""Sensor platform for OpenClaw."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
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
        OpenClawLastActiveSensor(coordinator, entry),
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
    """idle / busy state of the agent."""

    _attr_translation_key = "status"
    _attr_icon = "mdi:robot"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_status"

    @property
    def native_value(self) -> str:
        return (self.coordinator.data or {}).get("state", "idle")


class OpenClawModelSensor(OpenClawBaseSensor):
    """Currently active AI model."""

    _attr_translation_key = "model"
    _attr_icon = "mdi:brain"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_model"

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get("model")


class OpenClawLastActiveSensor(OpenClawBaseSensor):
    """Timestamp of last agent activity."""

    _attr_translation_key = "last_active"
    _attr_icon = "mdi:clock-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_last_active"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("last_active")
