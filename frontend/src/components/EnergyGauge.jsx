const LEVEL_CLASS = { Low: 'low', Moderate: 'moderate', High: 'high' }

export default function EnergyGauge({ assessment }) {
    const { energy_risk_score: score, risk_level } = assessment
    const cls = LEVEL_CLASS[risk_level] ?? 'low'
    const fillPct = score  // score is already 0–100

    return (
        <div className="gauge-section">
            {/* Vertical bar */}
            <div className="gauge-wrap">
                <div className="gauge-track" title={`${score}/100`}>
                    <div
                        className={`gauge-fill ${cls}`}
                        style={{ height: `${fillPct}%` }}
                    />
                    <div className="gauge-ticks">
                        {[0, 1, 2, 3, 4].map(i => <div className="gauge-tick" key={i} />)}
                    </div>
                </div>
                <div className="gauge-label">PWR</div>
            </div>

            {/* Score + level */}
            <div className="gauge-info">
                <div className="score-display">
                    <div className={`score-number ${cls}`}>{score}</div>
                    <div className="score-max">/ 100</div>
                    <div className={`risk-badge ${cls}`}>{risk_level}</div>
                </div>
            </div>
        </div>
    )
}
