"""DataUpdateCoordinator for OpenClaw."""
from __future__ import annotations

import datetime
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

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _invoke(self, session: aiohttp.ClientSession, tool: str, args: dict = {}) -> dict:
        """Call /tools/invoke and return parsed result."""
        async with session.post(
            f"{self.base_url}/tools/invoke",
            json={"tool": tool, "args": args},
            headers=self._headers,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"HTTP {resp.status} on tool {tool}")
            return await resp.json()

    async def _async_update_data(self) -> dict:
        """Fetch status from OpenClaw."""
        try:
            async with aiohttp.ClientSession() as session:
                sessions_resp = await self._invoke(session, "sessions_list", {})
                status_resp = await self._invoke(session, "session_status", {})
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error: {err}") from err

        # Parse status text for context/queue info
        raw = status_resp.get("result", {}).get("content", [{}])[0].get("text", "")
        result = self._parse_status_text(raw)

        # Enrich from sessions_list (more reliable)
        sessions = (
            sessions_resp.get("result", {}).get("details", {}).get("sessions") or []
        )
        if sessions:
            # Pick the most recently updated session
            s = sorted(sessions, key=lambda x: x.get("updatedAt", 0), reverse=True)[0]

            result["model"] = s.get("model") or result["model"]
            result["tokens_in"] = s.get("totalTokens", result["tokens_in"])
            result["estimated_cost_usd"] = round(s.get("estimatedCostUsd", 0), 4)

            # Status from session: "running" → busy, anything else → idle
            session_status = s.get("status", "done")
            result["state"] = "busy" if session_status == "running" else "idle"

            updated_ms = s.get("updatedAt")
            if updated_ms:
                dt = datetime.datetime.fromtimestamp(
                    updated_ms / 1000, tz=datetime.timezone.utc
                )
                result["last_updated"] = dt.strftime("%Y-%m-%d %H:%M UTC")

        return result

    def _parse_status_text(self, text: str) -> dict:
        """Parse session_status text for supplementary info."""
        result = {
            "raw": text,
            "state": "idle",
            "model": None,
            "tokens_in": 0,
            "tokens_out": 0,
            "context_pct": 0,
            "last_updated": None,
            "session": None,
            "estimated_cost_usd": 0.0,
        }

        # Model
        m = re.search(r"Model:\s*([\w/\.\-]+)", text)
        if m:
            result["model"] = m.group(1)

        # Tokens e.g. "19k in / 274 out"
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

        # Session key
        m = re.search(r"Session:\s*([\w:]+)", text)
        if m:
            result["session"] = m.group(1)

        return result

    async def async_ping(self) -> bool:
        """Test connectivity to OpenClaw Gateway."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/tools/invoke",
                    json={"tool": "session_status", "args": {}},
                    headers=self._headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    return resp.status == 200
        except aiohttp.ClientError:
            return False

    async def async_send_message(self, message: str) -> bool:
        """Send a message to OpenClaw main session."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/tools/invoke",
                    json={
                        "tool": "sessions_send",
                        "args": {
                            "sessionKey": "main",
                            "message": message,
                            "timeoutSeconds": 60,
                        },
                    },
                    headers=self._headers,
                    timeout=aiohttp.ClientTimeout(total=65),
                ) as resp:
                    return resp.status == 200
        except aiohttp.ClientError:
            return False
