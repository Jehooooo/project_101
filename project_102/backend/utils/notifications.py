"""
Notification Utility — DMMMSU-SLUC Disaster Monitoring System
==============================================================
Delivers alerts to ALL active users when an incident is submitted
or its status changes.

Channels
--------
1. Email  — Gmail SMTP (free, requires App Password)
2. Telegram Bot — 100% free, carrier-agnostic, unlimited messages.
   All staff join one Telegram group; the bot posts there.

Dynamic contacts
----------------
Emails and phones are always fetched live from the database.
Nothing is hardcoded.

Reliability
-----------
Every delivery attempt is individually logged.
Transient failures are retried (up to MAX_RETRIES times) with a
short delay so one bad recipient never blocks the rest.
"""

import logging
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Tuple

import requests

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

# ---------------------------------------------------------------------------
# Email / SMTP config  (set in backend/.env)
# ---------------------------------------------------------------------------
SMTP_SERVER   = os.environ.get("SMTP_SERVER",   "smtp.gmail.com")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
FROM_EMAIL    = os.environ.get("FROM_EMAIL",    "") or SMTP_USERNAME

# ---------------------------------------------------------------------------
# Telegram Bot config  (FREE — set in backend/.env)
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

# ---------------------------------------------------------------------------
# Startup validation — catch the "bot ID used as chat ID" mistake immediately
# ---------------------------------------------------------------------------
if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    _bot_numeric_id = TELEGRAM_BOT_TOKEN.split(":")[0]
    if TELEGRAM_CHAT_ID == _bot_numeric_id:
        logger.error(
            "TELEGRAM MISCONFIGURED ✗ — TELEGRAM_CHAT_ID (%s) is the bot's own user ID.\n"
            "  Bots cannot send messages to themselves (HTTP 403).\n"
            "  Fix: set TELEGRAM_CHAT_ID to a real user or group chat ID.\n"
            "  Option A (personal): open @userinfobot in Telegram → it replies with your ID.\n"
            "  Option B (group):    add bot to a group, send a message, then visit:\n"
            "    https://api.telegram.org/bot%s/getUpdates\n"
            "  Look for  \"chat\":{\"id\": -XXXXXXXXX}  (group IDs are negative numbers).",
            TELEGRAM_CHAT_ID, TELEGRAM_BOT_TOKEN,
        )
elif TELEGRAM_BOT_TOKEN and not TELEGRAM_CHAT_ID:
    logger.warning(
        "TELEGRAM MISCONFIGURED — TELEGRAM_CHAT_ID is empty in .env.\n"
        "  Set it to your personal Telegram user ID (via @userinfobot)\n"
        "  or to a group chat ID (negative number from /getUpdates)."
    )

# ---------------------------------------------------------------------------
# Retry policy
# ---------------------------------------------------------------------------
MAX_RETRIES   = 2
RETRY_DELAY_S = 3


# ===========================================================================
# Helpers — HTML builders
# ===========================================================================

def _status_color(status: str) -> str:
    return {"Pending": "#dc2626", "In Progress": "#d97706", "Solved": "#059669"}.get(status, "#6b7280")


def _html_new_incident(incident) -> str:
    reporter = incident.reporter.full_name if incident.reporter else "Unknown"
    return f"""
<html>
<body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;max-width:650px;margin:auto;">
  <div style="background:#dc2626;padding:20px 30px;border-radius:8px 8px 0 0;">
    <h2 style="color:#fff;margin:0;">&#128680; New Incident Reported</h2>
  </div>
  <div style="border:1px solid #e5e7eb;border-top:none;padding:30px;border-radius:0 0 8px 8px;">
    <p>A new incident has been submitted and requires your attention.</p>
    <table style="border-collapse:collapse;width:100%;">
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;width:35%;">Incident ID</td>
          <td style="padding:8px;border:1px solid #ddd;">{incident.incident_id}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Status</td>
          <td style="padding:8px;border:1px solid #ddd;color:#dc2626;font-weight:bold;">Pending</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Location</td>
          <td style="padding:8px;border:1px solid #ddd;">{incident.location}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Cause</td>
          <td style="padding:8px;border:1px solid #ddd;">{incident.cause}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Date</td>
          <td style="padding:8px;border:1px solid #ddd;">{incident.date.strftime('%B %d, %Y')}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Reported By</td>
          <td style="padding:8px;border:1px solid #ddd;">{reporter}</td></tr>
    </table>
    <hr style="margin:25px 0;border:none;border-top:1px solid #e5e7eb;">
    <p style="font-size:12px;color:#666;">
      Automated message — DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System.
      Do not reply to this email.
    </p>
  </div>
</body>
</html>"""


