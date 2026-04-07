"""
Standalone test script for DMMMSU notification system.
Run from the backend directory:  python test_notifications.py

Tests:
  1. SMTP connection & authentication  (email)
  2. Sends a real test email to SMTP_USERNAME
  3. Telegram Bot API connectivity
  4. Telegram test message
"""

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load .env from the same directory as this script
from pathlib import Path
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())
    print(f"✓ Loaded .env from {env_path}\n")
else:
    print(f"✗ .env not found at {env_path}\n")

# ── Read config ──────────────────────────────────────────────────────────────
SMTP_SERVER        = os.environ.get("SMTP_SERVER",   "smtp.gmail.com")
SMTP_PORT          = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME      = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD      = os.environ.get("SMTP_PASSWORD", "")
FROM_EMAIL         = os.environ.get("FROM_EMAIL",    "") or SMTP_USERNAME
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID",   "")

# Colour helpers
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg): print(f"  {RED}✗{RESET} {msg}")
def warn(msg): print(f"  {YELLOW}!{RESET} {msg}")
def info(msg): print(f"  {CYAN}→{RESET} {msg}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Config check
# ─────────────────────────────────────────────────────────────────────────────
print(f"{BOLD}═══════════════════════════════════════════════════{RESET}")
print(f"{BOLD}  DMMMSU Notification System — Diagnostic Test     {RESET}")
print(f"{BOLD}═══════════════════════════════════════════════════{RESET}\n")

print(f"{BOLD}[1] Configuration Check{RESET}")

is_placeholder_pwd   = "APP_PASSWORD" in SMTP_PASSWORD or "HERE" in SMTP_PASSWORD
is_placeholder_tg    = "HERE" in TELEGRAM_BOT_TOKEN or "HERE" in TELEGRAM_CHAT_ID
is_regular_pwd_maybe = SMTP_PASSWORD and len(SMTP_PASSWORD) != 16 and not is_placeholder_pwd

info(f"SMTP server    : {SMTP_SERVER}:{SMTP_PORT}")
info(f"SMTP username  : {SMTP_USERNAME or '(not set)'}")
info(f"SMTP password  : {'(not set)' if not SMTP_PASSWORD else '(placeholder)' if is_placeholder_pwd else f'***** ({len(SMTP_PASSWORD)} chars)'}")
info(f"From email     : {FROM_EMAIL or '(not set)'}")
info(f"Telegram token : {'(not set)' if not TELEGRAM_BOT_TOKEN else '(placeholder)' if is_placeholder_pwd else TELEGRAM_BOT_TOKEN[:10] + '...'}")
info(f"Telegram chat  : {TELEGRAM_CHAT_ID or '(not set)'}")
print()

if not SMTP_USERNAME or not SMTP_PASSWORD or is_placeholder_pwd:
    fail("SMTP credentials not configured.")
    print(f"\n  {YELLOW}How to fix:{RESET}")
    print("    1. Go to  https://myaccount.google.com/apppasswords")
    print("    2. Create an App Password for 'Mail'")
    print("    3. Open backend/.env and set:")
    print(f"         SMTP_PASSWORD=<your 16-char app password>")
    print()
elif is_regular_pwd_maybe:
    warn(f"SMTP_PASSWORD is {len(SMTP_PASSWORD)} chars. Gmail App Passwords are always exactly 16 chars.")
    warn("If this is your regular Gmail password, authentication WILL fail.")
    warn("Get an App Password at: https://myaccount.google.com/apppasswords")
    print()
else:
    ok("SMTP credentials look configured.")
    print()

# ─────────────────────────────────────────────────────────────────────────────
# 2. SMTP connection test
# ─────────────────────────────────────────────────────────────────────────────
email_ok = False
print(f"{BOLD}[2] SMTP Connection Test{RESET}")

if not SMTP_USERNAME or not SMTP_PASSWORD or is_placeholder_pwd:
    warn("Skipping — credentials not set.")
else:
    try:
        info(f"Connecting to {SMTP_SERVER}:{SMTP_PORT} ...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as srv:
            srv.ehlo()
            ok("TCP connection established.")
            srv.starttls()
            ok("TLS handshake successful.")
            srv.ehlo()
            srv.login(SMTP_USERNAME, SMTP_PASSWORD)
            ok(f"Authentication successful for  {SMTP_USERNAME}")
            email_ok = True
    except smtplib.SMTPAuthenticationError as e:
        fail(f"Authentication FAILED: {e}")
        print()
        print(f"  {YELLOW}Root cause:{RESET} Gmail rejected the password.")
        print(f"  {YELLOW}Current password length:{RESET} {len(SMTP_PASSWORD)} chars")
        print(f"  {YELLOW}App Passwords are always exactly 16 chars (no spaces).{RESET}")
        print()
        print("  Action required:")
        print("    1. Visit https://myaccount.google.com/apppasswords")
        print("    2. Ensure 2-Step Verification is ENABLED first")
        print("    3. Click 'Create App Password'")
        print("    4. Copy the 16-char code (example: abcd efgh ijkl mnop)")
        print("    5. Remove the spaces, paste into backend/.env:")
        print("         SMTP_PASSWORD=abcdefghijklmnop")
        print("    6. Re-run this script to verify")
    except OSError as e:
        fail(f"Network error: {e}")
        print("  Check your internet connection.")
    except Exception as e:
        fail(f"Unexpected error: {type(e).__name__}: {e}")
print()

# ─────────────────────────────────────────────────────────────────────────────
# 3. Send test email
# ─────────────────────────────────────────────────────────────────────────────
print(f"{BOLD}[3] Send Test Email{RESET}")

if not email_ok:
    warn("Skipping — SMTP not authenticated.")
else:
    recipient = SMTP_USERNAME
    info(f"Sending test email to {recipient} ...")
    try:
        msg              = MIMEMultipart("alternative")
        msg["Subject"]   = "[DMMMSU] ✓ Email Notification Test — Working!"
        msg["From"]      = FROM_EMAIL
        msg["To"]        = recipient
        msg.attach(MIMEText(f"""
<html>
<body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;">
  <div style="background:#059669;padding:20px 30px;border-radius:8px 8px 0 0;">
    <h2 style="color:#fff;margin:0;">&#10003; Email Notifications Are Working!</h2>
  </div>
  <div style="border:1px solid #e5e7eb;border-top:none;padding:30px;border-radius:0 0 8px 8px;">
    <p>This test email confirms that the DMMMSU-SLUC notification system
       is correctly configured and can deliver emails.</p>
    <p><strong>Sent to:</strong> {recipient}</p>
    <p>No action required. This was an automated test.</p>
    <hr style="margin:20px 0;border:none;border-top:1px solid #e5e7eb;">
    <p style="font-size:12px;color:#666;">DMMMSU-SLUC Disaster Monitoring System</p>
  </div>
</body>
</html>
""", "html"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as srv:
            srv.ehlo(); srv.starttls(); srv.ehlo()
            srv.login(SMTP_USERNAME, SMTP_PASSWORD)
            srv.sendmail(FROM_EMAIL, [recipient], msg.as_string())
        ok(f"Test email sent to {recipient}  ← Check your inbox!")
    except Exception as e:
        fail(f"Failed to send: {e}")
print()

# ─────────────────────────────────────────────────────────────────────────────
# 4. Telegram test
# ─────────────────────────────────────────────────────────────────────────────
print(f"{BOLD}[4] Telegram Bot Test{RESET}")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or is_placeholder_tg:
    warn("Skipping — Telegram not configured.")
    print()
    print("  To set up free Telegram notifications (takes ~5 min):")
    print("    1. Open Telegram → search @BotFather → /newbot")
    print("    2. Copy the bot token → set TELEGRAM_BOT_TOKEN in .env")
    print("    3. Create a staff group, add your bot")
    print("    4. Send a message in the group, then visit:")
    print("       https://api.telegram.org/bot<TOKEN>/getUpdates")
    print("    5. Copy chat id (negative number) → set TELEGRAM_CHAT_ID in .env")
else:
    try:
        import requests
        info("Sending Telegram test message ...")
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id":    TELEGRAM_CHAT_ID,
                "text":       "✅ <b>DMMMSU Test</b>\nTelegram notifications are working!",
                "parse_mode": "HTML",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            ok("Telegram message sent!  ← Check your group/channel.")
        else:
            fail(f"Telegram API error {resp.status_code}: {resp.text}")
    except ImportError:
        fail("requests library not installed. Run: pip install requests")
    except Exception as e:
        fail(f"Error: {e}")
print()

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print(f"{BOLD}═══════════════════════════════════════════════════{RESET}")
print(f"{BOLD}  Summary{RESET}")
print(f"{BOLD}═══════════════════════════════════════════════════{RESET}")
if email_ok:
    ok("Email  — WORKING ✓")
else:
    fail("Email  — NOT WORKING  (see [2] and [3] above for fix)")
if not TELEGRAM_BOT_TOKEN or is_placeholder_tg:
    warn("Telegram — NOT CONFIGURED (optional but free)")
print()
