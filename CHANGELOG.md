# Changelog

All notable changes to **PriceWatch** are documented here.

---

## [1.0.1] — 2026-10-18

### 🐛 Fixed
- Watches now re-arm when the price moves back across the target, so the next crossing alerts again
- A failed live price fetch skips that asset for the tick instead of logging a mock price and possibly alerting on it
- Alerts and charts show each asset's own currency (stocks are no longer labelled with the crypto currency)

---

## [1.0.0] — 2026-10-18

### ✨ Added
- Price watches with an asset, a target and a direction, stored in `data/watches.json`
- Polling daemon with live prices from CoinGecko (crypto) and Yahoo Finance (stocks and indices)
- Desktop notifications on a threshold crossing, always mirrored to the console
- Per-asset CSV history of every price check
- Weekly matplotlib chart per asset, on demand and every Sunday at 23:00
- `--mock` mode for fully offline runs
- Next.js project page

---

[1.0.1]: https://github.com/akshatgcodes/PriceWatch/releases/tag/v1.0.1
[1.0.0]: https://github.com/akshatgcodes/PriceWatch/releases/tag/v1.0.0

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
