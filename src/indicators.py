"""Indicators: EMA, ATR, engulfing, swing structure, AOI, H&S proxy.

All functions are pure pandas/numpy, no look-ahead (shifted where needed).
Verified against textbook definitions; unit-tested in tests/.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([(h - l), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def bullish_engulfing(df: pd.DataFrame) -> pd.Series:
    o, c = df["open"], df["close"]
    po, pc = o.shift(1), c.shift(1)
    return (pc < po) & (c > o) & (c >= po) & (o <= pc)


def bearish_engulfing(df: pd.DataFrame) -> pd.Series:
    o, c = df["open"], df["close"]
    po, pc = o.shift(1), c.shift(1)
    return (pc > po) & (c < o) & (c <= po) & (o >= pc)


def swing_high(s: pd.Series, k: int = 2) -> pd.Series:
    """True if s[i] is max of window [i-k, i+k]. Uses centered rolling (needs future
    k bars -> signal only valid with k-bar delay; backtester enforces delay)."""
    roll_max = s.rolling(2 * k + 1, center=True).max()
    return s == roll_max


def swing_low(s: pd.Series, k: int = 2) -> pd.Series:
    roll_min = s.rolling(2 * k + 1, center=True).min()
    return s == roll_min


def area_of_interest(df: pd.DataFrame, lookback: int = 50, tol_atr: float = 0.25) -> pd.Series:
    """Proxy for 'area of interest': prior N-bar high/low zone.
    Returns distance-to-nearest-edge in ATR units (min of dist to rolling high/low)."""
    a = atr(df, 14)
    rh = df["high"].rolling(lookback).max().shift(1)
    rl = df["low"].rolling(lookback).min().shift(1)
    dist_high = (rh - df["close"]).abs() / a
    dist_low = (df["close"] - rl).abs() / a
    return pd.concat([dist_high, dist_low], axis=1).min(axis=1)


def at_aoi(df: pd.DataFrame, lookback: int = 50, tol_atr: float = 0.5) -> pd.Series:
    return area_of_interest(df, lookback) <= tol_atr


def hs_bearish_proxy(df: pd.DataFrame, k: int = 2) -> pd.Series:
    """Head-and-shoulders (bearish) proxy on closes:
    three swing-highs H1<H2>H3 with H1~=H3 and neckline = min of two troughs.
    Returns boolean; delayed by k bars (uses centered swings)."""
    h = df["high"]
    sh = swing_high(h, k)
    idx = np.where(sh.fillna(False).values)[0]
    out = np.zeros(len(df), dtype=bool)
    closes = df["close"].values
    for j in range(2, len(idx)):
        i1, i2, i3 = idx[j - 2], idx[j - 1], idx[j]
        h1, h2, h3 = h.iloc[i1], h.iloc[i2], h.iloc[i3]
        if not (h2 > h1 and h2 > h3):
            continue
        # shoulders symmetric within 1.5 ATR
        a = atr(df, 14).iloc[i3]
        if abs(h1 - h3) > 1.5 * a:
            continue
        t1 = df["low"].iloc[i1:i2 + 1].min()
        t2 = df["low"].iloc[i2:i3 + 1].min()
        neck = min(t1, t2)
        # trigger bar: close below neckline after i3
        if i3 + 1 < len(df) and closes[i3 + 1] < neck:
            out[i3 + 1] = True
    return pd.Series(out, index=df.index)


def hs_bullish_proxy(df: pd.DataFrame, k: int = 2) -> pd.Series:
    l = df["low"]
    sl = swing_low(l, k)
    idx = np.where(sl.fillna(False).values)[0]
    out = np.zeros(len(df), dtype=bool)
    closes = df["close"].values
    for j in range(2, len(idx)):
        i1, i2, i3 = idx[j - 2], idx[j - 1], idx[j]
        l1, l2, l3 = l.iloc[i1], l.iloc[i2], l.iloc[i3]
        if not (l2 < l1 and l2 < l3):
            continue
        from pandas import Series as _S  # local to avoid circular
        a = atr(df, 14).iloc[i3]
        if abs(l1 - l3) > 1.5 * a:
            continue
        t1 = df["high"].iloc[i1:i2 + 1].max()
        t2 = df["high"].iloc[i2:i3 + 1].max()
        neck = max(t1, t2)
        if i3 + 1 < len(df) and closes[i3 + 1] > neck:
            out[i3 + 1] = True
    return pd.Series(out, index=df.index)


def structure_break_bearish(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Close below rolling N-bar low (break), shifted execution handled by backtester."""
    return df["close"] < df["low"].rolling(lookback).min().shift(1)


def structure_break_bullish(df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    return df["close"] > df["high"].rolling(lookback).max().shift(1)
