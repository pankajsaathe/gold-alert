#!/usr/bin/env python3
"""
========================================================
  GOLD PRICE ALERT — WhatsApp via Twilio
  Checks live gold price every minute and sends a
  WhatsApp message when your threshold is triggered.
========================================================

SETUP (one-time):
  pip install requests twilio

RUN:
  python gold_alert.py
"""

import time
import logging
import requests
from datetime import datetime
from twilio.rest import Client
import config  # loads config.py from same folder

# ── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Twilio client ─────────────────────────────────────────
twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)


# ── Fetch gold price ─────────────────────────────────────
def get_gold_price() -> float | None:
    """
    Fetches the current gold spot price (USD per troy ounce).
    Uses gold-api.com — completely free, no API key, no rate limits.
    Falls back to a second source if the first fails.
    Returns None only if both sources fail.
    """
    sources = [
        {
            "url": "https://api.gold-api.com/price/XAU",
            "parse": lambda d: float(d["price"]),
            "name": "gold-api.com"
        },
        {
            "url": "https://api.metalpriceapi.com/v1/latest?api_key=demo&base=XAU&currencies=USD",
            "parse": lambda d: round(1.0 / float(d["rates"]["USD"]), 2),
            "name": "metalpriceapi.com (fallback)"
        },
    ]
    for source in sources:
        try:
            resp = requests.get(source["url"], timeout=10)
            resp.raise_for_status()
            data = resp.json()
            price = source["parse"](data)
            log.debug(f"Price fetched from {source['name']}")
            return price
        except Exception as exc:
            log.warning(f"Could not fetch from {source['name']}: {exc}")
    return None


# ── Send WhatsApp alert ───────────────────────────────────
def send_whatsapp_alert(price: float, direction: str) -> None:
    arrow = "📉" if direction == "below" else "📈"
    condition = (
        f"dropped to or below ${config.ALERT_PRICE:,.2f}"
        if direction == "below"
        else f"risen to or above ${config.ALERT_PRICE:,.2f}"
    )
    body = (
        f"{arrow} *GOLD PRICE ALERT* {arrow}\n\n"
        f"Gold has {condition}.\n"
        f"Current price: *${price:,.2f} / oz*\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"— Gold Alert Bot 🤖"
    )
    twilio_client.messages.create(
        body=body,
        from_=config.TWILIO_FROM,
        to=config.YOUR_PHONE,
    )
    log.info(f"✅ WhatsApp alert sent! Gold at ${price:,.2f}")


# ── Should alert trigger? ─────────────────────────────────
def should_alert(price: float) -> str | None:
    """
    Returns 'below', 'above', or None based on config.ALERT_DIRECTION.
    """
    d = config.ALERT_DIRECTION
    if d == "below_or_equal" and price <= config.ALERT_PRICE:
        return "below"
    if d == "above_or_equal" and price >= config.ALERT_PRICE:
        return "above"
    if d == "both":
        if price <= config.ALERT_PRICE:
            return "below"
        if price >= config.ALERT_PRICE:
            return "above"
    return None


# ── Main loop ─────────────────────────────────────────────
def main():
    log.info("=" * 55)
    log.info("  Gold Price Alert Bot — Started")
    log.info(f"  Target price  : ${config.ALERT_PRICE:,.2f}")
    log.info(f"  Direction     : {config.ALERT_DIRECTION}")
    log.info(f"  Check interval: every {config.CHECK_INTERVAL}s")
    log.info(f"  Alert cooldown: {config.ALERT_COOLDOWN}s")
    log.info("=" * 55)

    last_alert_time = 0  # epoch seconds of last sent alert

    while True:
        price = get_gold_price()

        if price is None:
            log.warning("Skipping this check — price unavailable.")
        else:
            log.info(f"Gold price: ${price:,.2f}/oz  (target: ${config.ALERT_PRICE:,.2f})")
            direction = should_alert(price)

            if direction:
                now = time.time()
                cooldown_passed = (now - last_alert_time) >= config.ALERT_COOLDOWN

                if cooldown_passed:
                    try:
                        send_whatsapp_alert(price, direction)
                        last_alert_time = now
                    except Exception as exc:
                        log.error(f"Failed to send WhatsApp message: {exc}")
                else:
                    remaining = int(config.ALERT_COOLDOWN - (now - last_alert_time))
                    log.info(f"⏳ Alert suppressed — cooldown active ({remaining}s remaining)")
            else:
                log.info("No alert triggered.")

        time.sleep(config.CHECK_INTERVAL)


if __name__ == "__main__":
    main()
