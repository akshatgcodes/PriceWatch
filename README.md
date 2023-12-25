# PriceWatch

A CLI background daemon that watches stock and crypto prices, fires a desktop
notification the instant a price crosses a threshold you set, and quietly
builds up a local price history you can chart — with zero cloud, zero
subscription, entirely yours.

## What it does

Register one or more price watches (`--asset` / `--target` / `--direction`),
then start the daemon (`--run`). PriceWatch polls each tracked asset on a
fixed interval using the `schedule` library, logs every single price check
to a per-asset CSV file, and evaluates every active watch against the
latest price. The moment a threshold is crossed it fires a desktop
notification via `plyer` and prints an equivalent console message. It
watches multiple assets simultaneously — one shared polling loop, one state
file listing every active watch.

## The X factor: history log + weekly chart

PriceWatch isn't just an alerting tool — it's a passive price tracker with
visual history:

- **CSV price history** — every price check (not just crossings) is appended
  to `data/history_<ASSET>.csv` with a timestamp, so you build a full record
  over time for free.
- **Weekly PNG chart** — `--report` (or the daemon's built-in Sunday
  23:00 schedule) reads that CSV log and uses real `matplotlib` to render a
  price-over-time chart for the current ISO week, saved to
  `reports/week_<week>_<year>_<ASSET>.png`. Nothing is a placeholder image —
  every point on the chart comes straight from the logged history.

Run `--report` at any time to regenerate the current week's charts on
demand; the daemon also schedules it automatically every Sunday at 23:00
local time while `--run` is active.

## Key concepts demonstrated

- `requests` against the **CoinGecko** public API for crypto prices (`BTC`,
  `ETH`, `DOGE`, `SOL`, `ADA`, `XRP`, `LTC`, `BNB`, `MATIC`, `USDT` — see
  `COINGECKO_IDS` in `pricewatch.py`).
- `yfinance` for any other ticker, treated as an equity/index symbol
  (`AAPL`, `INFY`, `^NSEI`, ...).
- `schedule` for interval-based polling plus a weekly cron-like job.
- `plyer` for cross-platform desktop notifications, with a console-message
  fallback that is *never* silent (see caveat below).
- `matplotlib` (headless `Agg` backend) for weekly chart generation from
  real logged CSV data.
- `.env` (via `python-dotenv`) for configuration: `COINGECKO_API_KEY`,
  `PRICEWATCH_CURRENCY`, `PRICEWATCH_INTERVAL`.
- Per-asset CSV logging and a JSON watch-state file (`data/watches.json`)
  for tracking multiple simultaneous watches.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # optional, see Configuration below
```

Requires Python 3.8+.

## Run it

Register a watch (adds it to `data/watches.json`, does not start polling):

```bash
python pricewatch.py --asset BTC --target 60000 --direction above
python pricewatch.py --asset INFY --target 1800 --direction below
```

Start the background daemon (polls all active watches, logs to CSV, alerts
on crossings, auto-generates the weekly chart every Sunday 23:00):

```bash
python pricewatch.py --run
python pricewatch.py --run --interval 300      # poll every 5 minutes (default)
python pricewatch.py --run --mock              # offline / synthetic prices, see below
```

Generate this week's chart(s) from the logged history right now:

```bash
python pricewatch.py --report
```

List active watches:

```bash
python pricewatch.py --list
```

Sample output:

```
$ python pricewatch.py --asset BTC --target 60000 --direction above
Registered watch: alert when BTC goes above ₹60,000.00

$ python pricewatch.py --run --mock --interval 5
2026-09-15 20:17:07 [INFO] Starting PriceWatch daemon (interval=5s, mock=True)
2026-09-15 20:17:07 [INFO] BTC price: 5424173.94
🔔 ALERT: BTC crossed ₹60,000 — Current: ₹7,275,404.00

$ python pricewatch.py --report
📊 Weekly report saved to reports/week_38_2026_BTC.png
```

## Configuration (`.env`)

CoinGecko's free/public tier needs no API key, but the hook is here for
anyone on a paid tier or swapping providers. Create a `.env` file in the
project root (never committed — see `.gitignore`):

```
# Optional: only needed for CoinGecko's paid Demo/Pro tiers
COINGECKO_API_KEY=

