"""OpenClaw Integration for Home Assistant."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OpenClawCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

ICON_SRC = Path(__file__).parent / "brand" / "openclaw.svg"
ICON_DST_DIR = Path("/config/www/openclaw")
ICON_DST = ICON_DST_DIR / "openclaw.svg"


def _copy_icon() -> None:
    """Copy the OpenClaw icon to /config/www/openclaw/ for Lovelace use."""
    try:
        ICON_DST_DIR.mkdir(parents=True, exist_ok=True)
        if not ICON_DST.exists() or ICON_SRC.stat().st_mtime > ICON_DST.stat().st_mtime:
            shutil.copy2(ICON_SRC, ICON_DST)
            _LOGGER.debug("OpenClaw icon copied to %s", ICON_DST)
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Could not copy OpenClaw icon: %s", err)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenClaw from a config entry."""
    await hass.async_add_executor_job(_copy_icon)

    coordinator = OpenClawCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
