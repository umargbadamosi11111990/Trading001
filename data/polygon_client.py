import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential


class PolygonClient:
    BASE_URL = "https://api.polygon.io"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def get_ohlc_bars(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
        timespan: str = "hour",
        multiplier: int = 1,
        limit: int = 5000,
    ) -> pd.DataFrame:
        url = (
            f"{self.BASE_URL}/v2/aggs/ticker/{symbol}/range"
            f"/{multiplier}/{timespan}/{from_date}/{to_date}"
        )
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": limit,
            "apiKey": self.api_key,
        }
        rows = []
        while url:
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            rows.extend(data.get("results", []))
            url = data.get("next_url")
            params = {}

        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df["timestamp"] = pd.to_datetime(df["t"], unit="ms", utc=True)
        df = df.rename(
            columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
        )
        return df[["timestamp", "open", "high", "low", "close", "volume"]].set_index("timestamp")
