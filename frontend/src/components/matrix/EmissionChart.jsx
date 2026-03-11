/**
 * EmissionChart — brutalist SVG chart built from real /analysis/history data.
 * If no entries, shows an empty grid with a "NO DATA" message.
 */
export default function EmissionChart({ entries = [] }) {
    const W = 900, H = 200, PAD_L = 45, PAD_B = 20, PAD_T = 20, PAD_R = 10
    const chartW = W - PAD_L - PAD_R
    const chartH = H - PAD_T - PAD_B

    // Build points from most recent 20 entries (oldest first)
    const recent = [...entries].reverse().slice(0, 20)
    const hasData = recent.length > 0
    const maxCo2 = hasData ? Math.max(...recent.map(e => e.co2_kg_per_day), 0.01) : 1

    const pts = recent.map((e, i) => {
        const x = PAD_L + (i / Math.max(recent.length - 1, 1)) * chartW
        const y = PAD_T + (1 - e.co2_kg_per_day / maxCo2) * chartH
        return [x, y]
    })

    const polyline = pts.map(p => p.join(',')).join(' ')
    const polyFill = hasData
        ? `${polyline} ${PAD_L + chartW},${PAD_T + chartH} ${PAD_L},${PAD_T + chartH}`
        : ''

    // Y-axis labels
    const yLabels = [0, 0.25, 0.5, 0.75, 1.0].map(f => ({
        y: PAD_T + (1 - f) * chartH,
        t: (f * maxCo2).toFixed(3),
    }))

    return (
        <div className="chart-area">
            <svg width="100%" height="100%" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" style={{ display: 'block' }}>
                <defs>
                    <linearGradient id="chartGrad2" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#00FF41" stopOpacity="0.15" />
                        <stop offset="100%" stopColor="#00FF41" stopOpacity="0" />
                    </linearGradient>
                    <filter id="glow2">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                        <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
                    </filter>
                </defs>

                {/* Y-axis label */}
                <text x="10" y={H / 2} fill="#4A4A4A" fontFamily="JetBrains Mono" fontSize="9"
                    transform={`rotate(-90, 10, ${H / 2})`} textAnchor="middle">kgCO₂/day</text>

                {/* Grid + y labels */}
                {yLabels.map(l => (
                    <g key={l.y}>
                        <line x1={PAD_L} y1={l.y} x2={W - PAD_R} y2={l.y} stroke="#4A4A4A" strokeWidth="0.5" />
                        <text x={PAD_L - 4} y={l.y + 3} fill="#4A4A4A" fontFamily="JetBrains Mono" fontSize="9" textAnchor="end">{l.t}</text>
                    </g>
                ))}

                {hasData ? (
                    <>
                        <polygon points={polyFill} fill="url(#chartGrad2)" />
                        <polyline points={polyline} fill="none" stroke="#00FF41" strokeWidth="2" strokeLinejoin="miter" filter="url(#glow2)" />
                        {pts.map(([x, y], i) => (
                            <circle key={i} cx={x} cy={y} r="3" fill={recent[i].risk_level === 'High' ? '#FF003C' : '#FFB000'} />
                        ))}
                    </>
                ) : (
                    <text x={W / 2} y={H / 2} fill="#4A4A4A" fontFamily="JetBrains Mono" fontSize="11" textAnchor="middle">
                        NO DATA — analyze code in Lens Workspace to populate chart
                    </text>
                )}
            </svg>
        </div>
    )
}
