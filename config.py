import os

# ============================================================
#   GOLD ALERT - CONFIGURATION
#   Values are read from Railway environment variables.
#   For local testing, you can hardcode values below as fallback.
# ============================================================

# --- Twilio WhatsApp Credentials ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "YOUR_TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN",  "YOUR_TWILIO_AUTH_TOKEN")

# --- Phone Numbers ---
TWILIO_FROM = os.environ.get("TWILIO_FROM", "whatsapp:+14155238886")  # Twilio sandbox default
YOUR_PHONE  = os.environ.get("YOUR_PHONE",  "whatsapp:+31XXXXXXXXX")  # Your number with country code

# --- Alert Settings (easily editable in Railway dashboard) ---
ALERT_PRICE     = float(os.environ.get("ALERT_PRICE",     "4200"))   # USD threshold
CHECK_INTERVAL  = int(os.environ.get("CHECK_INTERVAL",    "60"))     # Seconds between checks
ALERT_COOLDOWN  = int(os.environ.get("ALERT_COOLDOWN",    "3600"))   # Seconds between repeat alerts

# --- Alert Direction ---
# "below_or_equal"  → alert when price <= ALERT_PRICE
# "above_or_equal"  → alert when price >= ALERT_PRICE
# "both"            → alert in either direction
ALERT_DIRECTION = os.environ.get("ALERT_DIRECTION", "below_or_equal")
