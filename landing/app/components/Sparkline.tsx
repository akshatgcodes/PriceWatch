/**
 * A lightweight, illustrative nod to the auto-generated matplotlib weekly
 * chart — a hand-drawn inline SVG, not a real chart or a charting library.
 */
export default function Sparkline() {
  const points = [
    [0, 78],
    [40, 70],
    [80, 74],
    [120, 58],
    [160, 62],
    [200, 40],
    [240, 46],
    [280, 22],
    [320, 30],
    [360, 12],
  ];

  const linePath = points
    .map(([x, y], i) => `${i === 0 ? "M" : "L"}${x},${y}`)
    .join(" ");

  const areaPath = `${linePath} L360,110 L0,110 Z`;
  const thresholdY = 50;
  const crossIndex = points.findIndex(([, y]) => y <= thresholdY);
  const crossPoint = points[crossIndex];

  return (
    <svg
      viewBox="0 0 360 110"
      className="h-auto w-full"
      role="img"
      aria-label="Illustrative weekly price chart with a threshold crossing marked"
    >
      <defs>
        <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#34d399" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#34d399" stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* gridlines */}
      {[20, 50, 80].map((y) => (
        <line
          key={y}
          x1="0"
          y1={y}
          x2="360"
          y2={y}
          stroke="currentColor"
          className="text-white/5"
          strokeWidth="1"
        />
      ))}

      {/* threshold line */}
      <line
        x1="0"
        y1={thresholdY}
        x2="360"
        y2={thresholdY}
        stroke="#f59e0b"
        strokeWidth="1.5"
        strokeDasharray="4 4"
        opacity="0.7"
      />
      <text x="4" y={thresholdY - 6} className="fill-amber-400 text-[9px] font-mono">
        target
      </text>

      {/* area + line */}
      <path d={areaPath} fill="url(#sparkFill)" />
      <path
        d={linePath}
        fill="none"
        stroke="#34d399"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* crossing marker */}
      {crossPoint && (
        <>
          <circle cx={crossPoint[0]} cy={crossPoint[1]} r="4.5" fill="#0b0f14" stroke="#34d399" strokeWidth="2" />
          <circle cx={crossPoint[0]} cy={crossPoint[1]} r="2" fill="#34d399" />
        </>
      )}
    </svg>
  );
}
