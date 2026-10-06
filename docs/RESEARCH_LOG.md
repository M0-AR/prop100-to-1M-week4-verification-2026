# RESEARCH_LOG (zero-to-hero, source-by-source)
1. websearch Exa `prop firm challenge verification backtesting best practices 2026 forex` → 100-trade bar, firm-specific params, costs, OOS, execution gap. Applied: engine + metrics + prop overlay.
2. duckduckgo_search `forex head and shoulders break retest strategy win rate academic study` → H&S 51%/19% (Bulkowski), break-retest rules, 1:2 R:R. Applied: H1–H3 formalization, symmetric-shoulder 1.5ATR rule.
3. searxng_web_search `regulated prop firm consistency rule profit cap payout 10K challenge 2026` → Network Error (SEARXNG_URL). Documented; used suggestions fallback + websearch coverage instead. No silent skip.
4. openresearch web_search `forex swing trading USDJPY NZD CAD backtest verification methodology` → Traders Gym/Manual vs automated, costs. Applied: costs + manual/intraday limitation note.
5. paper-search unified `technical analysis head and shoulders forex profitability` → 15 papers incl SSRN H&S institutional, Watson thesis, ITCM 2026. Applied: lit review + decay/psychology discussion.
6. agent-reach_search web `forex backtesting python vectorbt free tick data Dukascopy 2026` → duka-data 20y pipeline, vectorbt sweep, MT5 latency model. Applied: data plan + future H4 work + spread column lesson.
7. openresearch hacker_news `prop firm forex challenge pass rate` → no results. Documented (no HN signal).
8. openresearch openalex `forex technical analysis profitability engulfing pattern` → Alanazi 2020 key citation. Applied: engulfing cost-dependence claim.
9. kaggle search_everything `forex backtesting prop firm` → no results. Documented.
10. wiki_search `foreign exchange backtesting drawdown` → Algorithmic trading baseline only. Documented.
11. gitmcp docs `saleem-latif/duka-data` → full pipeline doc retrieved. Applied: future tick work + terms note.
12. gsd_websearch `forex strategy verification walk-forward Monte Carlo 2026 reproducible research` → empty output. Documented.
13. openresearch news `prop firm payouts regulated capital 2026` → GDELT rate-limited. Documented, single retry, no loop.
14. superpowers semantic `backtesting verification reproducible research methodology` → verification-before-completion guardrails. Applied: test-before-claim discipline.
15. searxng suggestions `forex prop firm backtest consistency rule` → empty suggestions. Documented.
16. webfetch lite.duckduckgo `forex break retest backtest profit factor 2026` → 10 results incl PF/consistency guides. Applied: PF>1.7 bar + 30-trade minimum.
17. paper-search arxiv `forex candlestick engulfing backtest profitability` → Maier-Paape correctness pair. Applied: stop-before-target + no-look-ahead tests.
18. Live verification (this host): Stooq FAIL (JS botwall, saved HTML prefix), Yahoo OK (1,760/1,702 bars), Frankfurter OK (2026-10-05). Decision: Yahoo primary, manifest honest. Engine tests: 3/3 pass after horizon fix (30→40 bars). Backtest pooled n=40 PF 0.50. Monte-Carlo 2% target-first. Prop payout $0, maxDD breached. All artifacts in results/.
