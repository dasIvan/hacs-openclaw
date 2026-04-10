"""Button platform for OpenClaw."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import OpenClawCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: OpenClawCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OpenClawPingButton(coordinator, entry)])


class OpenClawPingButton(ButtonEntity):
    _attr_translation_key = "ping"
    _attr_icon = "mdi:connection"
    _attr_has_entity_name = True

    def __init__(self, coordinator: OpenClawCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._entry = entry

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_ping"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "OpenClaw AI",
            "manufacturer": "OpenClaw",
            "model": "AI Gateway",
        }

    async def async_press(self) -> None:
        """Test connectivity to Gateway."""
        await self._coordinator.async_ping()
        await self._coordinator.async_request_refresh()
