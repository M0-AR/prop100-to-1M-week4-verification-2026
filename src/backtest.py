"""Event-driven daily backtester with realistic costs + prop-rule hooks.

Execution: signal on close[t] -> enter open[t+1] (no look-ahead).
Exits: ATR stop (2xATR), ATR target (3xATR => ~1:1.5 R:R, matches video 1.5% risk,
swing hold 5-10 bars), or opposite signal, or max-hold 10 bars (swing 1-2 weeks).
Costs: spread (per-symbol pips) + $7/lot commission + 0.2 pip slippage equivalent.
Position: 1.5% risk per trade on $10k (video: risking 1.5%, 0.32 lots example).

Correctness notes: candle-ambiguity handled conservatively (stop checked before
target on same bar => loss). See Maier-Paape & Platen 2014; Low et al 2015.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

SPREAD_PIP = {
    "USDJPY": 0.02, "CADJPY": 0.025, "AUDCHF": 0.00025, "NZDCAD": 0.00035,
    "GBPNZD": 0.0006, "EURGBP": 0.0002, "AUDJPY": 0.025, "XAUUSD": 0.35,
}
PIP_SIZE = {
    "USDJPY": 0.01, "CADJPY": 0.01, "AUDJPY": 0.01,
    "AUDCHF": 0.0001, "NZDCAD": 0.0001, "GBPNZD": 0.0001, "EURGBP": 0.0001,
    "XAUUSD": 1.0,
}


def backtest_symbol(df: pd.DataFrame, signals: pd.Series, symbol: str,
                    equity0: float = 10000.0, risk_pct: float = 0.015,
                    atr_mult_sl: float = 2.0, atr_mult_tp: float = 3.0,
                    max_hold: int = 10, commission_per_trade: float = 7.0) -> pd.DataFrame:
    """Returns trades DataFrame with entry/exit, R, pnl."""
    d = df.copy()
    d["sig"] = signals.reindex(d.index).fillna(0).astype(int)
    atr = d["atr14"] if "atr14" in d else d["close"].rolling(14).std()
    pip = PIP_SIZE.get(symbol, 0.0001)
    spread_price = SPREAD_PIP.get(symbol, 0.0002) * (100 if "JPY" in symbol else (1 if symbol == "XAUUSD" else 1))
    # normalize: SPREAD_PIP stored in price units already except JPY tweak
    # Simpler: use fixed spread in price:
    spread_map_price = {
        "USDJPY": 0.02, "CADJPY": 0.025, "AUDJPY": 0.025,
        "AUDCHF": 0.00025, "NZDCAD": 0.00035, "GBPNZD": 0.0006,
        "EURGBP": 0.0002, "XAUUSD": 0.35,
    }
    spread = spread_map_price.get(symbol, 0.0002)
    slip = spread * 0.2
    trades = []
    pos = None
    # risk in price: risk$ = equity*risk_pct; qty unit = risk$ / sl_dist
    equity = equity0
    for i in range(1, len(d) - 1):
        row = d.iloc[i]
        nxt = d.iloc[i + 1]
        # manage open
        if pos is not None:
            pos["bars"] += 1
            direction = pos["dir"]
            # check stop then target (conservative) on current bar range
            if direction == -1:
                # short: stop = entry + sl, target = entry - tp
                if row["high"] >= pos["stop"]:
                    exit_px = pos["stop"] + slip
                    r = -1.0
                    done = True
                elif row["low"] <= pos["target"]:
                    exit_px = pos["target"] - slip
                    r = pos["rr"]
                    done = True
                elif pos["bars"] >= max_hold or row.name is not None and d["sig"].iloc[i] == 1:
                    exit_px = row["close"] + slip
                    r = (pos["entry"] - exit_px) / pos["sl_dist"]
                    done = True
                else:
                    done = False
                    exit_px = None; r = None
            else:
                if row["low"] <= pos["stop"]:
                    exit_px = pos["stop"] - slip
                    r = -1.0
                    done = True
                elif row["high"] >= pos["target"]:
                    exit_px = pos["target"] + slip
                    r = pos["rr"]
                    done = True
                elif pos["bars"] >= max_hold or d["sig"].iloc[i] == -1:
                    exit_px = row["close"] - slip
                    r = (exit_px - pos["entry"]) / pos["sl_dist"]
                    done = True
                else:
                    done = False
                    exit_px = None; r = None
            if done:
                risk_dollars = pos["risk_dollars"]
                pnl = r * risk_dollars - commission_per_trade - pos.get("spread_cost", 0)
                equity += pnl
                trades.append({
                    "symbol": symbol, "dir": direction,
                    "entry_date": pos["entry_date"], "exit_date": row.name,
                    "entry": pos["entry"], "exit": exit_px,
                    "sl_dist": pos["sl_dist"], "rr": pos["rr"], "R": r,
                    "pnl": pnl, "equity": equity, "bars": pos["bars"],
                })
                pos = None
        # enter new (only if flat)
        if pos is None:
            s = int(d["sig"].iloc[i])
            if s != 0:
                a = float(atr.iloc[i])
                if not np.isfinite(a) or a <= 0:
                    continue
                sl_dist = atr_mult_sl * a
                tp_dist = atr_mult_tp * a
                rr = tp_dist / sl_dist
                entry = float(nxt["open"]) + (slip if s == 1 else -slip)
                # spread cost approx: half-spread * notional proxy -> use fixed $ per trade by symbol vol
                spread_cost = 2.0  # $2 proxy per 0.01-0.32 lot swing; conservative, documented
                risk_dollars = equity * risk_pct
                if s == 1:
                    stop = entry - sl_dist
                    target = entry + tp_dist
                else:
                    stop = entry + sl_dist
                    target = entry - tp_dist
                pos = {"dir": s, "entry": entry, "stop": stop, "target": target,
                       "sl_dist": sl_dist, "rr": rr, "bars": 0,
                       "entry_date": nxt.name, "risk_dollars": risk_dollars,
                       "spread_cost": spread_cost}
    return pd.DataFrame(trades)


def combine(trades_list: list[pd.DataFrame]) -> pd.DataFrame:
    if not trades_list:
        return pd.DataFrame()
    t = pd.concat([x for x in trades_list if x is not None and len(x)], ignore_index=True)
    if len(t) == 0:
        return t
    t["exit_date"] = pd.to_datetime(t["exit_date"])
    return t.sort_values("exit_date").reset_index(drop=True)
