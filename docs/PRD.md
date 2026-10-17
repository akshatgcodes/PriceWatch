# PriceWatch — Product Requirements Document

**Status:** Final (v1 shipped)
**Owner:** Akshat Gupta
**One-liner:** A background daemon that watches stock and crypto prices, alerts you on your desktop when a threshold is crossed, and charts the history it logs.

---

## 1. Problem

Checking a price over and over to see whether it has hit your number is a waste of attention. Price-alert apps exist, but they're cloud services with accounts and subscriptions, and they don't hand you the history. A local tool can alert you the moment a threshold is crossed and quietly keep a record you own.

---

## 2. Goals (v1)

1. Register watches as asset + target price + direction (above / below), stored in a local file.
2. Poll every watched asset on a fixed interval (default 300 s).
3. Use CoinGecko for supported crypto tickers and Yahoo Finance for everything else.
4. Fire a desktop notification, and always a console message, when a watch crosses its target.
5. Log every price check to a per-asset CSV.
6. Render a weekly price chart per asset from that CSV, on demand and every Sunday at 23:00.
7. Run fully offline with `--mock` for testing.

---

## 3. Non-Goals (explicit scope cuts)

- **Mobile push / email / SMS alerts** — desktop and console only.
- **Portfolio tracking** — no holdings, no profit and loss.
- **Running as a system service** — you start `--run` yourself (or wrap it with launchd or systemd).
- **Removing or editing watches from the CLI** — edit `data/watches.json`.

---

## 4. Users

**Primary:** Someone who wants to know when BTC, a stock or an index crosses a level, without watching a chart all day.

**Secondary:** Engineers reviewing a small daemon that combines scheduling, two price APIs, notifications and charting.

---

## 5. User Stories

1. *As a user,* I register `BTC above 6000000` so that I'm alerted when it gets there.
2. *As a user,* I register `INFY below 1800` so that I can watch a stock and a coin at once.
3. *As a user,* I start `--run` and leave it so that alerts arrive without me checking.
4. *As a user,* I run `--report` so that I get a PNG chart of this week's prices for each asset.
5. *As a user,* I run with `--mock` on a plane so that I can test everything offline.

---

## 6. Functional Requirements

### 6.1 Watches

- `--asset --target --direction` (all three together) adds a watch to `data/watches.json`. Exact duplicates are ignored.
- `--list` prints every registered watch.

### 6.2 Polling

- `--run` schedules a check every `--interval` seconds (default from `PRICEWATCH_INTERVAL`, otherwise 300).
- Each tick fetches a price once per distinct asset, appends it to `data/history_<ASSET>.csv`, and evaluates every watch for that asset.

### 6.3 Prices

- Crypto tickers in `COINGECKO_IDS` (BTC, ETH, DOGE, SOL, ADA, XRP, LTC, BNB, MATIC, USDT) use CoinGecko `simple/price` in `PRICEWATCH_CURRENCY` (default `inr`).
- Any other ticker uses `yfinance`: the last close for today, in the ticker's own currency.
- `--mock` uses a random walk around a base price per ticker.

### 6.4 Alerts

- A watch fires when `price >= target` (above) or `price <= target` (below) and it isn't already triggered. It's then marked triggered.
- The alert is printed to the console and sent through `plyer`. A notification failure is logged and never crashes the daemon.

### 6.5 Reports

- `--report` builds one PNG per known asset from points in the current ISO week, falling back to all history if the week has none.
- The daemon also runs the report every Sunday at 23:00.

---

## 7. Non-Functional Requirements

- **Resilience:** a failed fetch for one asset doesn't stop the others. Notification failures never crash the daemon.
- **Politeness:** one request per asset per tick, at a 300 s default interval, with a 10 s timeout on CoinGecko.
- **Local-only:** all data stays in `data/` and `reports/`, which are gitignored.

---

## 8. Success Metrics

| Metric | Target |
|---|---|
| Alert latency | An alert within one polling interval of the price crossing |
| History | Every tick adds one row per asset |
| Offline | `--run --mock` exercises polling, logging and alerts with no network |

---

## 9. Risks & Open Questions

- **Silent mock fallback** — if a live fetch raises, `get_price()` logs a warning and returns a mock price. That synthetic price is logged to the real history CSV and can trigger alerts.
- **Re-arming doesn't persist** — `check_watch()` resets `triggered` when the price moves back, but the watch file is only saved when an alert fires. Watches are reloaded each tick, so the reset is lost and a watch fires at most once.
- **Mixed currencies** — stock prices come in the ticker's own currency, but alert messages use the `PRICEWATCH_CURRENCY` symbol.
- **Notifications on headless systems** — `plyer` needs a desktop backend. The console message is the fallback.

---

## 10. v2 Candidates

- Fail loudly instead of falling back to mock data, and never log mock prices to the real history.
- Save the watch file whenever `triggered` changes, so watches re-arm.
- Show each asset's real currency in alerts.
- `--remove` and `--edit` for watches.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
