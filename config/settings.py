from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass(frozen=True)
class Settings:
    polygon_api_key: str
    alpaca_api_key: str
    alpaca_secret_key: str
    alpaca_base_url: str
    gmail_address: str
    gmail_app_password: str
    notify_email: str
    symbol: str = "SPY"
    timeframe: str = "1h"
    lookback_bars: int = 250
    atr_choppy_threshold: float = 0.005
    min_confidence: int = 65


settings = Settings(
    polygon_api_key=os.environ.get("POLYGON_API_KEY", ""),
    alpaca_api_key=os.environ.get("ALPACA_API_KEY", ""),
    alpaca_secret_key=os.environ.get("ALPACA_SECRET_KEY", ""),
    alpaca_base_url=os.environ.get("ALPACA_BASE_URL", "https://data.alpaca.markets"),
    gmail_address=os.environ.get("GMAIL_ADDRESS", ""),
    gmail_app_password=os.environ.get("GMAIL_APP_PASSWORD", ""),
    notify_email=os.environ.get("NOTIFY_EMAIL", "jayjayumar1990@gmail.com"),
)
