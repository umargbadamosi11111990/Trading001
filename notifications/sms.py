import requests
import structlog

from config.settings import settings
from signals.evaluator import Signal

log = structlog.get_logger()


def format_sms(signal: Signal) -> str:
    lines = [
        "=== SPY A++ SIGNAL ===",
        f"Dir:   {signal.direction}",
        f"Entry: ${signal.entry:.2f}",
        f"SL:    ${signal.stop_loss:.2f}",
        f"TP:    ${signal.take_profit:.2f}",
        f"R:R    1:{signal.rr_ratio:.1f}",
        f"Score: {signal.confidence}/100",
        "---",
    ]
    lines.extend(signal.reasoning)
    return "\n".join(lines)


def send_signal_sms(signal: Signal) -> str:
    body = format_sms(signal)
    resp = requests.post(
        "https://textbelt.com/text",
        data={
            "phone": settings.sms_to_number,
            "message": body,
            "key": settings.textbelt_key,
        },
        timeout=15,
    )
    resp.raise_for_status()
    result = resp.json()
    if not result.get("success"):
        raise RuntimeError(f"TextBelt error: {result.get('error')} | quotaRemaining={result.get('quotaRemaining')}")
    log.info("sms.sent", to=settings.sms_to_number, direction=signal.direction, quota=result.get("quotaRemaining"))
    return str(result.get("textId", ""))
