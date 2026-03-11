import { HEAT_METRICS } from '../../data/mockData.js'

export default function HeatProfile() {
    return (
        <div className="heat-profile">
            <div className="hp-title">EXECUTION PROFILE</div>
            <div className="hp-grid">
                {HEAT_METRICS.map(m => (
                    <div key={m.label} className="hp-cell">
                        <div className="hp-cell-label">{m.label}</div>
                        <div className="hp-cell-val" style={m.fontSize ? { fontSize: m.fontSize } : undefined}>
                            {m.val}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
