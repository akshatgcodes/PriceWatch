<p align="center">
  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24"
       fill="none" stroke="#34d399" stroke-width="1.5"
       stroke-linecap="round" stroke-linejoin="round">
    <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
    <polyline points="16 7 22 7 22 13"/>
  </svg>
</p>

<h1 align="center">PriceWatch</h1>

<p align="center">
  <strong>A background daemon that watches stock and crypto prices, alerts you on your desktop when a threshold is crossed, and charts the history it logs.</strong>
</p>

<p align="center">
  <a href="https://pricewatch.akshatgcodes.in">
    <img src="https://img.shields.io/badge/project_page-34d399-34d399?style=flat-square" alt="Project page">
  </a>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/CoinGecko-8DC63F?style=flat-square" alt="CoinGecko">
  <img src="https://img.shields.io/badge/yfinance-6001D2?style=flat-square" alt="yfinance">
  <img src="https://img.shields.io/badge/matplotlib-11557C?style=flat-square" alt="matplotlib">
  <img src="https://img.shields.io/badge/license-GPL--3.0-34d399?style=flat-square" alt="License">
</p>

---

## What is PriceWatch?

PriceWatch runs quietly in the background and polls the prices you care about, crypto from CoinGecko and stocks or indices from Yahoo Finance. The moment one crosses your target, it pops a desktop notification. Every check, not just the alerts, is logged to a per-asset CSV, so over time you build your own price history, and a weekly matplotlib chart is drawn from it automatically. No cloud and no subscription.

> **Project page →** [pricewatch.akshatgcodes.in](https://pricewatch.akshatgcodes.in)
> It's a local daemon: `pip install -r requirements.txt && python pricewatch.py --run --mock`

```
python pricewatch.py --asset BTC --target 6000000 --direction above
python pricewatch.py --run
🔔 ALERT: BTC crossed ₹6,000,000 — Current: ₹6,012,480.00
```

---

## What you get

- **Many watches, one loop** — register any number of `asset / target / above|below` watches, all polled together.
- **Desktop alerts** — `plyer` notifications, always mirrored to the console, so a headless machine never misses one silently.
- **Price history** — every check is appended to `data/history_<ASSET>.csv`.
- **Weekly chart** — `--report` (and automatically every Sunday at 23:00) renders `reports/week_<n>_<year>_<ASSET>.png`.
- **Offline mode** — `--mock` uses a random-walk price generator to test the whole pipeline with no network.

---

## Stack

| Layer | Tech |
|---|---|
| Language | Python 3.8+ |
| Prices | CoinGecko public API (`requests`) · Yahoo Finance (`yfinance`) |
| Scheduling | `schedule` |
| Alerts | `plyer` desktop notifications + console |
| Charts | matplotlib (headless `Agg`) |
| Storage | `data/watches.json` + per-asset CSVs |
| Project page | Next.js 16 on Vercel · GoDaddy DNS |

---

## Engineering Decisions

**Why log every check, not just crossings?**
History is a by-product of polling you're already doing. Logging it costs nothing and turns an alert tool into a price tracker with charts.

**Why alert on the crossing, not every tick above the target?**
A watch fires once when it crosses and re-arms when the price moves back. Without that, you'd get a notification every poll.

**Why always print the alert to the console?**
`plyer` fails on headless machines and in CI. The console line means an alert is never silently dropped.

**Why no fallback to mock prices?**
A failed live fetch skips that asset for the tick. Synthetic prices never reach the real history or trigger an alert; they only appear with `--mock`.

**What would you do differently in v2?**
Add `--remove` and `--edit` for watches, so the watch file never needs hand-editing.

---

## Docs

| Document | Description |
|---|---|
| [PRD](docs/PRD.md) | Product requirements — goals, user stories, non-goals |
| [Architecture](docs/ARCHITECTURE.md) | Polling loop, price sources, files |
| [Decisions](docs/DECISIONS.md) | Every major technical decision and why |
| [Setup](docs/SETUP.md) | Install, every flag, config |
| [Deploy](docs/DEPLOY.md) | How the project page is deployed |
| [Contributing](CONTRIBUTING.md) | How to propose changes |
| [Changelog](CHANGELOG.md) | What changed in each release |
| [Security](SECURITY.md) | How to report a vulnerability |

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
