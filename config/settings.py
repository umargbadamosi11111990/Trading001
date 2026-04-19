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
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_number: str
    twilio_to_number: str
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
    twilio_account_sid=os.environ.get("TWILIO_ACCOUNT_SID", ""),
    twilio_auth_token=os.environ.get("TWILIO_AUTH_TOKEN", ""),
    twilio_from_number=os.environ.get("TWILIO_FROM_NUMBER", ""),
    twilio_to_number=os.environ.get("TWILIO_TO_NUMBER", "+14106604533"),
)
