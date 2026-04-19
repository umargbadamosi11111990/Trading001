import pytz
import structlog
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

log = structlog.get_logger()

ET = pytz.timezone("America/New_York")


def build_scheduler(job_fn) -> BlockingScheduler:
    """
    Registers job_fn to fire 1 minute after each 1-hour SPY candle close.
    SPY candles close at :30 each hour during the session; we fire at :31.
    Hours covered: 10:31, 11:31, 12:31, 13:31, 14:31, 15:31, 16:31 ET (Mon-Fri).
    """
    scheduler = BlockingScheduler(timezone=ET)
    trigger = CronTrigger(
        day_of_week="mon-fri",
        hour="10,11,12,13,14,15,16",
        minute=31,
        timezone=ET,
    )
    scheduler.add_job(
        job_fn,
        trigger=trigger,
        id="spy_hourly_cycle",
        misfire_grace_time=120,
    )
    log.info("scheduler.registered", trigger="hourly :31 ET, Mon-Fri")
    return scheduler
