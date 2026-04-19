import pandas as pd
import pandas_ta as ta


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches OHLCV DataFrame with all required technical indicators.
    Requires at least 210 rows for EMA 200 to be fully warmed up.

    Added columns:
        ema_50, ema_200, rsi_14,
        macd, macd_signal, macd_hist,
        stoch_k, stoch_d,
        atr_14,
        vol_ma_20, vol_spike (bool)
    """
    df = df.copy()

    df["ema_50"] = ta.ema(df["close"], length=50)
    df["ema_200"] = ta.ema(df["close"], length=200)

    df["rsi_14"] = ta.rsi(df["close"], length=14)

    macd_df = ta.macd(df["close"], fast=12, slow=26, signal=9)
    df["macd"] = macd_df["MACD_12_26_9"]
    df["macd_signal"] = macd_df["MACDs_12_26_9"]
    df["macd_hist"] = macd_df["MACDh_12_26_9"]

    stoch_df = ta.stoch(df["high"], df["low"], df["close"], k=14, d=3, smooth_k=3)
    df["stoch_k"] = stoch_df["STOCHk_14_3_3"]
    df["stoch_d"] = stoch_df["STOCHd_14_3_3"]

    df["atr_14"] = ta.atr(df["high"], df["low"], df["close"], length=14)

    df["vol_ma_20"] = df["volume"].rolling(window=20).mean()
    df["vol_spike"] = df["volume"] > df["vol_ma_20"]

    return df
