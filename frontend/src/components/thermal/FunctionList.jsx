import { FUNCTIONS } from '../../data/mockData.js'

export default function FunctionList() {
    return (
        <div className="fn-list">
            {FUNCTIONS.map(f => (
                <div key={f.name} className={`fn-item${f.active ? ' active' : ''}`}>
                    <div className="fn-name">{f.name}</div>
                    <div className="fn-meta">
                        <span>{f.lines}</span>
                        <span className="fn-cost">{f.cost}</span>
                    </div>
                    <div className="fn-bar-wrap">
                        <div className="fn-bar" style={{
                            width: `${f.barPct}%`,
                            background: f.barColor,
                            boxShadow: f.barGlow || 'none',
                        }} />
                    </div>
                </div>
            ))}
        </div>
    )
}
