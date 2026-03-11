export default function Suggestions({ items }) {
    if (!items?.length) return null

    const SEV_DOTS = { high: '●', medium: '◆', low: '◇' }

    return (
        <div className="suggestions-panel">
            <div className="sug-title">OPTIMIZATION SUGGESTIONS</div>
            {items.map((s, i) => (
                <div key={i} className="sug-item">
                    <div className="sug-item-head">
                        <span className={`sug-dot ${s.severity}`}>{SEV_DOTS[s.severity] || '●'}</span>
                        <span style={{ color: s.severity === 'high' ? 'var(--danger)' : s.severity === 'medium' ? 'var(--warning)' : 'var(--primary)' }}>
                            {s.title}
                        </span>
                    </div>
                    <div className="sug-item-detail">{s.detail}</div>
                </div>
            ))}
        </div>
    )
}
