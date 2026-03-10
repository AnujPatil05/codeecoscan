const COMPONENTS = [
    { key: 'loop_score', label: 'Loop depth', max: 40 },
    { key: 'interaction_penalty', label: 'Interaction', max: 15 },
    { key: 'recursion', label: 'Recursion', max: 20 },
    { key: 'heavy_imports', label: 'Heavy imports', max: 25 },
]

export default function Breakdown({ assessment }) {
    const { risk_breakdown: bd } = assessment

    return (
        <div className="breakdown-section">
            <div className="breakdown-title">Score Breakdown</div>

            {COMPONENTS.map(({ key, label, max }, idx) => {
                const val = bd[key] ?? 0
                const pct = max > 0 ? (val / max) * 100 : 0

                return (
                    <div
                        className="breakdown-row"
                        key={key}
                        style={{ animationDelay: `${idx * 60}ms` }}
                    >
                        <div className="breakdown-name">{label}</div>
                        <div className="breakdown-bar-wrap">
                            <div className="breakdown-bar" style={{ width: `${pct}%` }} />
                        </div>
                        <div className={`breakdown-val ${val === 0 ? 'zero' : ''}`}>
                            {val > 0 ? `+${val}` : '—'}
                        </div>
                    </div>
                )
            })}
        </div>
    )
}
