import { useEffect } from 'react'
import EmissionChart from './EmissionChart.jsx'
import useHistory from '../../hooks/useHistory.js'

export default function EmissionMatrix({ onOpenDiff }) {
    const { data: history, loading, error, fetchHistory } = useHistory()

    useEffect(() => { fetchHistory(50) }, [fetchHistory])

    const entries = history || []
    const totalRuns = entries.length
    const avgScore = totalRuns ? Math.round(entries.reduce((s, e) => s + e.score, 0) / totalRuns) : 0
    const highCount = entries.filter(e => e.risk_level === 'High').length
    const totalCo2 = entries.reduce((s, e) => s + (e.co2_kg_per_day || 0), 0).toFixed(4)

    return (
        <>
            <div className="matrix-header">
                <div className="matrix-title">EMISSION MATRIX</div>
                <div className="ms-sep" />
                <div className="matrix-stat">
                    <div className="ms-label">TOTAL ANALYSES</div>
                    <div className="ms-val green">{totalRuns}</div>
                </div>
                <div className="ms-sep" />
                <div className="matrix-stat">
                    <div className="ms-label">AVG RISK SCORE</div>
                    <div className={`ms-val ${avgScore >= 70 ? 'red' : avgScore >= 40 ? 'yellow' : 'green'}`}>{avgScore || '—'}</div>
                </div>
                <div className="ms-sep" />
                <div className="matrix-stat">
                    <div className="ms-label">HIGH RISK RUNS</div>
                    <div className="ms-val red">{highCount}</div>
                </div>
                <div className="ms-sep" />
                <div className="matrix-stat">
                    <div className="ms-label">CUMULATIVE CO₂</div>
                    <div className="ms-val red">{totalCo2} kg/day</div>
                </div>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
                    <button className="btn-small" onClick={() => fetchHistory(50)} disabled={loading}>
                        {loading ? '↺ LOADING…' : '↺ REFRESH'}
                    </button>
                    <button className="btn-small primary" onClick={() => {
                        const csv = ['id,timestamp,file,score,risk,co2',
                            ...entries.map(e => `${e.id},${e.timestamp},${e.filename},${e.score},${e.risk_level},${e.co2_kg_per_day}`)
                        ].join('\n')
                        const blob = new Blob([csv], { type: 'text/csv' })
                        const url = URL.createObjectURL(blob)
                        const a = document.createElement('a'); a.href = url; a.download = 'emissions.csv'; a.click()
                        URL.revokeObjectURL(url)
                    }}>EXPORT CSV</button>
                </div>
            </div>

            <div className="matrix-body">
                <EmissionChart entries={entries} />
                <div className="table-area">
                    {error && <div style={{ padding: 12, fontSize: 11, color: 'var(--danger)' }}>⚠ {error} — run analyses in Lens Workspace to populate history.</div>}
                    {!loading && !entries.length && !error && (
                        <div style={{ padding: 24, fontSize: 11, color: 'var(--muted)', textAlign: 'center' }}>
                            No analysis history yet.<br />Use Lens Workspace (CTRL+2) to analyze code — results appear here.
                        </div>
                    )}
                    {entries.length > 0 && (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>TIMESTAMP</th>
                                    <th>FILE</th>
                                    <th>SOURCE</th>
                                    <th>SCORE</th>
                                    <th>RISK LEVEL</th>
                                    <th>ISSUES</th>
                                    <th>CO₂ (kg/day)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {entries.map(e => {
                                    const sev = e.risk_level === 'High' ? 'risk-high' : e.risk_level === 'Moderate' ? 'risk-med' : 'risk-low'
                                    return (
                                        <tr key={e.id}>
                                            <td className="td-sha">#{e.id}</td>
                                            <td className="td-ts">{new Date(e.timestamp).toLocaleString()}</td>
                                            <td>{e.filename}</td>
                                            <td style={{ color: 'var(--muted)', fontSize: 10 }}>{e.source}</td>
                                            <td className={e.score >= 70 ? 'td-delta up' : e.score >= 40 ? '' : 'td-delta down'}>{e.score}</td>
                                            <td><span className={`td-risk ${sev}`}>{e.risk_level.toUpperCase()}</span></td>
                                            <td style={{ color: 'var(--warning)' }}>{e.issue_count}</td>
                                            <td style={{ color: 'var(--muted)', fontSize: 10 }}>{e.co2_kg_per_day}</td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </>
    )
}
