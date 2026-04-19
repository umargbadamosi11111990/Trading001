from typing import Literal

Direction = Literal["LONG", "SHORT"]

# Max points per component — total = 100
WEIGHTS = {
    "ema_alignment": 20,
    "rsi_zone": 15,
    "macd_histogram": 15,
    "stoch_confirmation": 15,
    "volume_spike": 10,
    "price_structure": 15,
    "rr_ratio": 10,
}


def score_ema_alignment(row, direction: Direction) -> float:
    spread_pct = abs(row["ema_50"] - row["ema_200"]) / row["ema_200"] * 100
    aligned = (
        (direction == "LONG" and row["ema_50"] > row["ema_200"])
        or (direction == "SHORT" and row["ema_50"] < row["ema_200"])
    )
    if not aligned:
        return 0.0
    gap_score = min(spread_pct / 0.3, 1.0)
    return 10.0 + 10.0 * gap_score


def score_rsi(row, direction: Direction) -> float:
    rsi = row["rsi_14"]
    if direction == "LONG":
        if rsi > 70:
            return 0.0   # overbought — disqualify
        elif 40 <= rsi <= 65:
            return 15.0  # ideal zone
        elif 65 < rsi <= 70:
            return 8.0   # approaching overbought
        else:
            return 5.0   # oversold bounce
    else:
        if rsi < 30:
            return 0.0   # oversold — disqualify
        elif 35 <= rsi <= 60:
            return 15.0
        elif 30 <= rsi < 35:
            return 8.0
        else:
            return 5.0


def score_macd(row, direction: Direction) -> float:
    hist = row["macd_hist"]
    if direction == "LONG" and hist <= 0:
        return 0.0
    if direction == "SHORT" and hist >= 0:
        return 0.0
    magnitude = min(abs(hist) / 0.50, 1.0)
    return 15.0 * magnitude


def score_stoch(row, direction: Direction) -> float:
    k, d = row["stoch_k"], row["stoch_d"]
    if direction == "LONG":
        if k > 80:
            return 0.0   # overbought — disqualify
        elif k < 20 and k > d:
            return 15.0  # golden cross from oversold
        elif 20 <= k <= 80:
            return 10.0
        else:
            return 5.0
    else:
        if k < 20:
            return 0.0   # oversold — disqualify
        elif k > 80 and k < d:
            return 15.0  # death cross from overbought
        elif 20 <= k <= 80:
            return 10.0
        else:
            return 5.0


def score_volume(row) -> float:
    if row["vol_ma_20"] <= 0:
        return 0.0
    ratio = row["volume"] / row["vol_ma_20"]
    if ratio < 1.0:
        return 0.0
    elif ratio < 1.3:
        return 5.0
    elif ratio < 1.7:
        return 8.0
    else:
        return 10.0


def score_price_structure(
    row, direction: Direction, recent_high: float, recent_low: float
) -> float:
    close = row["close"]
    if direction == "LONG":
        margin = (close - recent_high) / recent_high
        if margin > 0.002:
            return 15.0
        elif margin > 0:
            return 10.0
        elif margin > -0.002:
            return 7.0
        else:
            return 2.0
    else:
        margin = (recent_low - close) / recent_low
        if margin > 0.002:
            return 15.0
        elif margin > 0:
            return 10.0
        elif margin > -0.002:
            return 7.0
        else:
            return 2.0


def score_rr(rr_ratio: float) -> float:
    if rr_ratio < 2.0:
        return 0.0
    elif rr_ratio < 3.0:
        return 5.0 + 5.0 * (rr_ratio - 2.0)
    else:
        return 10.0


def compute_confidence(
    row,
    direction: Direction,
    rr_ratio: float,
    recent_high: float,
    recent_low: float,
) -> int:
    total = (
        score_ema_alignment(row, direction)
        + score_rsi(row, direction)
        + score_macd(row, direction)
        + score_stoch(row, direction)
        + score_volume(row)
        + score_price_structure(row, direction, recent_high, recent_low)
        + score_rr(rr_ratio)
    )
    return int(min(round(total), 100))
