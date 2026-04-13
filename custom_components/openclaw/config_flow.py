"""Config flow for OpenClaw integration."""
from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_AGENT_NAME,
    CONF_HOST,
    CONF_PORT,
    CONF_TOKEN,
    DEFAULT_AGENT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)


class OpenClawConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenClaw."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            token = user_input[CONF_TOKEN]
            agent_name = user_input[CONF_AGENT_NAME].strip() or DEFAULT_AGENT_NAME

            # Test connection
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"http://{host}:{port}/tools/invoke",
                        json={"tool": "sessions_list", "args": {}},
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                        },
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 401:
                            errors["base"] = "invalid_auth"
                        elif resp.status != 200:
                            errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"

            if not errors:
                await self.async_set_unique_id(f"openclaw_{host}_{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=agent_name,
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_TOKEN: token,
                        CONF_AGENT_NAME: agent_name,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_AGENT_NAME, default=DEFAULT_AGENT_NAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_TOKEN): str,
                }
            ),
            errors=errors,
        )
