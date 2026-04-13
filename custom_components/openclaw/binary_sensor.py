"""Binary sensor platform for OpenClaw — connectivity."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    async_add_entities([OpenClawConnectedSensor(coordinator, entry)])


class OpenClawConnectedSensor(CoordinatorEntity, BinarySensorEntity):
    """True when OpenClaw Gateway is reachable."""

    _attr_has_entity_name = True
    _attr_translation_key = "connected"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:lan-connect"

    def __init__(self, coordinator: OpenClawCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_connected"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data and self.coordinator.data.get("connected"))

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self.coordinator.agent_name,
            "manufacturer": "OpenClaw",
            "model": "AI Gateway",
        }
