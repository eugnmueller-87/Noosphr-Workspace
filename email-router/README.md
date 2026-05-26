# Email Router

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)
![Claude AI](https://img.shields.io/badge/Claude%20AI-Powered-orange?style=flat&logo=anthropic&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-Integration-4A154B?style=flat&logo=slack&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

Automatically routes incoming emails from a Hostinger inbox into the right Slack channels using Claude AI classification. Built for the [Noosphr](https://noosphr.de) workspace.

## How it works

1. Polls your email inbox via IMAP every 60 seconds
2. Sends each new email to Claude AI for classification
3. Posts it to the correct Slack channel with a one-click reply button

## Routing

| Channel | Email types |
|---|---|
| `#business` | Partnerships, proposals, deals, AI inquiries, press, investors |
| `#support` | Customer issues, bug reports, help requests, feedback |
| `#spam` | Newsletters, promotions, automated notifications |

## Features

- Claude AI-powered classification (falls back to keywords if API unavailable)
- One-click **Reply** button in every Slack notification
- Runs as a systemd service on a VPS (auto-restarts on failure)
- Supports any Hostinger email account

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/eugnmueller-87/Noosphr-Workspace.git
cd Noosphr-Workspace/email-router
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- Hostinger email address and password
- Slack incoming webhook URLs (one per channel)
- Anthropic API key

### 3. Install dependencies

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### 4. Run

```bash
venv/bin/python3 email_router.py
```

### 5. Deploy as a service (VPS)

```bash
cp email-router.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable email-router
systemctl start email-router
```

## Requirements

- Python 3.12+
- Hostinger email with IMAP enabled
- Slack workspace with Incoming Webhooks configured
- Anthropic API key
