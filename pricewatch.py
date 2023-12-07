#!/usr/bin/env python3
"""
PriceWatch
==========
A CLI background daemon that watches stock/crypto prices, fires desktop
notifications when a price crosses a user-defined threshold, logs every
price check to a local CSV history file, and auto-generates weekly
matplotlib price charts into /reports.

Usage examples
--------------
    python pricewatch.py --asset BTC --target 60000 --direction above
    python pricewatch.py --asset INFY --target 1800 --direction below
    python pricewatch.py --run                     # start the daemon
    python pricewatch.py --run --mock               # start with synthetic prices (offline)
    python pricewatch.py --report                  # generate this week's chart(s)
    python pricewatch.py --list                     # show active watches

See README.md for full details, including the live-vs-mock data path and
the plyer / headless-notification caveat.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import logging
import os
import random
import sys
import time
from pathlib import Path

import requests

# --------------------------------------------------------------------------
# Optional dependencies are imported defensively so the module can still be
# imported (and py_compile'd) even if a package is missing in a given
# environment. Each capability degrades gracefully and logs why.
# --------------------------------------------------------------------------
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv is optional
    pass

try:
    import yfinance as yf
except ImportError:  # pragma: no cover
    yf = None

try:
    import schedule
except ImportError:  # pragma: no cover
    schedule = None

try:
    from plyer import notification
except ImportError:  # pragma: no cover
    notification = None

import matplotlib

matplotlib.use("Agg")  # headless-safe backend, must be set before pyplot import
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# Paths & config
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
WATCHES_FILE = DATA_DIR / "watches.json"

DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "pricewatch.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("pricewatch")

# CoinGecko coin-id lookup for supported crypto tickers.
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "DOGE": "dogecoin",
    "SOL": "solana",
    "ADA": "cardano",
    "XRP": "ripple",
    "LTC": "litecoin",
    "BNB": "binancecoin",
    "MATIC": "matic-network",
    "USDT": "tether",
}

# .env-driven config. CoinGecko's free/public tier does not require a key,
# but the hook is here (and documented in README) for anyone using a paid
# tier or wanting to swap in another provider.
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", "")
CURRENCY = os.environ.get("PRICEWATCH_CURRENCY", "inr").lower()
CURRENCY_SYMBOLS = {"inr": "₹", "usd": "$", "eur": "€", "gbp": "£"}


def currency_symbol() -> str:
    return CURRENCY_SYMBOLS.get(CURRENCY, CURRENCY.upper() + " ")


# --------------------------------------------------------------------------
# Price fetching
# --------------------------------------------------------------------------
class PriceFetchError(Exception):
    """Raised when a live price lookup fails."""


def is_crypto(asset: str) -> bool:
    return asset.upper() in COINGECKO_IDS


def fetch_price_live(asset: str) -> float:
    """Fetch the current price for `asset`.

    Crypto tickers (see COINGECKO_IDS) go through the CoinGecko public API
    via `requests`. Anything else is treated as an equity/index ticker and
    is looked up through `yfinance`.
    """
    asset_u = asset.upper()
    if is_crypto(asset_u):
        coin_id = COINGECKO_IDS[asset_u]
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, "vs_currencies": CURRENCY}
        headers = {}
        if COINGECKO_API_KEY:
            headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        try:
            return float(data[coin_id][CURRENCY])
        except (KeyError, TypeError) as exc:
            raise PriceFetchError(f"Unexpected CoinGecko response: {data}") from exc
    else:
        if yf is None:
            raise PriceFetchError("yfinance is not installed")
        ticker = yf.Ticker(asset_u)
        hist = ticker.history(period="1d")
        if hist.empty:
            raise PriceFetchError(f"No data returned by yfinance for {asset_u}")
        return float(hist["Close"].iloc[-1])


_mock_state: dict[str, float] = {}


def fetch_price_mock(asset: str) -> float:
    """Generate a synthetic-but-plausible price for offline smoke testing.

    Starts from a realistic base price per known ticker and applies a small
    random walk on each call, so a sequence of calls produces a believable
    history for CSV logging and chart generation without any network access.
    """
    base_prices = {"BTC": 5_500_000.0, "ETH": 280_000.0, "INFY": 1_800.0, "AAPL": 190.0}
    base = base_prices.get(asset.upper(), 100.0)
    prev = _mock_state.get(asset.upper(), base)
    drift = prev * random.uniform(-0.015, 0.015)
    new_price = max(0.01, prev + drift)
    _mock_state[asset.upper()] = new_price
    return round(new_price, 2)


def get_price(asset: str, use_mock: bool = False) -> float:
    """Single entry point for price lookups, used by the polling loop.

    When `use_mock` is True, or when the live lookup raises, falls back to
    `fetch_price_mock` so the rest of the pipeline (logging, alerting,
    charting) can always be exercised even without network access.
    """
    if use_mock:
        return fetch_price_mock(asset)
    try:
        return fetch_price_live(asset)
    except Exception as exc:  # noqa: BLE001 - deliberately broad, we always want a fallback
        logger.warning("Live price fetch failed for %s (%s). Falling back to mock data.", asset, exc)
        return fetch_price_mock(asset)


# --------------------------------------------------------------------------
# Watch state (multi-asset)
# --------------------------------------------------------------------------
def load_watches() -> list[dict]:
    if not WATCHES_FILE.exists():
        return []
    try:
        with open(WATCHES_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Could not read %s (%s); starting with an empty watch list.", WATCHES_FILE, exc)
        return []


def save_watches(watches: list[dict]) -> None:
    with open(WATCHES_FILE, "w") as f:
        json.dump(watches, f, indent=2)


def add_watch(asset: str, target: float, direction: str) -> list[dict]:
    watches = load_watches()
    asset_u = asset.upper()
    for w in watches:
        if w["asset"] == asset_u and w["target"] == target and w["direction"] == direction:
            logger.info("Watch already registered: %s %s %s", asset_u, direction, target)
            return watches
    watches.append(
        {
            "asset": asset_u,
            "target": target,
            "direction": direction,
            "triggered": False,
            "created": datetime.datetime.now().isoformat(timespec="seconds"),
        }
    )
    save_watches(watches)
    logger.info("Registered watch: %s %s %s", asset_u, direction, target)
    return watches


# --------------------------------------------------------------------------
# CSV history logging
# --------------------------------------------------------------------------
def history_path(asset: str) -> Path:
    return DATA_DIR / f"history_{asset.upper()}.csv"


def log_price(asset: str, price: float, timestamp: str | None = None) -> None:
    timestamp = timestamp or datetime.datetime.now().isoformat(timespec="seconds")
    path = history_path(asset)
    new_file = not path.exists()
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["timestamp", "price"])
        writer.writerow([timestamp, price])


# --------------------------------------------------------------------------
# Notifications
# --------------------------------------------------------------------------
def notify(title: str, message: str) -> None:
    """Always print the alert to the console, then best-effort a desktop
    notification via plyer. Headless sandboxes / CI have no notification
    backend, so plyer failures are caught, logged, and never allowed to
    crash the daemon or silently drop the alert.
    """
    print(message)
    if notification is None:
        logger.warning("plyer not installed; console message above is the only alert.")
        return
    try:
        notification.notify(title=title, message=message, app_name="PriceWatch", timeout=10)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Desktop notification failed (%s). Console message above stands in for it.", exc)


# --------------------------------------------------------------------------
# Threshold checking
# --------------------------------------------------------------------------
def check_watch(watch: dict, price: float) -> bool:
    """Returns True if this check fired a new alert."""
    target = watch["target"]
    direction = watch["direction"]
    crossed = (direction == "above" and price >= target) or (direction == "below" and price <= target)

    if crossed and not watch.get("triggered"):
        sym = currency_symbol()
        msg = f"\U0001f514 ALERT: {watch['asset']} crossed {sym}{target:,.0f} — Current: {sym}{price:,.2f}"
        notify("PriceWatch Alert", msg)
        watch["triggered"] = True
        return True

    if not crossed and watch.get("triggered"):
        # Price moved back across the line; allow a future crossing to alert again.
        watch["triggered"] = False

    return False


def run_check(use_mock: bool = False) -> None:
    """One polling tick: fetch + log + evaluate every distinct watched asset."""
    watches = load_watches()
    if not watches:
        logger.info("No active watches registered. Use --asset/--target/--direction first.")
        return

    assets = sorted({w["asset"] for w in watches})
    state_changed = False
    for asset in assets:
        try:
            price = get_price(asset, use_mock=use_mock)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to get a price for %s: %s", asset, exc)
            continue

        log_price(asset, price)
        logger.info("%s price: %.2f", asset, price)

        for w in watches:
            if w["asset"] == asset:
                if check_watch(w, price):
                    state_changed = True

    if state_changed:
        save_watches(watches)


# --------------------------------------------------------------------------
# Weekly chart report (the X factor)
# --------------------------------------------------------------------------
def generate_report(asset: str | None = None) -> list[Path]:
    """Build a matplotlib PNG chart per tracked asset from its CSV history,
    saved into /reports as week_<isoweek>_<isoyear>_<asset>.png.

    Prefers points from the current ISO week (Mon-Sun); if the log doesn't
    have anything that recent yet, falls back to whatever history exists so
    a report can still be produced on demand.
    """
    watches = load_watches()
    if asset:
        assets = [asset.upper()]
    else:
        known = {w["asset"] for w in watches}
        known |= {p.stem.replace("history_", "") for p in DATA_DIR.glob("history_*.csv")}
        assets = sorted(known)

    if not assets:
        logger.warning("No assets to report on (no watches and no history logs).")
        return []

    today = datetime.date.today()
    iso_year, iso_week, _ = today.isocalendar()
    monday = today - datetime.timedelta(days=today.weekday())
    week_start = datetime.datetime.combine(monday, datetime.time.min)

    generated: list[Path] = []
    for a in assets:
        path = history_path(a)
        if not path.exists():
            logger.warning("No history log for %s yet, skipping report.", a)
            continue

        timestamps: list[datetime.datetime] = []
        prices: list[float] = []
        with open(path) as f:
            for row in csv.DictReader(f):
                try:
                    timestamps.append(datetime.datetime.fromisoformat(row["timestamp"]))
                    prices.append(float(row["price"]))
                except (KeyError, ValueError):
                    continue

        if not timestamps:
            logger.warning("History log for %s has no valid rows, skipping report.", a)
            continue

        points = [(t, p) for t, p in zip(timestamps, prices) if t >= week_start]
        if not points:
            points = list(zip(timestamps, prices))
        points.sort(key=lambda tp: tp[0])
        xs, ys = zip(*points)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(xs, ys, marker="o", markersize=3, linewidth=1.5, color="#2563eb")
        ax.set_title(f"{a} Price — Week {iso_week}, {iso_year}")
        ax.set_xlabel("Time")
        ax.set_ylabel(f"Price ({CURRENCY.upper()})")
        ax.grid(True, alpha=0.3)
        if min(xs) == max(xs):
            # All points share one timestamp (e.g. a burst of test data, or
            # only a single check logged so far); matplotlib's date locator
            # picks a nonsensical multi-year range in this degenerate case,
            # so pin a small explicit window around the single point instead.
            pad = datetime.timedelta(minutes=5)
            ax.set_xlim(xs[0] - pad, xs[0] + pad)
        fig.autofmt_xdate()
        fig.tight_layout()

        filename = f"week_{iso_week}_{iso_year}_{a}.png"
        out_path = REPORTS_DIR / filename
        fig.savefig(out_path, dpi=150)
        plt.close(fig)

        logger.info("Weekly report saved to %s", out_path)
        print(f"\U0001f4ca Weekly report saved to {out_path.relative_to(BASE_DIR)}")
        generated.append(out_path)

    return generated


# --------------------------------------------------------------------------
# Daemon loop
# --------------------------------------------------------------------------
def start_daemon(interval_seconds: int, use_mock: bool = False) -> None:
    if schedule is None:
        logger.error("The 'schedule' package is not installed; cannot start the polling daemon.")
        sys.exit(1)

    logger.info("Starting PriceWatch daemon (interval=%ss, mock=%s)", interval_seconds, use_mock)
    schedule.every(interval_seconds).seconds.do(run_check, use_mock=use_mock)
    schedule.every().sunday.at("23:00").do(generate_report)

    run_check(use_mock=use_mock)  # run once immediately so the user sees output right away

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("PriceWatch daemon stopped by user.")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pricewatch.py",
        description="Watch stock/crypto prices, alert on threshold crossings, log history, chart weekly trends.",
    )
    parser.add_argument("--asset", help="Asset symbol, e.g. BTC, ETH, INFY, AAPL")
    parser.add_argument("--target", type=float, help="Target price threshold")
    parser.add_argument("--direction", choices=["above", "below"], help="Alert when price goes above/below target")
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.environ.get("PRICEWATCH_INTERVAL", "300")),
        help="Polling interval in seconds for --run (default: 300, or $PRICEWATCH_INTERVAL)",
    )
    parser.add_argument("--run", action="store_true", help="Start the background polling daemon")
    parser.add_argument("--report", action="store_true", help="Generate this week's price chart(s) from logged history")
    parser.add_argument("--mock", action="store_true", help="Use synthetic mock prices instead of live APIs (offline testing)")
    parser.add_argument("--list", action="store_true", help="List all registered watches and exit")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list:
        watches = load_watches()
        if not watches:
            print("No active watches.")
        for w in watches:
            print(f"{w['asset']:6s} {w['direction']:5s} {w['target']:>14,.2f}  triggered={w.get('triggered', False)}")
        return

    partial = [args.asset, args.target, args.direction]
    if any(v is not None for v in partial) and not all(v is not None for v in partial):
        parser.error("--asset, --target, and --direction must all be given together to register a watch.")

    if args.asset and args.target is not None and args.direction:
        add_watch(args.asset, args.target, args.direction)
        sym = currency_symbol()
        print(f"Registered watch: alert when {args.asset.upper()} goes {args.direction} {sym}{args.target:,.2f}")

    did_something = bool(args.asset)

    if args.report:
        generate_report(asset=args.asset if (args.asset and not args.run) else None)
        did_something = True

    if args.run:
        start_daemon(args.interval, use_mock=args.mock)
        return

    if not did_something:
        parser.print_help()


if __name__ == "__main__":
    main()