def _html_status_update(incident) -> str:
    color = _status_color(incident.status)
    return f"""
<html>
<body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;max-width:650px;margin:auto;">
  <div style="background:#1e40af;padding:20px 30px;border-radius:8px 8px 0 0;">
    <h2 style="color:#fff;margin:0;">&#128203; Incident Status Updated</h2>
  </div>
  <div style="border:1px solid #e5e7eb;border-top:none;padding:30px;border-radius:0 0 8px 8px;">
    <p>The status of an incident has been updated.</p>
    <table style="border-collapse:collapse;width:100%;">
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;width:35%;">Incident ID</td>
          <td style="padding:8px;border:1px solid #ddd;">{incident.incident_id}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">New Status</td>
          <td style="padding:8px;border:1px solid #ddd;color:{color};font-weight:bold;">{incident.status}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Location</td>
          <td style="padding:8px;border:1px solid #ddd;">{incident.location}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;font-weight:bold;">Date</td>
          <td style="padding:8px;border:1px solid #ddd;">{incident.date.strftime('%B %d, %Y')}</td></tr>
    </table>
    <hr style="margin:25px 0;border:none;border-top:1px solid #e5e7eb;">
    <p style="font-size:12px;color:#666;">
      Automated message — DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System.
      Do not reply to this email.
    </p>
  </div>
</body>
</html>"""


def _html_test(to_email: str) -> str:
    return f"""
<html>
<body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;max-width:650px;margin:auto;">
  <div style="background:#059669;padding:20px 30px;border-radius:8px 8px 0 0;">
    <h2 style="color:#fff;margin:0;">&#10003; Notification Test Successful</h2>
  </div>
  <div style="border:1px solid #e5e7eb;border-top:none;padding:30px;border-radius:0 0 8px 8px;">
    <p>This is a test notification from the DMMMSU-SLUC Disaster Monitoring System.</p>
    <p>If you are reading this, email notifications are working correctly for:</p>
    <p style="font-size:16px;font-weight:bold;background:#f0fdf4;padding:12px 20px;
              border-radius:6px;border-left:4px solid #059669;">{to_email}</p>
    <p>No action is required.</p>
    <hr style="margin:25px 0;border:none;border-top:1px solid #e5e7eb;">
    <p style="font-size:12px;color:#666;">
      Automated message — DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System.
    </p>
  </div>
</body>
</html>"""


# ===========================================================================
# Helpers — DB contact retrieval
# ===========================================================================

def _get_all_contacts() -> Tuple[List[str], List[str]]:
    """
    Fetch emails and phone numbers of ALL active users from the DB.
    Imported lazily to avoid circular imports at module load time.
    Returns (emails, phones).
    """
    from models.user import User  # noqa: PLC0415

    users  = User.query.filter_by(is_active=True).all()
    emails = [u.email for u in users if u.email]
    phones = [u.phone for u in users if u.phone]

    logger.info(
        "DB contacts fetched — %d email(s): %s | %d phone(s): %s",
        len(emails), emails, len(phones), phones,
    )
    return emails, phones


# ===========================================================================
# Email delivery
# ===========================================================================