# Currency for price lookups and chart y-axis labels (CoinGecko vs_currency code)
PRICEWATCH_CURRENCY=inr

# Default polling interval in seconds for --run (overridden by --interval)
PRICEWATCH_INTERVAL=300
```

## Live vs. mocked data path — what was actually tested

Both paths are real, working code — not stubs — and both were exercised
during development:

- **Live path (tested and confirmed working):** in this build/test
  environment, outbound network access to both `https://api.coingecko.com`
  and Yahoo Finance (via `yfinance`) was available. `fetch_price_live()` was
  called directly and through the CLI: a real CoinGecko lookup for `BTC`
  returned a live INR price, and a real `yfinance` lookup for `AAPL`
  returned a live USD price. A registered `BTC` watch was polled live,
  correctly fired a threshold alert against the real price, and logged that
  real price to `data/history_BTC.csv`.
- **Mock path (tested and confirmed working):** `fetch_price_mock()` (a
  seeded random walk around a realistic base price per ticker) was used to
  (a) generate several days of backdated, multi-point-per-day history so
  the weekly chart could be verified against a realistic multi-point
  series rather than one live data point, and (b) run the full `--run`
  daemon loop for several polling ticks with `--mock`, confirming
  simultaneous multi-asset polling, CSV logging, and an `INFY` threshold
  alert firing mid-loop.
- **Automatic fallback:** `get_price()` always tries the live path first
  and transparently falls back to the mock generator (logging a warning)
  if the live call raises for any reason — rate limiting, no network, an
  unrecognized ticker, etc. This means the daemon never just stalls if a
  live API is temporarily unreachable.
- **Switching between them explicitly:** pass `--mock` on any command
  (`--run --mock`) to force the synthetic generator, e.g. for offline
  demos or CI. Omit it to use the live APIs.

## The plyer / headless-notification caveat

`plyer.notification.notify()` depends on a platform-specific backend (on
macOS that means `pyobjus`, on Linux a `notify-send`-compatible D-Bus
service, etc.), which frequently isn't installed or isn't reachable in a
headless/sandboxed/CI environment. In this build environment, the macOS
backend was in fact unavailable (`ModuleNotFoundError: No module named
'pyobjus'`).

PriceWatch handles this deliberately, not silently:

1. `notify()` **always prints the alert message to the console first**,
   before attempting the desktop notification.
2. The `plyer` call is wrapped in `try/except`; any failure is caught and
   logged as a warning (to both the console and `pricewatch.log`) instead
   of crashing the daemon or being swallowed.

So on a machine with a working notification backend you get a real desktop
popup *and* the console/log line; on a headless box you reliably still get
the console/log alert.

## Project layout

```
pricewatch.py            CLI + daemon + fetching + logging + charting
requirements.txt
.env.example
data/
  watches.json            active watch state (generated, gitignored)
  history_<ASSET>.csv      per-asset price history (generated, gitignored)
reports/
  week_<W>_<Y>_<ASSET>.png weekly charts (generated, gitignored)
pricewatch.log            runtime log (generated, gitignored)
```

Generated data/report/log files are gitignored (see `.gitignore`) since
they're per-user runtime output, not source; `data/.gitkeep` and
`reports/.gitkeep` keep the folder structure present in git.

## Known deviations from the spec

- The sample output in the spec shows a single `reports/week_49_2023.png`
  file. Since PriceWatch tracks multiple assets simultaneously, the report
  filename includes the asset symbol (`week_49_2023_BTC.png`,
  `week_49_2023_INFY.png`, ...) so each asset gets its own chart instead of
  multiple assets being overplotted on one image.
- Threshold alerts are edge-triggered per crossing: once fired, a watch
  won't re-alert until the price moves back across the threshold and
  crosses it again, to avoid spamming a notification on every single poll
  while a price sits past its target.

## Notes

Built as a focused, single-purpose tool - a price-watching CLI daemon, nothing more, nothing less.

## Troubleshooting

If something doesn't run as expected, double-check you're using the dependency versions noted above and running the exact commands from the "Run it" section.

## Possible Improvements

- More test coverage
- Better error messages for edge cases
- A cleaner CLI/UI polish pass

## Acknowledgements

Thanks to the open-source libraries this project leans on - see the dependency list above for the full set.

## License

GPLv3 - see [LICENSE](LICENSE) for details.
