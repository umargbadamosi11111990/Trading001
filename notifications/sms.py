import structlog
from twilio.rest import Client

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
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    body = format_sms(signal)
    message = client.messages.create(
        body=body,
        from_=settings.twilio_from_number,
        to=settings.twilio_to_number,
    )
    log.info("sms.sent", sid=message.sid, to=settings.twilio_to_number, direction=signal.direction)
    return message.sid
