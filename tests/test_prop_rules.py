"""Prop-rule unit tests: $500 cap, $150/win consistency."""
import pandas as pd
from src.prop_rules import payout_estimate
def test_consistency_cap():
    t = pd.DataFrame({"pnl": [400.0, -50.0], "R": [2.0, -1.0],
                      "exit_date": pd.to_datetime(["2020-01-02", "2020-01-03"]),
                      "symbol": ["USDJPY"]*2})
    p = payout_estimate(t)
    assert p["capped"] == 150.0 - 50.0
    assert p["payout"] == 100.0
