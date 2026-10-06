"""Prop-firm compliance: 10K one-step (video) with profit-cap + consistency rule.

Video states: 10K challenge, profit cap 5% ($500), consistency 30% => max $150/win
counts toward payout, payout request $522 example, 1.5% risk/trade.
Also models standard guards: daily loss 5%, max drawdown 10% (typical 1-step).
"""
from __future__ import annotations
import pandas as pd

PROFIT_CAP = 500.0
CONSISTENCY_MAX_PER_WIN = 150.0


def apply_consistency_cap(trades: pd.DataFrame) -> pd.DataFrame:
    t = trades.copy()
    if len(t) == 0:
        t["pnl_capped"] = []
        return t
    t["pnl_capped"] = t["pnl"].clip(upper=CONSISTENCY_MAX_PER_WIN)
    return t


def payout_estimate(trades: pd.DataFrame) -> dict:
    if trades is None or len(trades) == 0:
        return {"gross": 0.0, "capped": 0.0, "payout": 0.0, "cap_hit": False}
    t = apply_consistency_cap(trades)
    gross = float(t["pnl"].sum())
    capped = float(t["pnl_capped"].sum())
    payout = max(0.0, min(capped, PROFIT_CAP))
    return {"gross": gross, "capped": capped, "payout": payout,
            "cap_hit": capped >= PROFIT_CAP}


def daily_guard(trades: pd.DataFrame, equity0=10000.0, daily_pct=0.05) -> dict:
    if trades is None or len(trades) == 0:
        return {"breached": False, "worst_day": 0.0}
    t = trades.copy()
    t["exit_date"] = pd.to_datetime(t["exit_date"])
    t["day"] = t["exit_date"].dt.date
    d = t.groupby("day")["pnl"].sum()
    worst = float(d.min()) if len(d) else 0.0
    return {"breached": bool(worst < -equity0 * daily_pct), "worst_day": worst,
            "daily_limit": -equity0 * daily_pct}


def maxdd_guard(equity_curve: pd.Series, max_pct=0.10) -> dict:
    if equity_curve is None or len(equity_curve) == 0:
        return {"breached": False, "maxdd": 0.0}
    roll = equity_curve.cummax()
    dd = (equity_curve - roll) / roll
    m = float(dd.min())
    return {"breached": bool(m < -max_pct), "maxdd": m}
