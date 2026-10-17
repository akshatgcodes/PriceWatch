# Local Setup — PriceWatch

> **Project page:** [pricewatch.akshatgcodes.in](https://pricewatch.akshatgcodes.in)
> PriceWatch is a local daemon, so it runs on your machine. This guide covers installing, configuring and running it.

---

## Prerequisites

- Python 3.8+
- A desktop session for notifications. On headless machines, alerts are printed to the console instead

---

## 1. Clone and install

```bash
git clone https://github.com/akshatgcodes/PriceWatch
cd PriceWatch
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Environment variables

```bash
cp .env.example .env   # optional
```

| Variable | Where to get it |
|---|---|
| `COINGECKO_API_KEY` | Optional. Only for CoinGecko's paid Demo / Pro tiers. The free tier needs no key |
| `PRICEWATCH_CURRENCY` | Optional. CoinGecko `vs_currency` code, default `inr` |
| `PRICEWATCH_INTERVAL` | Optional. Polling interval in seconds, default `300` |

---

## 3. Run

```bash
# register watches (saved to data/watches.json)
python pricewatch.py --asset BTC --target 6000000 --direction above
python pricewatch.py --asset INFY --target 1800 --direction below
python pricewatch.py --list

# start the daemon
python pricewatch.py --run
python pricewatch.py --run --interval 60
python pricewatch.py --run --mock --interval 5   # offline, synthetic prices

# this week's charts, written to reports/
python pricewatch.py --report
```

| Flag | What it does |
|---|---|
| `--asset`, `--target`, `--direction above\|below` | Register a watch (all three together) |
| `--list` | Show registered watches |
| `--run` | Start polling; also schedules the weekly report for Sunday 23:00 |
| `--interval N` | Seconds between checks (overrides `PRICEWATCH_INTERVAL`) |
| `--mock` | Use synthetic prices instead of live APIs |
| `--report` | Generate this week's chart for each asset |

Supported crypto tickers: BTC, ETH, DOGE, SOL, ADA, XRP, LTC, BNB, MATIC, USDT. Any other symbol (`AAPL`, `INFY`, `^NSEI`) goes to Yahoo Finance.

---

## 4. Project page (optional)

```bash
cd landing && npm install && npm run dev   # http://localhost:3000
```

See [DEPLOY.md](DEPLOY.md) for how it's hosted.

---

## Testing

There's no automated test suite yet. CI checks that every Python file compiles and that the project page lints and builds. To check a change by hand, register a watch near a mock base price (for example `--asset INFY --target 1800 --direction above`), run `--run --mock --interval 5` for a few ticks, and confirm rows appear in `data/history_INFY.csv` and an alert fires. Then run `--report` and open the PNG in `reports/`.

---

## Known limitations

- If a live fetch fails, PriceWatch silently switches to mock prices for that tick, and those prices are logged to your history.
- A watch only alerts once, because the re-arm after the price moves back isn't saved.
- Stock prices are in the ticker's own currency, but alerts show the `PRICEWATCH_CURRENCY` symbol.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
