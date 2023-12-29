import TerminalWindow from "@/app/components/TerminalWindow";
import Sparkline from "@/app/components/Sparkline";
import Badge from "@/app/components/Badge";

const CONCEPTS = [
  "Python 3.8+",
  "yfinance",
  "CoinGecko API",
  "schedule",
  "plyer",
  "matplotlib",
  "CSV logging",
  ".env config",
  "GPLv3",
];

const FEATURES = [
  {
    title: "Multi-asset watches",
    body: "Register any number of stocks or crypto tickers at once. One shared polling loop, one watch-state file (data/watches.json) tracks every active threshold.",
  },
  {
    title: "Edge-triggered alerts",
    body: "A crossing fires once, not on every poll. The watch won't re-alert until price moves back across the threshold and crosses it again — no notification spam.",
  },
  {
    title: "Background daemon",
    body: "python pricewatch.py --run starts an interval-based polling loop via the schedule library and keeps tracking every registered asset until you stop it.",
  },
  {
    title: "Desktop notifications, never silent",
    body: "Alerts fire through plyer for a native popup, but the console/log line prints first and always — so headless boxes still get a reliable alert.",
  },
  {
    title: "Live prices, mock fallback",
    body: "CoinGecko for crypto, yfinance for everything else. If a live call fails for any reason, PriceWatch transparently falls back to a seeded mock generator instead of stalling.",
  },
  {
    title: "Configurable via .env",
    body: "Set PRICEWATCH_CURRENCY, PRICEWATCH_INTERVAL, and an optional COINGECKO_API_KEY without touching code.",
  },
];

