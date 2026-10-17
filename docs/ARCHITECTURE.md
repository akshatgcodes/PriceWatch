# PriceWatch — Architecture

---

## 1. Stack

| Layer | Tech |
|---|---|
| Language | Python 3.8+ |
| CLI | `argparse` |
| Crypto prices | CoinGecko `GET /api/v3/simple/price` via `requests` (10 s timeout) |
| Stock / index prices | `yfinance` (`Ticker.history(period="1d")`) |
| Scheduling | `schedule` (`every(N).seconds`, `every().sunday.at("23:00")`) |
| Notifications | `plyer.notification` + `print` |
| Charts | matplotlib with the `Agg` backend |
| Config | `python-dotenv` |
| Project page | Next.js 16 static site in `landing/`, on Vercel |

---

## 2. Components

```
pricewatch.py      the whole daemon: config, price sources, watches, logging, alerts, reports, CLI
data/watches.json  registered watches (runtime, gitignored)
data/history_*.csv one price log per asset (runtime, gitignored)
reports/*.png      weekly charts (runtime, gitignored)
.env.example       COINGECKO_API_KEY, PRICEWATCH_CURRENCY, PRICEWATCH_INTERVAL
landing/           Next.js project page
```

| Function | Role |
|---|---|
| `fetch_price_live(asset)` | CoinGecko for known crypto ids, otherwise yfinance |
| `fetch_price_mock(asset)` | ±1.5% random walk from a base price per ticker |
| `get_price(asset, use_mock)` | Mock if asked, otherwise live. A live failure raises |
| `currency_code / currency_symbol(asset)` | Configured currency for crypto, the ticker's own (from yfinance metadata) for stocks |
| `add_watch / load_watches / save_watches` | Watch list in `data/watches.json` |
| `log_price(asset, price)` | Appends `timestamp, price` to the asset's CSV |
| `check_watch(watch, price)` | Crossing check + `triggered` flag |
| `notify(title, msg)` | Console print, then best-effort `plyer` |
| `run_check(use_mock)` | One tick across every distinct asset |
| `generate_report(asset?)` | Weekly PNG per asset from its CSV |

---

## 3. Data Flow

```
--asset BTC --target 6000000 --direction above
    --> add_watch --> data/watches.json

--run [--interval N] [--mock]
    schedule every N s:
        run_check
          load_watches
          for each distinct asset:
              get_price  (live → CoinGecko | yfinance; on error → skip asset)
              log_price  --> data/history_<ASSET>.csv
              for each watch on that asset:
                  check_watch --> crossed & not triggered? notify + triggered=True
          save_watches if any watch's triggered flag changed (fired or re-armed)
    schedule Sunday 23:00:
        generate_report --> reports/week_<W>_<Y>_<ASSET>.png

--report
    generate_report for every asset in watches.json or data/history_*.csv
```

---

## 4. Files

`data/watches.json`:

```json
[
  { "asset": "BTC", "target": 6000000.0, "direction": "above",
    "triggered": false, "created": "2023-12-10T21:04:11" }
]
```

`data/history_BTC.csv` gets one row per check: a timestamp and the price.

---

## 5. Security

- **Secrets:** only an optional `COINGECKO_API_KEY`, read from `.env` (gitignored) and sent as `x-cg-demo-api-key`.
- **Network:** outbound HTTPS to CoinGecko and Yahoo Finance only. There's no inbound port.
- **Local files:** everything stays in `data/` and `reports/`, which are gitignored.

---

## 6. Error Handling & Reliability

| Failure | Behaviour |
|---|---|
| CoinGecko / yfinance error | Error logged; that asset is skipped for the tick, nothing logged or alerted |
| Unexpected CoinGecko JSON | `PriceFetchError`; asset skipped for the tick |
| `plyer` unavailable or failing | Warning logged; the console alert stands |
| Corrupt `watches.json` | Error logged; starts with an empty list |
| Partial watch flags | `--asset`, `--target` and `--direction` must come together, or argparse errors |

---

## 7. Deployment

The daemon isn't hosted. It runs on your machine. The project page in `landing/` is a Vercel project with root directory `landing`, deployed on every push to `master` (see [DEPLOY.md](DEPLOY.md)).

---

## 8. Explicit Scope Cuts

- **System service integration** — run it under launchd, systemd or `tmux` yourself.
- **Other alert channels** — desktop and console only.
- **Database** — CSV and JSON files are enough for a personal tracker.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
