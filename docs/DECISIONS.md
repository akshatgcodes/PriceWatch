# Engineering Decisions — PriceWatch

---

## Decision 1 — Two price sources, chosen by ticker

**Context:** Crypto and stocks live in different APIs, and the user shouldn't have to say which is which.

**Decision:** Tickers in `COINGECKO_IDS` go to CoinGecko's free `simple/price` endpoint in `PRICEWATCH_CURRENCY`. Everything else goes to `yfinance` as an equity or index symbol.

**Reason:** `--asset BTC` and `--asset INFY` just work. CoinGecko's public tier needs no key, and yfinance covers global tickers and indices like `^NSEI`.

**Tradeoff:** Prices come in different currencies, so each asset's currency is tracked: CoinGecko in the configured one, stocks in the currency yfinance reports. Crypto symbols outside the map need adding by hand.

---

## Decision 2 — Log every check, not only alerts

**Context:** The daemon already fetches a price every interval.

**Decision:** Every fetched price is appended to `data/history_<ASSET>.csv`, whether or not it crosses anything.

**Reason:** The history is free. It feeds the weekly chart and turns an alert tool into a personal price tracker.

**Tradeoff:** The CSVs grow forever at one row per asset per interval: about 288 rows a day at the default 5 minutes.

---

## Decision 3 — Alert on the crossing, with a triggered flag

**Context:** Alerting on every tick above the target would spam the user.

**Decision:** `check_watch()` fires only when the price is past the target and the watch isn't already triggered, then sets `triggered`. It resets when the price moves back, and `run_check()` saves the file whenever the flag flips either way.

**Reason:** One notification per crossing is what a user expects, and re-arming means the next crossing alerts again.

**Tradeoff:** A price hovering right at the target can alert repeatedly as it crosses back and forth. A small hysteresis band would fix that.

---

## Decision 4 — Console first, desktop notification second

**Context:** `plyer` needs a desktop notification backend that headless servers and CI don't have.

**Decision:** `notify()` always prints the alert, then tries `plyer`, catching and logging any failure.

**Reason:** An alert is never silently dropped, and the daemon never crashes because of the notification layer.

**Tradeoff:** On a headless box, the alert is only as visible as the terminal it's printed to.

---

## Decision 5 — Mock prices only behind `--mock`

**Context:** The full pipeline (polling, logging, alerting, charting) needs to run offline, in CI and on demand. An earlier version also fell back to mock prices whenever a live fetch failed.

**Decision:** `fetch_price_mock()` produces a ±1.5% random walk per ticker, used only with `--mock`. A failed live fetch now skips the asset for that tick.

**Reason:** The fallback put synthetic prices into the real history and could fire real-looking alerts. Missing one tick is better than a wrong price.

**Tradeoff:** During an API outage there's a gap in the history and no alerts for that asset.

---

## What I'd do differently in v2

- **Hysteresis** around the target, so a price hovering at the line doesn't alert on every wobble.
- **Retry a failed fetch once** before skipping the tick.
- **`--remove` / `--edit`** for watches.

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
