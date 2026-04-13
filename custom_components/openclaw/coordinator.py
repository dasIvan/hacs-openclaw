"""DataUpdateCoordinator for OpenClaw."""
from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_AGENT_NAME, CONF_HOST, CONF_PORT, CONF_TOKEN, DEFAULT_AGENT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class OpenClawCoordinator(DataUpdateCoordinator):
    """Fetch data from OpenClaw Gateway via sessions_list."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.token = entry.data[CONF_TOKEN]
        self.agent_name = entry.data.get(CONF_AGENT_NAME, DEFAULT_AGENT_NAME)
        self.base_url = f"http://{self.host}:{self.port}"

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _async_update_data(self) -> dict:
        """Fetch status from OpenClaw using sessions_list only."""
        result = {
            "connected": False,
            "state": "idle",
            "model": None,
            "last_active": None,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/tools/invoke",
                    json={"tool": "sessions_list", "args": {}},
                    headers=self._headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result["connected"] = True
                        self._parse_sessions(data, result)
                    else:
                        raise UpdateFailed(f"HTTP {resp.status}")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error: {err}") from err

        return result

    def _parse_sessions(self, data: dict, result: dict) -> None:
        """Extract state, model, last_active from sessions_list response."""
        sessions = (
            data.get("result", {}).get("details", {}).get("sessions") or []
        )
        if not sessions:
            return

        # Most recently updated session
        s = sorted(sessions, key=lambda x: x.get("updatedAt", 0), reverse=True)[0]

        result["model"] = s.get("model") or None
        result["state"] = "busy" if s.get("status") == "running" else "idle"

        updated_ms = s.get("updatedAt")
        if updated_ms:
            result["last_active"] = datetime.fromtimestamp(
                updated_ms / 1000, tz=timezone.utc
            )

    async def async_ping(self) -> bool:
        """Test connectivity to OpenClaw Gateway."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/tools/invoke",
                    json={"tool": "sessions_list", "args": {}},
                    headers=self._headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    return resp.status == 200
        except aiohttp.ClientError:
            return False