def _send_email_batch(subject: str, html_body: str, recipients: List[str]) -> bool:
    """
    Send one HTML email to all *recipients* in a single SMTP session.
    Retries on transient errors; aborts immediately on auth failure.
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.error(
            "EMAIL NOT SENT — SMTP credentials missing in .env.\n"
            "  Set SMTP_USERNAME and SMTP_PASSWORD (Gmail App Password).\n"
            "  How to get an App Password:\n"
            "    1. Enable 2-Step Verification: https://myaccount.google.com/security\n"
            "    2. Visit: https://myaccount.google.com/apppasswords\n"
            "    3. Create password for 'Mail' → paste the 16-char code into .env"
        )
        return False

    if not recipients:
        logger.warning("EMAIL SKIPPED — no recipients found in DB.")
        return False

    msg              = MIMEMultipart("alternative")
    msg["Subject"]   = subject
    msg["From"]      = FROM_EMAIL
    msg["To"]        = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            logger.info("Email attempt %d — connecting to %s:%d …", attempt, SMTP_SERVER, SMTP_PORT)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as srv:
                srv.ehlo()
                srv.starttls()
                srv.ehlo()
                srv.login(SMTP_USERNAME, SMTP_PASSWORD)
                srv.sendmail(FROM_EMAIL, recipients, msg.as_string())

            logger.info("EMAIL SENT ✓ — %d recipient(s): %s", len(recipients), recipients)
            return True

        except smtplib.SMTPAuthenticationError as exc:
            logger.error(
                "EMAIL FAILED — Authentication error: %s\n"
                "  Your SMTP_PASSWORD in .env is likely your regular Gmail password.\n"
                "  Gmail REQUIRES an App Password for SMTP access.\n"
                "  Steps:\n"
                "    1. Go to https://myaccount.google.com/apppasswords\n"
                "    2. Create an App Password (Mail / Other)\n"
                "    3. Replace SMTP_PASSWORD in backend/.env with the 16-char code\n"
                "  Current value length: %d chars (App Passwords are always 16 chars)",
                exc, len(SMTP_PASSWORD),
            )
            return False  # Auth errors never succeed on retry

        except smtplib.SMTPException as exc:
            logger.warning("Email attempt %d SMTP error: %s", attempt, exc)
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_DELAY_S)
            else:
                logger.error("EMAIL FAILED — all %d attempts exhausted.", MAX_RETRIES + 1)
                return False

        except OSError as exc:
            logger.warning("Email attempt %d network error: %s", attempt, exc)
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_DELAY_S)
            else:
                logger.error("EMAIL FAILED — all %d attempts exhausted.", MAX_RETRIES + 1)
                return False

    return False


# ===========================================================================
# Telegram Bot delivery  (FREE — no carrier required)
# ===========================================================================

def _send_telegram(message: str) -> bool:
    """
    Post *message* to the configured Telegram group/channel.
    Completely free, carrier-agnostic.  Works with DITO, Globe, Smart, etc.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning(
            "TELEGRAM SKIPPED — TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env.\n"
            "  Setup (free, 5 minutes):\n"
            "    1. Open Telegram → search @BotFather → /newbot\n"
            "    2. Copy the bot token → set as TELEGRAM_BOT_TOKEN in .env\n"
            "    3. Add the bot to your staff group/channel\n"
            "    4. Send a message in the group, then visit:\n"
            "       https://api.telegram.org/bot<TOKEN>/getUpdates\n"
            "    5. Copy the chat id → set as TELEGRAM_CHAT_ID in .env"
        )
        return False

    url     = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
    }

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                logger.info("TELEGRAM SENT ✓")
                return True
            logger.warning(
                "Telegram attempt %d — HTTP %d: %s",
                attempt, resp.status_code, resp.text,
            )
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_DELAY_S)
            else:
                logger.error("TELEGRAM FAILED — all attempts exhausted.")
                return False

        except requests.RequestException as exc:
            logger.warning("Telegram attempt %d network error: %s", attempt, exc)
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_DELAY_S)
            else:
                logger.error("TELEGRAM FAILED — all attempts exhausted.")
                return False

    return False


# ===========================================================================
# Public API — called from app.py
# ===========================================================================

