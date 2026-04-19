import structlog
from datetime import datetime, timedelta, timezone

import pandas as pd

from config.settings import settings
from data.alpaca_client import AlpacaClient
from data.polygon_client import PolygonClient

log = structlog.get_logger()


class DataFeed:
    def __init__(self):
        self.polygon = PolygonClient(settings.polygon_api_key)
        self.alpaca = AlpacaClient(
            settings.alpaca_api_key,
            settings.alpaca_secret_key,
            settings.alpaca_base_url,
        )

    def get_bars(self, lookback_bars: int = 250) -> pd.DataFrame:
        to_date = datetime.now(timezone.utc)
        # Over-fetch calendar days: ~6.5 trading hours/day, 1.5x safety buffer
        calendar_days = int(lookback_bars / 6.5 * 1.5) + 14
        from_date = to_date - timedelta(days=calendar_days)

        try:
            df = self.polygon.get_ohlc_bars(
                symbol=settings.symbol,
                from_date=from_date.strftime("%Y-%m-%d"),
                to_date=to_date.strftime("%Y-%m-%d"),
            )
            if df.empty:
                raise ValueError("Polygon returned empty data")
            log.info("data_feed.polygon_success", bars=len(df))
        except Exception as exc:
            log.warning("data_feed.polygon_failed", error=str(exc), fallback="alpaca")
            df = self.alpaca.get_ohlc_bars(
                symbol=settings.symbol,
                start=from_date.isoformat(),
                end=to_date.isoformat(),
            )
            if df.empty:
                raise RuntimeError("Both Polygon and Alpaca returned empty data")
            log.info("data_feed.alpaca_success", bars=len(df))

        return df.tail(lookback_bars)