export default function Home() {
  return (
    <div className="min-h-full bg-[#05070a] text-zinc-100">
      {/* ambient glow */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-x-0 top-0 -z-10 h-[520px] bg-[radial-gradient(ellipse_60%_50%_at_50%_-10%,rgba(52,211,153,0.16),transparent)]"
      />

      {/* nav */}
      <header className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-6 sm:px-8">
        <div className="flex items-center gap-2 font-mono text-sm font-medium text-zinc-200">
          <span className="text-emerald-400">$</span> pricewatch
        </div>
        <nav className="hidden gap-6 font-mono text-xs text-zinc-400 sm:flex">
          <a href="#x-factor" className="transition-colors hover:text-zinc-100">
            x-factor
          </a>
          <a href="#features" className="transition-colors hover:text-zinc-100">
            features
          </a>
          <a href="#run-it" className="transition-colors hover:text-zinc-100">
            run it
          </a>
        </nav>
      </header>

      <main className="mx-auto w-full max-w-5xl px-6 sm:px-8">
        {/* hero */}
        <section className="flex flex-col items-start gap-6 pt-10 pb-20 sm:pt-16 sm:pb-28">
          <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/[0.06] px-3 py-1 font-mono text-xs text-emerald-300">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            CLI daemon · desktop alerts · zero cloud
          </span>

          <h1 className="text-4xl font-semibold tracking-tight text-zinc-50 sm:text-6xl">
            PriceWatch
          </h1>

          <p className="max-w-2xl font-mono text-base text-zinc-400 sm:text-lg">
            Set a price. Walk away. Get pinged the second it crosses.
          </p>

          <p className="max-w-2xl text-base leading-7 text-zinc-400">
            A background daemon that watches stocks and crypto simultaneously,
            fires a desktop notification the instant a threshold you set is
            crossed, and quietly builds a local price history you can chart —
            entirely on your own machine. No dashboard to host, no account to
            create, no subscription to cancel.
          </p>

          <div className="flex flex-wrap gap-2 pt-2">
            {CONCEPTS.map((c) => (
              <Badge key={c}>{c}</Badge>
            ))}
          </div>

          <div className="w-full pt-8">
            <TerminalWindow />
          </div>
        </section>

        {/* x factor */}
        <section id="x-factor" className="scroll-mt-20 border-t border-white/10 py-20">
          <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
            <div className="flex flex-col gap-5">
              <span className="font-mono text-xs uppercase tracking-widest text-emerald-400">
                the x factor
              </span>
              <h2 className="text-2xl font-semibold text-zinc-50 sm:text-3xl">
                Not just alerts — a passive price tracker with visual history
              </h2>
              <p className="text-base leading-7 text-zinc-400">
                Most threshold-alert scripts throw away every price they
                check the moment they check it. PriceWatch doesn&apos;t.
              </p>
              <ul className="flex flex-col gap-4 pt-2">
                <li className="flex gap-3">
                  <span className="mt-1 text-emerald-400">▸</span>
                  <span className="text-sm leading-6 text-zinc-300">
                    <strong className="text-zinc-100">
                      CSV price-history log —
                    </strong>{" "}
                    every single price check, not just crossings, is appended
                    to{" "}
                    <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-xs text-zinc-200">
                      data/history_&lt;ASSET&gt;.csv
                    </code>{" "}
                    with a timestamp — a full record, built for free.
                  </span>
                </li>
                <li className="flex gap-3">
                  <span className="mt-1 text-emerald-400">▸</span>
                  <span className="text-sm leading-6 text-zinc-300">
                    <strong className="text-zinc-100">
                      Auto-generated weekly chart —
                    </strong>{" "}
                    real{" "}
                    <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-xs text-zinc-200">
                      matplotlib
                    </code>{" "}
                    reads that CSV and renders a price-over-time{" "}
                    <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-xs text-zinc-200">
                      .png
                    </code>{" "}
                    to{" "}
                    <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-xs text-zinc-200">
                      /reports
                    </code>{" "}
                    every Sunday at 23:00 — or on demand with{" "}
                    <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-xs text-zinc-200">
                      --report
                    </code>
                    . Every point on the chart comes from real logged
                    history, never a placeholder.
                  </span>
                </li>
              </ul>
              <p className="pt-2 text-sm leading-6 text-zinc-500">
                Zero cloud. Zero subscription. A local CSV, a local PNG, and a
                daemon that never phones home.
              </p>
            </div>

            <div className="overflow-hidden rounded-xl border border-white/10 bg-[#0b0f14] p-5">
              <div className="mb-4 flex items-center justify-between font-mono text-xs text-zinc-500">
                <span>reports/week_38_2026_BTC.png</span>
                <span className="text-emerald-400">matplotlib · Agg</span>
              </div>
              <Sparkline />
              <div className="mt-4 flex items-center justify-between font-mono text-[11px] text-zinc-600">
                <span>mon</span>
                <span>tue</span>
                <span>wed</span>
                <span>thu</span>
                <span>fri</span>
                <span>sat</span>
                <span>sun</span>
              </div>
            </div>
          </div>
        </section>

        {/* features */}
        <section id="features" className="scroll-mt-20 border-t border-white/10 py-20">
          <div className="mb-12 flex flex-col gap-3">
            <span className="font-mono text-xs uppercase tracking-widest text-emerald-400">
              how it works
            </span>
            <h2 className="text-2xl font-semibold text-zinc-50 sm:text-3xl">
              One daemon, every threshold you care about
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="rounded-xl border border-white/10 bg-white/[0.02] p-5 transition-colors hover:border-emerald-400/30 hover:bg-white/[0.04]"
              >
                <h3 className="mb-2 text-sm font-semibold text-zinc-100">
                  {f.title}
                </h3>
                <p className="text-sm leading-6 text-zinc-400">{f.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* run it */}
        <section id="run-it" className="scroll-mt-20 border-t border-white/10 py-20">
          <div className="mb-10 flex flex-col gap-3">
            <span className="font-mono text-xs uppercase tracking-widest text-emerald-400">
              run it
            </span>
            <h2 className="text-2xl font-semibold text-zinc-50 sm:text-3xl">
              From clone to first alert in five commands
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-white/10 bg-[#0b0f14] p-5">
              <p className="mb-3 font-mono text-xs text-zinc-500">setup</p>
              <pre className="overflow-x-auto font-mono text-[13px] leading-7 text-zinc-300">
                <code>
                  <span className="text-zinc-600">$ </span>python3 -m venv .venv{"\n"}
                  <span className="text-zinc-600">$ </span>source .venv/bin/activate{"\n"}
                  <span className="text-zinc-600">$ </span>pip install -r requirements.txt{"\n"}
                  <span className="text-zinc-600">$ </span>cp .env.example .env
                </code>
              </pre>
            </div>

            <div className="rounded-xl border border-white/10 bg-[#0b0f14] p-5">
              <p className="mb-3 font-mono text-xs text-zinc-500">usage</p>
              <pre className="overflow-x-auto font-mono text-[13px] leading-7 text-zinc-300">
                <code>
                  <span className="text-zinc-600">$ </span>python pricewatch.py --asset BTC \{"\n"}
                  {"    "}--target 60000 --direction above{"\n"}
                  <span className="text-zinc-600">$ </span>python pricewatch.py --run{"\n"}
                  <span className="text-zinc-600">$ </span>python pricewatch.py --report{"\n"}
                  <span className="text-zinc-600">$ </span>python pricewatch.py --list
                </code>
              </pre>
            </div>
          </div>

          <p className="mt-6 max-w-2xl text-sm leading-6 text-zinc-500">
            <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-xs text-zinc-300">
              --run --mock
            </code>{" "}
            forces the seeded synthetic price generator for offline demos or
            CI; omit it to hit CoinGecko and yfinance live.
          </p>
        </section>
      </main>

      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto flex w-full max-w-5xl flex-col items-start justify-between gap-3 px-6 font-mono text-xs text-zinc-600 sm:flex-row sm:items-center sm:px-8">
          <span>pricewatch.py · Python CLI daemon</span>
          <span>Licensed under GPLv3</span>
        </div>
      </footer>
    </div>
  );
}
