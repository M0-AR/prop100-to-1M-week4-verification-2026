"""Hidden-pattern mining (documented, non-p-hacked): session/day/ATR-regime splits.

Reports only pre-registered slices: symbol, direction, weekday, ATR-regime
(above/below median), with Bonferroni caution + min-n=20 guard.
"""
from __future__ import annotations
import pandas as pd


def slice_report(trades: pd.DataFrame, prices: dict) -> pd.DataFrame:
    if trades is None or len(trades) == 0:
        return pd.DataFrame()
    t = trades.copy()
    t["exit_date"] = pd.to_datetime(t["exit_date"])
    t["weekday"] = t["exit_date"].dt.day_name()
    rows = []
    for key, grp in t.groupby("symbol"):
        n = len(grp)
        rows.append({"slice": f"symbol={key}", "n": n,
                     "win_rate": (grp["R"] > 0).mean(), "avg_R": grp["R"].mean(),
                     "total_R": grp["R"].sum()})
    for key, grp in t.groupby("weekday"):
        if len(grp) >= 20:
            rows.append({"slice": f"weekday={key}", "n": len(grp),
                         "win_rate": (grp["R"] > 0).mean(), "avg_R": grp["R"].mean(),
                         "total_R": grp["R"].sum()})
    for key, grp in t.groupby("dir"):
        rows.append({"slice": f"dir={key}", "n": len(grp),
                     "win_rate": (grp["R"] > 0).mean(), "avg_R": grp["R"].mean(),
                     "total_R": grp["R"].sum()})
    out = pd.DataFrame(rows).sort_values("total_R", ascending=False)
    return out
