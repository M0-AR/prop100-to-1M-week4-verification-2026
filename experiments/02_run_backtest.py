"""02: run full 8-symbol backtest 2020->present; writes results/*.json/csv + equity."""
import json
from pathlib import Path
import pandas as pd
from src.data_loader import load
from src.strategy import add_context, STRATEGY_MAP
from src.backtest import backtest_symbol, combine
from src.metrics import summary, sharpe_daily
from src.prop_rules import payout_estimate, daily_guard

RES = Path(__file__).resolve().parents[1] / "results"
RES.mkdir(exist_ok=True)

if __name__ == "__main__":
    all_t, per = [], {}
    prices = {}
    for sym, (side, fn, desc) in STRATEGY_MAP.items():
        df = load(sym)
        prices[sym] = df
        d = add_context(df)
        sig = fn(d)
        tr = backtest_symbol(d, sig, sym)
        all_t.append(tr)
        s = summary(tr)
        per[sym] = {"desc": desc, "signals": int((sig != 0).sum()), **s,
                    "pnl": float(tr["pnl"].sum()) if len(tr) else 0.0}
        print(sym, per[sym])
    T = combine(all_t)
    T.to_csv(RES / "all_trades.csv", index=False)
    eq = 10000 + T["pnl"].cumsum() if len(T) else pd.Series([10000])
    eq.to_csv(RES / "equity.csv", index=False, header=True)
    out = {"per_symbol": per, "pooled": summary(T),
           "sharpe_proxy": sharpe_daily(eq if isinstance(eq, pd.Series) else pd.Series(eq.values.ravel())),
           "payout": payout_estimate(T), "daily": daily_guard(T),
           "n_trades": int(len(T))}
    (RES / "backtest_summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
