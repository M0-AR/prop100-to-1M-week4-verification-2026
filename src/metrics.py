"""Metrics: expectancy, PF, Sharpe, MAE, walk-forward, Monte-Carlo, spread sensitivity."""
from __future__ import annotations
import numpy as np
import pandas as pd


def summary(trades: pd.DataFrame) -> dict:
    if trades is None or len(trades) == 0:
        return {"n": 0, "win_rate": 0.0, "profit_factor": 0.0, "expectancy_R": 0.0,
                "total_R": 0.0, "avg_R": 0.0, "max_loss_streak": 0, "pnl": 0.0}
    w = (trades["R"] > 0).mean()
    gp = trades.loc[trades["pnl"] > 0, "pnl"].sum()
    gl = -trades.loc[trades["pnl"] <= 0, "pnl"].sum()
    pf = float(gp / gl) if gl > 0 else float("inf") if gp > 0 else 0.0
    # max consecutive R<=0
    s = 0; m = 0
    for r in trades["R"].values:
        s = s + 1 if r <= 0 else 0
        m = max(m, s)
    return {"n": int(len(trades)), "win_rate": float(w), "profit_factor": float(pf),
            "expectancy_R": float(trades["R"].mean()), "total_R": float(trades["R"].sum()),
            "avg_R": float(trades["R"].mean()), "max_loss_streak": int(m),
            "pnl": float(trades["pnl"].sum())}


def sharpe_daily(equity: pd.Series) -> float:
    r = equity.pct_change().dropna()
    if len(r) < 5 or r.std() == 0:
        return 0.0
    return float((r.mean() / r.std()) * np.sqrt(252))


def monte_carlo_ruin(trades: pd.DataFrame, equity0=10000.0, target=500.0,
                     daily_limit=500.0, n_paths=5000, seed=7) -> dict:
    """Shuffle trade order; count paths hitting +target before -daily_limit drawdown
    within one 'challenge window' (same N trades). Sequence-risk proxy (see README)."""
    if trades is None or len(trades) == 0:
        return {"p_target_first": 0.0, "p_ruin": 0.0, "n_paths": n_paths}
    rng = np.random.default_rng(seed)
    pnls = trades["pnl"].values
    hit = 0; ruin = 0
    for _ in range(n_paths):
        order = rng.permutation(pnls)
        eq = equity0; peak = equity0; day_eq = equity0
        # approximate daily as cumulative within window (conservative)
        ok = False; dead = False
        for p in order:
            eq += p
            peak = max(peak, eq)
            if eq - equity0 >= target:
                ok = True; break
            if peak - eq >= daily_limit or equity0 - eq >= daily_limit:
                dead = True; break
        hit += ok; ruin += dead and not ok
    return {"p_target_first": hit / n_paths, "p_ruin": ruin / n_paths, "n_paths": n_paths}


def walk_forward_split(dates, n_splits=3):
    idx = np.array_split(np.arange(len(dates)), n_splits)
    return idx
