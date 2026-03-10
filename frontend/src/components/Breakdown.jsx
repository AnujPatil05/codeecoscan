const TOOLTIPS = {
    loop_score: 'Quadratic penalty for nested loops. Depth 3 → score 40. Deep nesting causes exponential energy growth.',
    interaction_penalty: 'Added when loops ≥ depth 2 contain function calls. Combining loops and calls compounds CPU overhead.',
    recursion: '+10 for recursive functions. +10 extra if recursion occurs inside a loop body.',
    heavy_imports: 'Libraries like torch, tensorflow, pandas, sklearn signal heavy computation. 8 pts per import, capped at 25.',
}

const COMPONENT_META = [
    { key: 'loop_score', label: 'Loop depth', max: 40 },
    { key: 'interaction_penalty', label: 'Interaction', max: 15 },
    { key: 'recursion', label: 'Recursion', max: 20 },
    { key: 'heavy_imports', label: 'Heavy imports', max: 25 },
]

function TooltipRow({ label, val, max, tooltip }) {
    const pct = max > 0 ? (val / max) * 100 : 0

    return (
        <div className="breakdown-row" title={tooltip}>
            <div className="breakdown-name">
                {label}
                <span className="tooltip-marker">?</span>
            </div>
            <div className="breakdown-bar-wrap">
                <div className="breakdown-bar" style={{ width: `${pct}%` }} />
            </div>
            <div className={`breakdown-val ${val === 0 ? 'zero' : ''}`}>
                {val > 0 ? `+${val}` : '—'}
            </div>
            {/* Tooltip bubble rendered via CSS :hover on the row */}
            <div className="tooltip-bubble">{tooltip}</div>
        </div>
    )
}

export default function Breakdown({ assessment }) {
    const { risk_breakdown: bd } = assessment

    return (
        <div className="breakdown-section">
            <div className="breakdown-title">Score Breakdown</div>

            {COMPONENT_META.map(({ key, label, max }, idx) => (
                <TooltipRow
                    key={key}
                    label={label}
                    val={bd[key] ?? 0}
                    max={max}
                    tooltip={TOOLTIPS[key]}
                    style={{ animationDelay: `${idx * 70}ms` }}
                />
            ))}
        </div>
    )
}
