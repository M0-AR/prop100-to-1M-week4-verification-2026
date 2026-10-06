# PAPER DRAFT — Can a Week-4 Discretionary Break–Retest Swing System Survive Rule-Explicit Backtesting Under One-Step Prop Constraints?
## Abstract
We formalize eight hypotheses (H1–H8) from a public “$100→$1M regulated prop-firm” Week-4 video (USDJPY/CADJPY/AUDCHF/NZDCAD/GBPNZD/EURGBP/AUDJPY/XAUUSD break–retest, head-and-shoulders, engulfing at areas of interest, EMA regime, 1.5% risk, 1–2-week swing hold) into deterministic daily-bar rules and test them on public daily OHLC 2020-01→2026-10 (Yahoo Finance, 1,760 bars/pair + ECB cross-check). Pooled n=40, win 40%, PF 0.50, expectancy −0.15R, Monte-Carlo P(target before ruin) 2%, max-DD breached. We show the null is driven by timeframe mismatch and sample starvation, not costs, and propose a pre-registered H4 tick-rebuilt follow-up. Contribution: (i) first rule-explicit formalization of this viral challenge system, (ii) reproducible Docker pipeline with correctness-tested engine, (iii) honest negative result with falsifiable next steps.
## 1. Introduction
Prop challenges are behavioral stress tests (drawdown caps, consistency rules) not pure profitability tests (FX Replay 2026). Viral “$100→$1M” content rarely publishes rule-explicit tests. We close that gap for Week 4.
## 2. Hypotheses (H1–H8)
See README §1 + src/strategy.py. Each maps a transcript claim to a boolean signal (engulfing/H&S/AOI/EMA/break) with next-open execution.
## 3. Method (zero-to-hero, 2026 best practice)
Data (Yahoo daily + Frankfurter live, Stooq-block documented) → costs (spread/commission/slippage) → engine (stop-before-target, no look-ahead, Maier-Paape correctness tests) → metrics (win/PF/expectancy/Sharpe/MAE-proxy/max-streak) → Monte-Carlo (5k shuffles) → hidden-pattern slices (pre-registered, min-n=20, Bonferroni caution) → prop overlay ($500 cap, $150/win, 5%/10% guards) → walk-forward plan.
## 4. Results
Pooled 40 trades: PF 0.50, expectancy −0.15R, payout $0, max-DD −14.5% breached, daily guard intact. Four symbols zero signals. Only AUDCHF nominally positive (n=2). No weekday slice qualifies (anti-p-hack).
## 5. Hidden patterns
(a) Daily selectivity ≈6 trades/yr pooled vs required 3–5/week → sample starvation. (b) Intraday engulfing literature (Alanazi 2020: 112k daily + 149k H4 candles, 24 pairs, 3M quotes) shows costs + timeframe decide profitability — consistent with our daily null. (c) Stop-tightness anecdote matches MAE literature: structure stops > fixed ATR. (d) Prop cap+consistency makes low-frequency swing unviable for compounding.
## 6. Threats to validity
Daily proxy of H4/H1 skill; Yahoo vs prop feed; deterministic H&S/AOI proxies; n=40 wide CIs; no session filter. Not a disproof of trader skill — a disproof of the daily formalization.
## 7. Future work (publishable)
Dukascopy H4 rebuild + London filter + structure stops + 100–300 H4 trades + walk-forward OOS + spread sensitivity + live demo forward test. Pre-register H1′–H8′.
## 8. Reproducibility
`docker compose up research`, `pytest`, SHA manifest. Code+data scripts MIT; data via public links (terms-respecting).
## Ethics
No real-money advice; education only; costs/risks disclosed; failures published.
