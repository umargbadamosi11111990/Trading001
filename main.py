import logging

import structlog

from config.settings import settings
from data.feed import DataFeed
from indicators.compute import compute_indicators
from notifications.sms import send_signal_sms
from scheduler.runner import build_scheduler
from signals.evaluator import evaluate

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
logging.basicConfig(level=logging.INFO)
log = structlog.get_logger()

feed = DataFeed()


def run_cycle():
    log.info("cycle.start", symbol=settings.symbol)
    try:
        df = feed.get_bars(lookback_bars=settings.lookback_bars)
        df = compute_indicators(df)
        signal = evaluate(df)

        if signal is not None:
            log.info("cycle.aplus_detected", confidence=signal.confidence, direction=signal.direction)
            try:
                sid = send_signal_sms(signal)
                log.info("cycle.sms_dispatched", sid=sid)
            except Exception as sms_err:
                log.error("cycle.sms_failed", error=str(sms_err))
        else:
            log.info("cycle.no_signal")

    except Exception as exc:
        log.error("cycle.error", error=str(exc), exc_info=True)


if __name__ == "__main__":
    log.info("system.starting", symbol=settings.symbol, timeframe=settings.timeframe)
    scheduler = build_scheduler(run_cycle)
    scheduler.start()
