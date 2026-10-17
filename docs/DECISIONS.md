# Engineering Decisions — PriceWatch

---

## Decision 1 — Two price sources, chosen by ticker

**Context:** Crypto and stocks live in different APIs, and the user shouldn't have to say which is which.

**Decision:** Tickers in `COINGECKO_IDS` go to CoinGecko's free `simple/price` endpoint in `PRICEWATCH_CURRENCY`. Everything else goes to `yfinance` as an equity or index symbol.

**Reason:** `--asset BTC` and `--asset INFY` just work. CoinGecko's public tier needs no key, and yfinance covers global tickers and indices like `^NSEI`.

**Tradeoff:** Prices come in different currencies (CoinGecko in the configured one, stocks in their own). Only crypto symbols outside the map need adding by hand.

---

## Decision 2 — Log every check, not only alerts

**Context:** The daemon already fetches a price every interval.

**Decision:** Every fetched price is appended to `data/history_<ASSET>.csv`, whether or not it crosses anything.

**Reason:** The history is free. It feeds the weekly chart and turns an alert tool into a personal price tracker.

**Tradeoff:** The CSVs grow forever at one row per asset per interval: about 288 rows a day at the default 5 minutes.

---

## Decision 3 — Alert on the crossing, with a triggered flag

**Context:** Alerting on every tick above the target would spam the user.

**Decision:** `check_watch()` fires only when the price is past the target and the watch isn't already triggered, then sets `triggered`. It's meant to reset when the price moves back.

**Reason:** One notification per crossing is what a user expects from an alert.

**Tradeoff:** The reset isn't saved to disk (the file is only written when an alert fires), so in practice each watch alerts once. This is a known bug, listed in the PRD's risks.

---

## Decision 4 — Console first, desktop notification second

**Context:** `plyer` needs a desktop notification backend that headless servers and CI don't have.

**Decision:** `notify()` always prints the alert, then tries `plyer`, catching and logging any failure.

**Reason:** An alert is never silently dropped, and the daemon never crashes because of the notification layer.

**Tradeoff:** On a headless box, the alert is only as visible as the terminal it's printed to.

---

## Decision 5 — A mock price generator, also used as a fallback

**Context:** The full pipeline (polling, logging, alerting, charting) needs to run offline, in CI and on demand.

**Decision:** `fetch_price_mock()` produces a ±1.5% random walk per ticker. `--mock` uses it directly, and `get_price()` falls back to it when a live fetch fails.

**Reason:** `--mock` makes everything testable offline, and the fallback keeps the daemon from stalling when an API is briefly down.

**Tradeoff:** The automatic fallback is risky. Synthetic prices go into the real history and can trigger real-looking alerts. v2 should remove the fallback and keep mock data strictly behind `--mock`.

---

## What I'd do differently in v2

- **No silent mock fallback** — skip the tick and log an error instead.
- **Save the watch file whenever `triggered` changes**, so watches re-arm after the price moves back.
- **Store the currency with each watch** and show it in alerts.

---

## Explicit non-decisions (deferred to v2)

| Feature | Why deferred |
|---|---|
| Email / push alerts | Needs credentials or a hosted service, against the local-only goal |
| Watch removal from the CLI | Editing `watches.json` is enough for v1 |
| Running as a system service | Platform-specific (launchd / systemd). Left to the user |

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
