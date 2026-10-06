"""Formalized Week-4 hypotheses H1..H8 extracted from the transcript.

Each hypothesis is a RULE-EXPLICIT signal function returning entries
(+1 long / -1 short / 0 flat) on a DAILY OHLC frame. Intraday H4/H1
engulfing in the video is proxied by daily engulfing + AOI retest, because
public daily data is verifiable without broker key; H4 refinement is a
documented limitation (see README/PAPER).

H1 USDJPY short:  bearish engulfing (or H&S proxy) at AOI + close<EMA20
H2 CADJPY short:  cousin of H1, same rule on CADJPY
H3 AUDCHF short (CTT): H&S bearish proxy + daily bearish engulfing at resistance
H4 NZDCAD long:  bullish engulfing at support AOI (break-retest up)
H5 GBPNZD short: break below minor AOI + close<EMA20 (continuation)
H6 EURGBP long:  bullish engulfing at support + close>EMA20 (continuation buys)
H7 AUDJPY long:  momentum break-retest: bullish break then bullish engulfing within 3 bars
H8 XAUUSD short: break below AOI + bearish engulfing (gold rejection short)
"""
from __future__ import annotations
import pandas as pd
from . import indicators as I


def add_context(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["ema20"] = I.ema(d["close"], 20)
    d["atr14"] = I.atr(d, 14)
    d["bull_eng"] = I.bullish_engulfing(d).fillna(False)
    d["bear_eng"] = I.bearish_engulfing(d).fillna(False)
    d["at_aoi"] = I.at_aoi(d, 50, 0.75).fillna(False)
    d["hs_bear"] = I.hs_bearish_proxy(d, 2).fillna(False)
    d["br_bear"] = I.structure_break_bearish(d, 20).fillna(False)
    d["br_bull"] = I.structure_break_bullish(d, 20).fillna(False)
    return d


def sig_usdjpy_short(d: pd.DataFrame) -> pd.Series:
    return ((d["bear_eng"] | d["hs_bear"]) & d["at_aoi"] & (d["close"] < d["ema20"])).astype(int) * -1


def sig_cadjpy_short(d: pd.DataFrame) -> pd.Series:
    return ((d["bear_eng"] | d["br_bear"]) & d["at_aoi"] & (d["close"] < d["ema20"])).astype(int) * -1


def sig_audchf_short(d: pd.DataFrame) -> pd.Series:
    # counter-trend short: needs H&S or engulfing at AOI while ABOVE ema also allowed
    # (counter-trend), but require bearish trigger bar.
    return ((d["bear_eng"] | d["hs_bear"]) & d["at_aoi"]).astype(int) * -1


def sig_nzdcad_long(d: pd.DataFrame) -> pd.Series:
    return (d["bull_eng"] & d["at_aoi"]).astype(int)


def sig_gbpnzd_short(d: pd.DataFrame) -> pd.Series:
    return ((d["br_bear"]) & (d["close"] < d["ema20"])).astype(int) * -1


def sig_eurgbp_long(d: pd.DataFrame) -> pd.Series:
    return ((d["bull_eng"]) & d["at_aoi"] & (d["close"] > d["ema20"])).astype(int)


def sig_audjpy_long(d: pd.DataFrame) -> pd.Series:
    br = d["br_bull"]
    # retest: bullish engulfing within 3 bars after a bullish break
    br_idx = br.fillna(False)
    recent_br = br_idx.rolling(3).max().fillna(0).astype(bool)
    return ((d["bull_eng"]) & recent_br).astype(int)


def sig_xauusd_short(d: pd.DataFrame) -> pd.Series:
    return ((d["bear_eng"]) & (d["br_bear"] | d["at_aoi"])).astype(int) * -1


STRATEGY_MAP = {
    "USDJPY": ("short", sig_usdjpy_short, "H1 USDJPY bearish engulf/H&S at AOI, close<EMA20"),
    "CADJPY": ("short", sig_cadjpy_short, "H2 CADJPY cousin short"),
    "AUDCHF": ("short", sig_audchf_short, "H3 AUDCHF CTT H&S short"),
    "NZDCAD": ("long", sig_nzdcad_long, "H4 NZDCAD break-retest long"),
    "GBPNZD": ("short", sig_gbpnzd_short, "H5 GBPNZD continuation short"),
    "EURGBP": ("long", sig_eurgbp_long, "H6 EURGBP continuation long"),
    "AUDJPY": ("long", sig_audjpy_long, "H7 AUDJPY momentum retest long"),
    "XAUUSD": ("short", sig_xauusd_short, "H8 GOLD rejection short"),
}
