"""Engine correctness (Maier-Paape style): no look-ahead, stop-before-target, costs."""
import pandas as pd
from src.backtest import backtest_symbol
from src.strategy import add_context


def test_no_lookahead():
    dates = pd.date_range("2020-01-01", periods=40, freq="D", tz="UTC")
    df = pd.DataFrame({"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0}, index=dates)
    d = add_context(df)
    sig = pd.Series(0, index=d.index)
    sig.iloc[20] = 1
    tr = backtest_symbol(d, sig, "EURGBP")
    assert len(tr) == 1 and tr.iloc[0]["entry_date"] == dates[21]


def test_stop_before_target_conservative():
    dates = pd.date_range("2020-01-01", periods=10, freq="D", tz="UTC")
    df = pd.DataFrame({"open": 100.0, "high": 110.0, "low": 90.0, "close": 100.0}, index=dates)
    d = add_context(df)
    d["atr14"] = 1.0
    sig = pd.Series(0, index=d.index); sig.iloc[2] = 1
    tr = backtest_symbol(d, sig, "EURGBP")
    assert len(tr) >= 1 and tr.iloc[0]["R"] == -1.0
