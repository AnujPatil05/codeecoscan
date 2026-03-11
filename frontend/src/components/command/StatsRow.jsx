import { STATS } from '../../data/mockData.js'

export default function StatsRow() {
    return (
        <div className="cmd-stats">
            {STATS.map((s, i) => (
                <div key={i} className="stat-cell">
                    <div className="stat-label">{s.label}</div>
                    <div className={`stat-val${s.cls === 'green' ? '' : s.cls ? ` ${s.cls}` : ''}`}
                        style={s.cls === 'green' ? { color: 'var(--primary)', textShadow: 'var(--glow-primary)' } : undefined}>
                        {s.val}
                    </div>
                    <div className="stat-sub">{s.sub}</div>
                </div>
            ))}
        </div>
    )
}
