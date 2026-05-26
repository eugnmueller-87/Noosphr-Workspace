import imaplib
import email
import time
import os
import requests
import anthropic
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

WEBHOOKS = {
    "business": os.getenv("SLACK_WEBHOOK_BUSINESS"),
    "support": os.getenv("SLACK_WEBHOOK_SUPPORT"),
    "spam": os.getenv("SLACK_WEBHOOK_SPAM"),
}

CLASSIFY_PROMPT = """You are an email classifier for Noosphr, an AI technology company (info@Noosphr.de).
Noosphr builds AI-powered products and services. Relevant topics include AI, automation, software, agents, APIs, and tech.

Classify the following email into exactly one of these categories:
- business: Partnerships, collaborations, offers, deals, invoices, contracts, proposals, meetings, sales inquiries, networking, job applications, press, investors, AI-related inquiries, tech collaborations
- support: Customer questions, technical issues, bug reports, help requests, complaints, feedback about a product or service
- spam: Newsletters, promotions, automated notifications, irrelevant cold outreach, social media alerts, system emails

Respond with ONLY one word: business, support, or spam.

From: {sender}
Subject: {subject}
Body: {body}"""


def decode_str(value):
    if value is None:
        return ""
    parts = decode_header(value)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def classify(sender, subject, body):
    if not ANTHROPIC_API_KEY:
        print("[WARN] No ANTHROPIC_API_KEY set, falling back to keyword routing")
        return classify_fallback(sender, subject, body)

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": CLASSIFY_PROMPT.format(
                    sender=sender,
                    subject=subject,
                    body=body[:1000]
                )
            }]
        )
        result = message.content[0].text.strip().lower()
        if result in ("business", "support", "spam"):
            print(f"[AI] Classified as #{result}: {subject}")
            return result
        print(f"[WARN] Unexpected AI response '{result}', falling back")
        return classify_fallback(sender, subject, body)

    except Exception as e:
        print(f"[ERROR] Claude classification failed: {e}, falling back to keywords")
        return classify_fallback(sender, subject, body)


def classify_fallback(sender, subject, body):
    text = f"{sender} {subject} {body}".lower()
    support_kw = ["help", "issue", "problem", "support", "ticket", "error", "broken", "not working", "bug", "question"]
    business_kw = ["invoice", "contract", "partnership", "proposal", "quote", "order", "payment", "billing",
                   "business", "collaboration", "opportunity", "meeting", "offer", "deal", "project"]
    if any(kw in text for kw in support_kw):
        return "support"
    if any(kw in text for kw in business_kw):
        return "business"
    return "spam"


def post_to_slack(channel, sender, subject, body_preview):
    webhook = WEBHOOKS[channel]
    reply_email = sender.split("<")[-1].replace(">", "").strip() if "<" in sender else sender.strip()
    reply_subject = f"Re: {subject}"
    mailto = f"mailto:{reply_email}?subject={requests.utils.quote(reply_subject)}"

    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*New email → #{channel}*\n*From:* {sender}\n*Subject:* {subject}\n*Preview:* {body_preview[:300]}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": f"✉ Reply to {reply_email}"},
                        "url": mailto,
                        "style": "primary"
                    }
                ]
            },
            {"type": "divider"}
        ]
    }
    try:
        r = requests.post(webhook, json=payload, timeout=10)
        r.raise_for_status()
        print(f"[OK] Posted to #{channel}: {subject}")
    except Exception as e:
        print(f"[ERROR] Slack post failed: {e}")


def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_payload(decode=True).decode("utf-8", errors="replace")
                except Exception:
                    return ""
    else:
        try:
            return msg.get_payload(decode=True).decode("utf-8", errors="replace")
        except Exception:
            return ""
    return ""


def check_emails():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        _, data = mail.search(None, "UNSEEN")
        email_ids = data[0].split()

        if not email_ids:
            print("[INFO] No new emails.")
            mail.logout()
            return

        for eid in email_ids:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            sender = decode_str(msg.get("From"))
            subject = decode_str(msg.get("Subject"))
            body = get_body(msg)

            channel = classify(sender, subject, body)
            post_to_slack(channel, sender, subject, body)

            mail.store(eid, "+FLAGS", "\\Seen")

        mail.logout()

    except Exception as e:
        print(f"[ERROR] Email check failed: {e}")


def main():
    print(f"[START] Email router running — polling every {POLL_INTERVAL}s")
    if ANTHROPIC_API_KEY:
        print("[INFO] Claude AI classification enabled")
    else:
        print("[WARN] Claude AI classification disabled — using keyword fallback")
    while True:
        check_emails()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
