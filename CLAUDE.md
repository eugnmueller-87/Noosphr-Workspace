# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository

Internal AI tooling for **Noosphr** (`info@Noosphr.de`) — an AI technology company. Currently contains one production service: `email-router`.

## email-router

### Setup

```bash
cd email-router
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env  # fill in credentials
```

### Run

```bash
venv/bin/python3 email_router.py
```

### Deploy to VPS (187.124.14.81)

```bash
scp email_router.py .env requirements.txt root@187.124.14.81:/opt/email-router/
ssh root@187.124.14.81 "systemctl restart email-router"
```

### Check logs on VPS

```bash
ssh root@187.124.14.81 "journalctl -fu email-router"
```

### Service management on VPS

The service runs as a systemd unit at `/etc/systemd/system/email-router.service`. It uses a virtualenv at `/opt/email-router/venv/`. The `EnvironmentFile` in the service file points to `/opt/email-router/.env` — always redeploy `.env` alongside code changes if credentials change.

## Architecture

Single-file service (`email_router.py`) with a polling loop:

1. **IMAP poll** — connects to `imap.hostinger.com:993` every 60s, fetches UNSEEN messages
2. **Classification** — sends each email to `claude-haiku-4-5-20251001` via Anthropic API. Falls back to keyword matching if `ANTHROPIC_API_KEY` is missing or the API call fails
3. **Slack post** — posts to one of three Incoming Webhook URLs (`#business`, `#support`, `#spam`) using Slack Block Kit with a mailto reply button and an Open Inbox button

### Classification routing

- **business** — partnerships, proposals, AI inquiries, press, investors, meetings
- **support** — customer issues, bugs, help requests
- **spam** — newsletters, promotions, automated notifications, unrecognised outreach

The Claude prompt is `CLASSIFY_PROMPT` at the top of `email_router.py` — edit this to tune classification behaviour. Body is truncated to 1000 chars before being sent to the API.

### Environment variables

| Variable | Purpose |
|---|---|
| `EMAIL_ADDRESS` | `info@Noosphr.de` |
| `EMAIL_PASSWORD` | Hostinger email password |
| `IMAP_HOST` | `imap.hostinger.com` |
| `IMAP_PORT` | `993` |
| `SLACK_WEBHOOK_BUSINESS` | Slack webhook for `#business` |
| `SLACK_WEBHOOK_SUPPORT` | Slack webhook for `#support` |
| `SLACK_WEBHOOK_SPAM` | Slack webhook for `#spam` |
| `ANTHROPIC_API_KEY` | Claude API key — disables AI classification if missing |
| `POLL_INTERVAL` | Seconds between IMAP polls (default: 60) |
