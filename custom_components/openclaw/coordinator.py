"""DataUpdateCoordinator for OpenClaw."""
from __future__ import annotations

import logging
import re
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, CONF_PORT, CONF_TOKEN, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class OpenClawCoordinator(DataUpdateCoordinator):
    """Fetch data from OpenClaw Gateway."""

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
        self.base_url = f"http://{self.host}:{self.port}"

    async def _async_update_data(self) -> dict:
        """Fetch status from OpenClaw."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"tool": "session_status", "args": {}}
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                }
                async with session.post(
                    f"{self.base_url}/tools/invoke",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP {resp.status}")
                    data = await resp.json()

            if not data.get("ok"):
                raise UpdateFailed("OpenClaw returned error")

            raw = data["result"]["content"][0]["text"]
            return self._parse_status(raw)

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error: {err}") from err

    def _parse_status(self, text: str) -> dict:
        """Parse status text into structured data."""
        result = {
            "raw": text,
            "state": "idle",
            "model": None,
            "tokens_in": 0,
            "tokens_out": 0,
            "context_pct": 0,
            "last_updated": None,
            "session": None,
            "queue": None,
        }

        # Model
        m = re.search(r"Model:\s*([\w/\.\-]+)", text)
        if m:
            result["model"] = m.group(1)

        # Tokens  e.g. "19k in / 274 out"
        m = re.search(r"Tokens:\s*([\d\.]+)(k?)\s*in\s*/\s*([\d\.]+)(k?)\s*out", text)
        if m:
            def to_int(val, suffix):
                n = float(val)
                return int(n * 1000) if suffix == "k" else int(n)
            result["tokens_in"] = to_int(m.group(1), m.group(2))
            result["tokens_out"] = to_int(m.group(3), m.group(4))

        # Context %
        m = re.search(r"Context:.*?\((\d+)%\)", text)
        if m:
            result["context_pct"] = int(m.group(1))

        # Session + last updated
        m = re.search(r"Session:\s*([\w:]+)\s*[•·]\s*updated\s*(.+?)(?:\n|$)", text)
        if m:
            result["session"] = m.group(1)
            result["last_updated"] = m.group(2).strip()

        # Queue → state
        m = re.search(r"Queue:\s*(\w+)", text)
        if m:
            q = m.group(1).lower()
            result["queue"] = q
            result["state"] = "busy" if q in ("run", "running", "processing") else "idle"

        return result

    async def async_send_message(self, message: str) -> bool:
        """Send a message to OpenClaw."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "tool": "sessions_send",
                    "args": {
                        "sessionKey": "main",
                        "message": message,
                        "timeoutSeconds": 60,
                    },
                }
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                }
                async with session.post(
                    f"{self.base_url}/tools/invoke",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=65),
                ) as resp:
                    return resp.status == 200
        except aiohttp.ClientError:
            return False
