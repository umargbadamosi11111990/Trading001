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
    sms_to_number: str
    textbelt_key: str
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
    sms_to_number=os.environ.get("SMS_TO_NUMBER", "2404592841"),
    textbelt_key=os.environ.get("TEXTBELT_KEY", "textbelt"),
)
