/** SVG sparkline showing score trend over recent analyses. */
export default function Sparkline({ history }) {
    if (history.length < 2) return null

    const W = 120, H = 32
    const pad = 2
    const xs = history.map((_, i) => pad + (i / (history.length - 1)) * (W - pad * 2))
    const ys = history.map(v => H - pad - ((v / 100) * (H - pad * 2)))

    const points = xs.map((x, i) => `${x},${ys[i]}`).join(' ')

    // Color last point by score level
    const last = history[history.length - 1]
    const color = last >= 70 ? 'var(--high-color)' : last >= 35 ? 'var(--moderate-color)' : 'var(--low-color)'

    return (
        <div className="sparkline-wrap">
            <div className="sparkline-label">Score trend</div>
            <svg width={W} height={H} className="sparkline-svg">
                <polyline
                    points={points}
                    fill="none"
                    stroke="var(--dim)"
                    strokeWidth="1"
                />
                <polyline
                    points={points}
                    fill="none"
                    stroke={color}
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    opacity="0.9"
                />
                {/* Last point dot */}
                <circle cx={xs[xs.length - 1]} cy={ys[ys.length - 1]} r="2.5" fill={color} />
            </svg>
        </div>
    )
}
