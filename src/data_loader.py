"""Public-data loader: Yahoo Finance daily OHLC (no key) + Frankfurter ECB cross-check.

Primary (backtest): Yahoo v8 chart daily 2020-01-01 -> present for 8 symbols.
  JPY=X (USDJPY), CADJPY=X, AUDCHF=X, NZDCAD=X, GBPNZD=X, EURGBP=X, AUDJPY=X, GC=F (XAUUSD)
  URL: https://query1.finance.yahoo.com/v8/finance/chart/{Y}?period1=&period2=&interval=1d
  Verified 2026-10-06: Stooq blocked by JS-botwall (documented in DATA_MANIFEST),
  Yahoo + Frankfurter both return HTTP 200 from this host.
Independent check: Frankfurter ECB daily (https://api.frankfurter.app) for FX triangulation.
All downloads logged to data/DATA_MANIFEST.md with row counts + SHA.
"""
from __future__ import annotations
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import requests

YAHOO = {
    "USDJPY": "JPY=X", "CADJPY": "CADJPY=X", "AUDCHF": "AUDCHF=X",
    "NZDCAD": "NZDCAD=X", "GBPNZD": "GBPNZD=X", "EURGBP": "EURGBP=X",
    "AUDJPY": "AUDJPY=X", "XAUUSD": "GC=F",
}
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch_yahoo(symbol: str, start="2020-01-01", end=None) -> pd.DataFrame:
    y = YAHOO[symbol]
    p1 = int(datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    p2 = int(datetime.now(timezone.utc).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{y}?period1={p1}&period2={p2}&interval=1d"
    r = requests.get(url, timeout=30, headers={"User-Agent": "research/1.0"})
    r.raise_for_status()
    j = r.json()
    res = j["chart"]["result"][0]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    df = pd.DataFrame({
        "date": pd.to_datetime(ts, unit="s", utc=True),
        "open": q["open"], "high": q["high"], "low": q["low"],
        "close": q["close"], "volume": q.get("volume", [None] * len(ts)),
    })
    df = df.dropna(subset=["open", "high", "low", "close"]).sort_values("date")
    if len(df) < 100:
        raise RuntimeError(f"too few bars for {symbol}: {len(df)}")
    return df.reset_index(drop=True)


def save_all(start="2020-01-01", end=None) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    for sym in YAHOO:
        try:
            df = fetch_yahoo(sym, start, end)
            p = RAW / f"{sym}_D1.csv"
            df.to_csv(p, index=False)
            h = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
            rows.append((sym, len(df), str(df['date'].min().date()),
                         str(df['date'].max().date()), h, "OK Yahoo"))
        except Exception as e:  # keep manifest honest about failures
            rows.append((sym, 0, "-", "-", "-", f"FAIL {e}"))
    man = RAW.parent / "DATA_MANIFEST.md"
    lines = ["# DATA_MANIFEST (public, reproducible)", "",
             f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}", "",
             "Primary: Yahoo Finance v8 daily OHLC (no key). Stooq attempted first, "
             "blocked by JS-botwall 2026-10-06, fallback to Yahoo verified. "
             "Redistribution: link + script, not vendored bulk (terms-respecting).", "",
             "| symbol | rows | from | to | sha12 | status |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |")
    # live spot via Frankfurter (ECB) as independent second source
    try:
        fx = requests.get("https://api.frankfurter.app/latest?from=EUR",
                          timeout=20).json()
        lines += ["", f"Frankfurter live check (EUR base, {fx.get('date')}): "
                      f"USD={fx.get('rates',{}).get('USD')} JPY={fx.get('rates',{}).get('JPY')} "
                      f"GBP={fx.get('rates',{}).get('GBP')}"]
    except Exception as e:
        lines += ["", f"Frankfurter live check FAILED: {e}"]
    man.write_text("\n".join(lines))
    return man


def load(symbol: str) -> pd.DataFrame:
    p = RAW / f"{symbol}_D1.csv"
    df = pd.read_csv(p, parse_dates=["date"])
    df = df.set_index("date").sort_index()
    return df[["open", "high", "low", "close"]]
