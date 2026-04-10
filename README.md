# OpenClaw for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A Home Assistant integration for [OpenClaw](https://openclaw.ai) — monitor your AI assistant and send messages directly from HA.

## Features

- **Status sensor** — idle / busy state
- **Token sensors** — track API usage (tokens in/out)
- **Model sensor** — which AI model is active
- **Last active sensor** — when Aris last responded
- **Ping button** — send a message to your OpenClaw agent
- **Config flow** — set up via UI, no YAML needed

## Installation via HACS

1. Open HACS → Integrations
2. Click the three dots → Custom repositories
3. Add: `https://github.com/dasIvan/hacs-openclaw` → Category: Integration
4. Install **OpenClaw**
5. Restart Home Assistant
6. Go to Settings → Integrations → Add → **OpenClaw**

## Configuration

| Field | Description |
|-------|-------------|
| Host | IP address of your OpenClaw server |
| Port | Gateway port (default: `18789`) |
| Token | Your Gateway token from `openclaw.json` |

## Lovelace Card Example

```yaml
type: entities
title: Aris (OpenClaw)
entities:
  - entity: sensor.openclaw_status
    name: Status
  - entity: sensor.openclaw_model
    name: Model
  - entity: sensor.openclaw_last_active
    name: Last Active
  - entity: sensor.openclaw_tokens_in
    name: Tokens In
  - entity: sensor.openclaw_tokens_out
    name: Tokens Out
  - entity: button.openclaw_ping
    name: Ping Aris
```

## Sending Messages via Automation

```yaml
service: button.press
target:
  entity_id: button.openclaw_ping
```

Or use `rest_command` for custom messages:

```yaml
rest_command:
  aris_send:
    url: "http://<your-host>:18789/tools/invoke"
    method: POST
    headers:
      Authorization: "Bearer <your-token>"
      Content-Type: "application/json"
    payload: '{"tool":"sessions_send","args":{"sessionKey":"main","message":"{{ message }}","timeoutSeconds":30}}'
```

## Requirements

- Home Assistant 2024.1.0+
- OpenClaw with Gateway running on your local network
