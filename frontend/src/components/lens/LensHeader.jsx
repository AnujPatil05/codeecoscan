import { generateReport } from '../../utils/reportExport.js'
import AnimatedMetric from '../shared/AnimatedMetric.jsx'

export default function LensHeader({ score, refactorScore, delta, file, live }) {
    const scoreNum = score ?? 0
    const deltaVal = delta != null ? `Δ ${delta > 0 ? '+' : ''}${delta}%` : '—'
    const scoreCls = scoreNum >= 70 ? 'red' : scoreNum >= 40 ? 'yellow' : 'green'
    const isEmpty = score == null

    return (
        <div className="lens-header">
            <div className="lens-metric">
                <div className="lm-label">FILE</div>
                <div className="lm-val" style={{ color: 'var(--text)', fontSize: 13 }}>{file || '—'}</div>
            </div>
            <div className="lens-sep" />
            <div className="lens-metric">
                <div className="lm-label">ENERGY RISK SCORE</div>
                <div className={`lm-val ${isEmpty ? '' : scoreCls}`}>
                    {isEmpty ? '—' : <><AnimatedMetric value={scoreNum} /> / 100</>}
                </div>
            </div>
            <div className="lens-sep" />
            <div className="lens-metric">
                <div className="lm-label">RISK LEVEL</div>
                <div className={`lm-val ${scoreCls}`}>{live?.risk_assessment?.risk_level || (isEmpty ? '—' : 'UNKNOWN')}</div>
            </div>
            <div className="lens-sep" />
            <div className="lens-metric">
                <div className="lm-label">ISSUES FOUND</div>
                <div className="lm-val" style={{ color: 'var(--warning)', textShadow: 'var(--glow-warning)' }}>
                    {live?.issues?.length != null ? <AnimatedMetric value={live.issues.length} /> : '—'}
                </div>
            </div>
            <div className="lens-actions">
                <button
                    className="btn-small"
                    onClick={() => generateReport(live)}
                    disabled={!live}
                    title="Download HTML energy audit report"
                >
                    REPORT
                </button>
                <button
                    className="btn-small"
                    onClick={() => {
                        if (!live) return
                        const blob = new Blob([JSON.stringify(live, null, 2)], { type: 'application/json' })
                        const url = URL.createObjectURL(blob)
                        const a = document.createElement('a')
                        a.href = url; a.download = 'analysis.json'; a.click()
                        URL.revokeObjectURL(url)
                    }}
                    disabled={!live}
                >
                    JSON
                </button>
            </div>
        </div>
    )
}
