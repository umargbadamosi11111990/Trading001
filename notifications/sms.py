import smtplib
import structlog
from email.mime.text import MIMEText

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
    msg = MIMEText(body)
    msg["From"] = settings.gmail_address
    msg["To"] = settings.sms_gateway
    msg["Subject"] = ""

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.gmail_address, settings.gmail_app_password)
        server.sendmail(settings.gmail_address, settings.sms_gateway, msg.as_string())

    log.info("sms.sent", to=settings.sms_gateway, direction=signal.direction)
    return "ok"
