"""04: hidden-pattern slices (pre-registered only)."""
from pathlib import Path
import pandas as pd
from src.hidden_patterns import slice_report
RES = Path(__file__).resolve().parents[1] / "results"
if __name__ == "__main__":
    T = pd.read_csv(RES / "all_trades.csv")
    rep = slice_report(T, {})
    rep.to_csv(RES / "hidden_patterns.csv", index=False)
    print(rep.to_string())
