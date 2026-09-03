"""
Email delivery for feedback submissions.

Feedback is always written to data/feedback.jsonl first (see
frontend/feedback_widget.py) -- that write must never depend on network
access or credentials. Emailing it out is a best-effort second step on
top of that, controlled entirely by environment variables so no
credentials are hardcoded here:

    SMTP_HOST        e.g. smtp.office365.com  (required to enable email)
    SMTP_PORT        default 587
    SMTP_USERNAME    mailbox / account used to send
    SMTP_PASSWORD    password or app password for that account
    SMTP_USE_TLS     "true"/"false", default "true" (STARTTLS)
    FEEDBACK_EMAIL_FROM   default: SMTP_USERNAME
    FEEDBACK_EMAIL_TO     default: rby4kor@bosch.com

If SMTP_HOST / SMTP_USERNAME / SMTP_PASSWORD aren't set, send_feedback_email
returns (False, "smtp_not_configured") without raising -- the feedback
widget treats that as "saved locally, not emailed" rather than an error,
since most local/dev runs won't have a mailbox configured.
"""
import os
import smtplib
from email.message import EmailMessage

DEFAULT_TO = "rby4kor@bosch.com"


def _smtp_settings():
    return {
        "host": os.environ.get("SMTP_HOST"),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "username": os.environ.get("SMTP_USERNAME"),
        "password": os.environ.get("SMTP_PASSWORD"),
        "use_tls": os.environ.get("SMTP_USE_TLS", "true").strip().lower() != "false",
        "from_addr": os.environ.get("FEEDBACK_EMAIL_FROM") or os.environ.get("SMTP_USERNAME"),
        "to_addr": os.environ.get("FEEDBACK_EMAIL_TO", DEFAULT_TO),
    }


def is_email_configured() -> bool:
    s = _smtp_settings()
    return bool(s["host"] and s["username"] and s["password"])


def send_feedback_email(entry: dict):
    """
    Sends one feedback entry by email. Returns (ok: bool, detail: str) and
    never raises -- callers should treat a False return as "not sent,
    already logged" rather than crash the submit flow over it.
    """
    settings = _smtp_settings()
    if not (settings["host"] and settings["username"] and settings["password"]):
        return False, "smtp_not_configured"

    mood_label = {
        "great": "Going well",
        "mixed": "Mixed / unsure",
        "uncomfortable": "Something's off",
    }.get(entry.get("mood"), entry.get("mood", "unknown"))

    msg = EmailMessage()
    msg["Subject"] = f"[Bosch AI Intelligence Workspace] Feedback — {mood_label}"
    msg["From"] = settings["from_addr"]
    msg["To"] = settings["to_addr"]
    msg.set_content(
        "New feedback submitted in the Bosch AI Intelligence Workspace.\n\n"
        f"Mood: {mood_label}\n"
        f"Page: {entry.get('page', 'unknown')}\n"
        f"Submitted: {entry.get('ts', 'unknown')}\n"
        f"Reply-to contact: {entry.get('contact') or 'not provided'}\n\n"
        "Message:\n"
        f"{entry.get('message', '')}\n\n"
        f"— Entry ID {entry.get('id', 'unknown')}, logged to data/feedback.jsonl\n"
    )

    try:
        with smtplib.SMTP(settings["host"], settings["port"], timeout=10) as server:
            if settings["use_tls"]:
                server.starttls()
            server.login(settings["username"], settings["password"])
            server.send_message(msg)
        return True, "sent"
    except Exception as e:
        return False, str(e)
