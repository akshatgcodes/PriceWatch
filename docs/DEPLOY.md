# Deploying PriceWatch

> **Live:** [pricewatch.akshatgcodes.in](https://pricewatch.akshatgcodes.in) (project page) · **Host:** Vercel · **Auto-deploy:** on push to `master`

PriceWatch itself is a local daemon and isn't hosted. Only the project page in `landing/` is deployed. To install and run the daemon, see [SETUP.md](SETUP.md).

---

## 1. Architecture in production

| Piece | Runs on | Notes |
|---|---|---|
| Project page | Vercel | Next.js 16 app in `landing/` |
| Daemon | Your machine | `python pricewatch.py --run` |
| DNS | GoDaddy | `pricewatch.akshatgcodes.in` → CNAME to Vercel |

---

## 2. Environment variables

None for the project page. The daemon's settings live in your local `.env` (see [SETUP.md](SETUP.md)).

---

## 3. First-time deploy

1. [vercel.com/new](https://vercel.com/new) → import `akshatgcodes/PriceWatch`
2. Framework preset: **Next.js** · Root directory: `landing`
3. Deploy. Every push to `master` now deploys to production, and every PR gets a preview URL.

---

## 4. Custom domain

`pricewatch.akshatgcodes.in` is set up with the setup toolkit:

```powershell
.\scripts\setup-subdomain.ps1 -Subdomain "pricewatch" -Platform Vercel -VercelProject "pricewatch"
```

Manual fallback: add the domain in Vercel → Project → Domains, then create a GoDaddy CNAME `pricewatch` → the target Vercel shows. HTTPS certificates are issued automatically once DNS resolves (2–10 min).

---

## 5. Verify a deploy

- [ ] `https://pricewatch.akshatgcodes.in` loads with no console errors

---

## 6. Rollback

| Host | How |
|---|---|
| Vercel | Dashboard → Deployments → pick the last good one → **Promote to Production** (or `vercel rollback`) |

After rolling back, note it in a commit or PR so the next push doesn't silently re-ship the broken version.

---

## 7. Monitoring & logs

- **Logs:** Vercel → Project `pricewatch` → Logs
- **Dependencies:** Dependabot opens weekly update PRs for the Python packages, the project page and GitHub Actions, and a maintenance report is emailed every week (see `.github/workflows/`)

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
