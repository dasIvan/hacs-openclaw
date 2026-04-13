# OpenClaw for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A Home Assistant integration for [OpenClaw](https://openclaw.ai) — monitor your AI agent and build custom status cards directly in HA.

## Features

- **Status sensor** — idle / busy state of your agent
- **Model sensor** — which AI model is currently active
- **Last Active sensor** — timestamp of last agent activity (native HA time formatting)
- **Connected binary sensor** — is the OpenClaw Gateway reachable?
- **Config flow** — set up via UI, no YAML needed
- **Custom agent name** — name it whatever you want (Aris, Jarvis, HAL, ...)

## Installation via HACS

1. Open HACS → Integrations
2. Click the three dots → **Custom repositories**
3. Add: `https://github.com/dasIvan/hacs-openclaw` → Category: **Integration**
4. Install **OpenClaw AI**
5. Restart Home Assistant
6. Go to **Settings → Integrations → Add → OpenClaw AI**

## Configuration

| Field | Description |
|-------|-------------|
| Agent Name | How you call your assistant (e.g. Aris, Jarvis) |
| Host | IP address of your OpenClaw server |
| Port | Gateway port (default: `18789`) |
| Token | Your Gateway token — find it in `~/.openclaw/openclaw.json` under `gateway.auth.token` |

## Entities

After setup, the following entities are created (names based on your configured agent name):

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.<name>_status` | Sensor | `idle` or `busy` |
| `sensor.<name>_model` | Sensor | Active AI model |
| `sensor.<name>_last_active` | Sensor | Last activity timestamp |
| `binary_sensor.<name>_connected` | Binary Sensor | Gateway reachable |

## Lovelace Status Card

A ready-to-use card template is included in [`lovelace-card-example.yaml`](lovelace-card-example.yaml).

It requires [`custom:button-card`](https://github.com/custom-cards/button-card) (installable via HACS → Frontend).

Features:
- Dark gradient background (blue = online, grey = offline)
- Agent icon (lobster logo)
- Status badge — green (idle) / red (busy)
- Active model name
- Last activity time

To use it:
1. Install `button-card` via HACS → Frontend
2. Copy your `icon.png` to `/config/www/openclaw/icon.png`
3. Copy the card YAML into your Lovelace dashboard (raw config editor)
4. Adjust entity IDs to match your agent name

## Sending Messages via Automation

Use a `rest_command` to send messages to your agent from any HA automation:

```yaml
rest_command:
  agent_send:
    url: "http://<your-host>:18789/tools/invoke"
    method: POST
    headers:
      Authorization: "Bearer <your-token>"
      Content-Type: "application/json"
    payload: '{"tool":"sessions_send","args":{"sessionKey":"main","message":"{{ message }}","timeoutSeconds":30}}'
```

Then call it in an automation:

```yaml
service: rest_command.agent_send
data:
  message: "Good morning!"
```

## Requirements

- Home Assistant 2024.1.0+
- OpenClaw with Gateway running on your local network (`openclaw gateway start`)
