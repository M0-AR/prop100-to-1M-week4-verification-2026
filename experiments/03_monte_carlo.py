"""03: Monte-Carlo sequence risk (5k paths)."""
import json
from pathlib import Path
import pandas as pd
from src.metrics import monte_carlo_ruin
RES = Path(__file__).resolve().parents[1] / "results"
if __name__ == "__main__":
    T = pd.read_csv(RES / "all_trades.csv")
    r = monte_carlo_ruin(T)
    (RES / "monte_carlo.json").write_text(json.dumps(r, indent=2))
    print(r)
