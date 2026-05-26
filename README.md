# Noosphr Workspace

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)
![Claude AI](https://img.shields.io/badge/Claude%20AI-Powered-orange?style=flat&logo=anthropic&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-Integration-4A154B?style=flat&logo=slack&logoColor=white)
![VPS](https://img.shields.io/badge/VPS-Hetzner-D50C2D?style=flat&logo=hetzner&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

Internal AI tooling for **Noosphr** — an AI technology company building intelligent products and automation systems.

This workspace contains production tools that power day-to-day operations at Noosphr.

---

## Projects

### 📧 Email Router

> AI-powered email triage that routes incoming emails from `info@Noosphr.de` into the right Slack channels automatically.

| Feature | Detail |
|---|---|
| Classification | Claude AI (Haiku) — understands context, not just keywords |
| Channels | `#business`, `#support`, `#spam` |
| Reply | One-click reply button in every Slack notification |
| Inbox | Hostinger IMAP (`imap.hostinger.com`) |
| Hosting | Systemd service on Hetzner VPS — runs 24/7 |
| Fallback | Keyword-based routing if Claude API is unavailable |

**How it works:**
1. Polls `info@Noosphr.de` every 60 seconds via IMAP
2. Sends each new email to Claude AI for classification
3. Posts to the correct Slack channel with sender, subject, preview and a reply button

→ [View code](email-router/)

---

## Setup

```bash
git clone https://github.com/eugnmueller-87/Noosphr-Workspace.git
cd Noosphr-Workspace/email-router
cp .env.example .env
# Fill in your credentials in .env
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python3 email_router.py
```

---

## Stack

![Hostinger](https://img.shields.io/badge/Hostinger-Email-673DE6?style=flat)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude%20Haiku-CC785C?style=flat)
![Slack](https://img.shields.io/badge/Slack-Webhooks-4A154B?style=flat&logo=slack&logoColor=white)
![Python](https://img.shields.io/badge/Python-imaplib-3776AB?style=flat&logo=python&logoColor=white)
![Systemd](https://img.shields.io/badge/Systemd-Service-000000?style=flat)

---

*Built and maintained by [Eugen Mueller](https://github.com/eugnmueller-87) — Noosphr*
