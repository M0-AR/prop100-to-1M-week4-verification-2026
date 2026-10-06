"""05: prop compliance (profit-cap $500, $150/win consistency, daily DD)."""
import json
from pathlib import Path
import pandas as pd
from src.prop_rules import payout_estimate, daily_guard, maxdd_guard
RES = Path(__file__).resolve().parents[1] / "results"
if __name__ == "__main__":
    T = pd.read_csv(RES / "all_trades.csv")
    eq = pd.read_csv(RES / "equity.csv")
    eqs = eq.iloc[:, 0] if len(eq.columns) else pd.Series([10000])
    out = {"payout": payout_estimate(T), "daily": daily_guard(T),
           "maxdd": maxdd_guard(10000 + T["pnl"].cumsum() if len(T) else eqs)}
    (RES / "prop_compliance.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
