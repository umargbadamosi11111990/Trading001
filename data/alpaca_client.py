import pandas as pd
import requests


class AlpacaClient:
    def __init__(self, api_key: str, secret_key: str, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key,
        }

    def get_ohlc_bars(
        self,
        symbol: str,
        start: str,
        end: str,
        timeframe: str = "1Hour",
        limit: int = 1000,
    ) -> pd.DataFrame:
        url = f"{self.base_url}/v2/stocks/{symbol}/bars"
        params = {
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": limit,
            "feed": "iex",
            "adjustment": "all",
        }
        rows = []
        while True:
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            rows.extend(data.get("bars", []))
            token = data.get("next_page_token")
            if not token:
                break
            params["page_token"] = token

        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df["timestamp"] = pd.to_datetime(df["t"], utc=True)
        df = df.rename(
            columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
        )
        return df[["timestamp", "open", "high", "low", "close", "volume"]].set_index("timestamp")
