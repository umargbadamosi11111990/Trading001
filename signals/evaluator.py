from dataclasses import dataclass
from typing import Literal, Optional

import pandas as pd
import structlog

from config.settings import settings
from signals.scoring import (
    Direction,
    compute_confidence,
    score_price_structure,
    score_rsi,
    score_stoch,
)

log = structlog.get_logger()


@dataclass
class Signal:
    direction: Direction
    entry: float
    stop_loss: float
    take_profit: float
    rr_ratio: float
    confidence: int
    reasoning: list


def evaluate(df: pd.DataFrame) -> Optional[Signal]:
    """
    Evaluates the last completed candle against A++ criteria.
    Returns Signal if all 8 hard gates pass and confidence >= min_confidence, else None.
    """
    if len(df) < 210:
        log.warning("evaluator.insufficient_data", rows=len(df))
        return None

    row = df.iloc[-1]

    # Gate 1: ATR choppiness filter
    if row["atr_14"] <= 0 or pd.isna(row["atr_14"]):
        return None
    atr_ratio = row["atr_14"] / row["close"]
    if atr_ratio < settings.atr_choppy_threshold:
        log.debug("evaluator.choppy_market", atr_ratio=f"{atr_ratio:.4f}")
        return None

    # Gate 2: EMA alignment determines direction
    if pd.isna(row["ema_50"]) or pd.isna(row["ema_200"]):
        return None
    if row["ema_50"] > row["ema_200"]:
        direction: Direction = "LONG"
    elif row["ema_50"] < row["ema_200"]:
        direction = "SHORT"
    else:
        return None

    # Gate 3: RSI not disqualified
    if pd.isna(row["rsi_14"]) or score_rsi(row, direction) == 0.0:
        log.debug("evaluator.rsi_disqualified", rsi=row["rsi_14"], direction=direction)
        return None

    # Gate 4: MACD histogram in signal direction
    if pd.isna(row["macd_hist"]):
        return None
    if direction == "LONG" and row["macd_hist"] <= 0:
        return None
    if direction == "SHORT" and row["macd_hist"] >= 0:
        return None

    # Gate 5: Stochastic not extreme against direction
    if pd.isna(row["stoch_k"]) or score_stoch(row, direction) == 0.0:
        return None

    # Gate 6: Volume above 20-bar average
    if not row["vol_spike"]:
        log.debug("evaluator.volume_below_average")
        return None

    # Determine key levels from the 20 candles preceding current bar
    lookback = 20
    window = df.iloc[-(lookback + 1):-1]
    recent_high = window["high"].max()
    recent_low = window["low"].min()
    atr = row["atr_14"]
    entry = float(row["close"])

    if direction == "LONG":
        stop_loss = recent_low - (atr * 0.5)
        stop_dist = entry - stop_loss
        take_profit = entry + (stop_dist * 2.5)
    else:
        stop_loss = recent_high + (atr * 0.5)
        stop_dist = stop_loss - entry
        take_profit = entry - (stop_dist * 2.5)

    # Gate 7: Minimum R:R 1:2
    if stop_dist <= 0:
        return None
    rr_ratio = abs(take_profit - entry) / stop_dist
    if rr_ratio < 2.0:
        return None

    # Gate 8: Meaningful price structure
    if score_price_structure(row, direction, recent_high, recent_low) < 5.0:
        log.debug("evaluator.weak_price_structure")
        return None

    confidence = compute_confidence(row, direction, rr_ratio, recent_high, recent_low)

    if confidence < settings.min_confidence:
        log.info(
            "evaluator.signal_below_threshold",
            confidence=confidence,
            direction=direction,
        )
        return None

    ema_gap_pct = abs(row["ema_50"] - row["ema_200"]) / row["ema_200"] * 100
    vol_ratio = row["volume"] / row["vol_ma_20"] if row["vol_ma_20"] > 0 else 0
    reasoning = [
        f"EMA50 {'above' if direction == 'LONG' else 'below'} EMA200 by {ema_gap_pct:.2f}% — trend confirmed.",
        f"RSI {row['rsi_14']:.1f}, MACD hist {row['macd_hist']:+.4f}, Stoch K/D {row['stoch_k']:.1f}/{row['stoch_d']:.1f} — momentum aligned.",
        f"Volume {vol_ratio:.1f}x avg; {'breakout' if direction == 'LONG' else 'breakdown'} structure present.",
    ]

    log.info(
        "evaluator.aplus_signal",
        direction=direction,
        entry=f"{entry:.2f}",
        stop_loss=f"{stop_loss:.2f}",
        take_profit=f"{take_profit:.2f}",
        rr=f"1:{rr_ratio:.1f}",
        confidence=confidence,
    )

    return Signal(
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        take_profit=take_profit,
        rr_ratio=rr_ratio,
        confidence=confidence,
        reasoning=reasoning,
    )
