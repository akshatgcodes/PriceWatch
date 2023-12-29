export default function TerminalWindow() {
  return (
    <div className="w-full overflow-hidden rounded-xl border border-white/10 bg-[#0b0f14] shadow-2xl shadow-black/40">
      <div className="flex items-center gap-2 border-b border-white/10 bg-white/[0.03] px-4 py-3">
        <span className="h-3 w-3 rounded-full bg-[#ff5f56]" />
        <span className="h-3 w-3 rounded-full bg-[#ffbd2e]" />
        <span className="h-3 w-3 rounded-full bg-[#27c93f]" />
        <span className="ml-3 font-mono text-xs text-zinc-500">
          zsh — pricewatch.py
        </span>
      </div>
      <pre className="overflow-x-auto px-5 py-5 font-mono text-[13px] leading-6 text-zinc-300 sm:text-sm">
        <code>
          <span className="text-zinc-600">$ </span>
          <span className="text-zinc-200">
            python pricewatch.py --asset BTC --target 60000 --direction above
          </span>
          {"\n"}
          <span className="text-zinc-600">$ </span>
          <span className="text-zinc-200">
            python pricewatch.py --asset INFY --target 1800 --direction below
          </span>
          {"\n"}
          <span className="text-zinc-600">$ </span>
          <span className="text-zinc-200">python pricewatch.py --report</span>
          <span className="text-zinc-600">
            {"          "}# generate this week&apos;s chart
          </span>
          {"\n\n"}
          <span className="text-emerald-400">
            🔔 ALERT: BTC crossed ₹60,000 — Current: ₹60,412
          </span>
          {"\n"}
          <span className="text-sky-400">
            📊 Weekly report saved to reports/week_49_2023.png
          </span>
          <span className="animate-pulse text-zinc-500">▋</span>
        </code>
      </pre>
    </div>
  );
}