def send_email_notification(incident, status_update: bool = False) -> bool:
    """Email ALL active users about a new incident or a status change."""
    emails, _ = _get_all_contacts()

    if status_update:
        subject  = f"[DMMMSU] Status Update: {incident.incident_id} → {incident.status}"
        html     = _html_status_update(incident)
    else:
        subject  = f"[DMMMSU] New Incident Reported: {incident.incident_id}"
        html     = _html_new_incident(incident)

    return _send_email_batch(subject, html, emails)


def send_sms_notification(incident, status_update: bool = False) -> bool:
    """
    Send a Telegram message to the staff group (free, carrier-agnostic).
    Name kept as 'send_sms_notification' for compatibility with app.py.
    """
    reporter = incident.reporter.full_name if incident.reporter else "Unknown"

    if status_update:
        msg = (
            f"📋 <b>Incident Status Updated</b>\n"
            f"ID: <code>{incident.incident_id}</code>\n"
            f"New Status: <b>{incident.status}</b>\n"
            f"Location: {incident.location}\n"
            f"Date: {incident.date.strftime('%B %d, %Y')}"
        )
    else:
        msg = (
            f"🚨 <b>New Incident Reported</b>\n"
            f"ID: <code>{incident.incident_id}</code>\n"
            f"Location: {incident.location}\n"
            f"Cause: {incident.cause}\n"
            f"Reported by: {reporter}\n"
            f"Status: <b>Pending</b>"
        )

    return _send_telegram(msg)


def send_test_notification(to_email: Optional[str] = None) -> dict:
    """
    Send a test email (and Telegram) to verify configuration.
    If *to_email* is provided, sends only to that address.
    Otherwise fetches all active user emails from DB.

    Returns a dict with keys: email_ok, telegram_ok, recipients, errors.
    """
    results = {"email_ok": False, "telegram_ok": False, "recipients": [], "errors": []}

    # ── Determine recipients ──────────────────────────────────────────
    if to_email:
        recipients = [to_email]
    else:
        try:
            recipients, _ = _get_all_contacts()
        except Exception as exc:
            results["errors"].append(f"DB fetch failed: {exc}")
            recipients = []

    results["recipients"] = recipients

    # ── Test email ────────────────────────────────────────────────────
    if recipients:
        # Send individual test emails so each address is in the "To:" field
        any_ok = False
        for addr in recipients:
            ok = _send_email_batch(
                subject  = "[DMMMSU] Test Notification — Email is Working ✓",
                html_body = _html_test(addr),
                recipients = [addr],
            )
            if ok:
                any_ok = True
            else:
                results["errors"].append(f"Email failed for {addr}")
        results["email_ok"] = any_ok
    else:
        results["errors"].append("No email recipients available.")

    # ── Test Telegram ─────────────────────────────────────────────────
    results["telegram_ok"] = _send_telegram(
        "✅ <b>DMMMSU Test Notification</b>\n"
        "Telegram notifications are working correctly!"
    )

    return results


def send_password_reset_email(user, reset_token: str) -> bool:
    """Send a password-reset email to a specific user."""
    subject  = "Password Reset — DMMMSU-SLUC Disaster Monitoring System"
    html     = f"""
<html>
<body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;max-width:600px;margin:auto;">
  <div style="background:#1e40af;padding:20px 30px;border-radius:8px 8px 0 0;">
    <h2 style="color:#fff;margin:0;">&#128273; Password Reset Request</h2>
  </div>
  <div style="border:1px solid #e5e7eb;border-top:none;padding:30px;border-radius:0 0 8px 8px;">
    <p>Hello {user.first_name},</p>
    <p>Your password reset token:</p>
    <p style="font-size:20px;font-weight:bold;background:#f3f4f6;padding:14px 20px;
              border-radius:6px;letter-spacing:3px;text-align:center;">{reset_token}</p>
    <p style="color:#666;font-size:12px;">This token expires in 1 hour.</p>
    <p>If you did not request this, ignore this email.</p>
    <hr style="margin:25px 0;border:none;border-top:1px solid #e5e7eb;">
    <p style="font-size:12px;color:#666;">
      Automated message — DMMMSU-SLUC Disaster Monitoring System.
    </p>
  </div>
</body>
</html>"""
    return _send_email_batch(subject, html, [user.email])
