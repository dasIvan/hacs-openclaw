"""Button platform for OpenClaw — send a message to Aris."""
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
    _attr_name = "OpenClaw Ping"
    _attr_icon = "mdi:send"

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
            "name": "OpenClaw",
            "manufacturer": "OpenClaw",
            "model": "AI Gateway",
        }

    async def async_press(self) -> None:
        await self._coordinator.async_send_message("Status-Check von Home Assistant")
