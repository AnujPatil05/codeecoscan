import { useState, useRef } from 'react'
import useProfiling from '../../hooks/useProfiling.js'

const HEAT_THRESHOLDS = [0, 0.05, 0.1, 0.2, 0.35, 0.5]
function timeToHeat(timeMs, maxTime) {
    if (!maxTime) return 'heat-0'
    const ratio = timeMs / maxTime
    if (ratio >= 0.5) return 'heat-5'
    if (ratio >= 0.35) return 'heat-4'
    if (ratio >= 0.2) return 'heat-3'
    if (ratio >= 0.1) return 'heat-2'
    if (ratio >= 0.05) return 'heat-1'
    return 'heat-0'
}

const SAMPLE_CODE = `import pandas as pd
import numpy as np

def train(data, epochs=100):
    results = []
    for epoch in range(epochs):
        for batch in data:
            for sample in batch:
                processed = abs(sample)
                results.append(processed)
    return results

def load_data(path):
    df = pd.read_csv(path)
    df_copy = df.copy()
    return df_copy.values.tolist()
`

export default function ThermalHeatmap() {
    const [code, setCode] = useState(SAMPLE_CODE)
    const { data, loading, error, profile } = useProfiling()

    const lineTimes = data?.line_times || []
    const fnCosts = data?.function_costs || []
    const maxTime = Math.max(...lineTimes.map(l => l.time_ms), 1)

    // Build a map: lineNum → timing
    const lineMap = {}
    for (const lt of lineTimes) lineMap[lt.line] = lt

    const codeLines = code.split('\n')

    return (
        <>
            <div className="thermal-header">
                <div className="thermal-title">THERMAL HEATMAP</div>
                <div style={{ flex: 1 }} />
                <div className="thermal-legend">
                    {['COLD', '', '', '', '', 'HOT'].map((l, i) => (
                        <span key={i} className={`heat-${i}`} style={{ padding: '2px 8px', fontSize: 9, marginRight: 2 }}>{l || `L${i}`}</span>
                    ))}
                </div>
                <button
                    className="analyze-btn"
                    style={{ marginLeft: 16, padding: '6px 16px', fontSize: 10, width: 'auto' }}
                    onClick={() => profile(code)}
                    disabled={loading}
                >
                    {loading ? '▶ PROFILING…' : '▶ PROFILE'}
                </button>
            </div>

            <div className="thermal-body">
                {/* Left: code textarea + result */}
                <div className="thermal-code-area">
                    {/* Input or heatmap view */}
                    {!data ? (
                        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                            <div style={{ padding: '6px 12px', fontSize: 10, color: 'var(--muted)', borderBottom: '1px solid var(--muted)' }}>
                                PASTE CODE → CLICK PROFILE
                            </div>
                            <textarea
                                className="code-textarea"
                                style={{ flex: 1 }}
                                value={code}
                                onChange={e => setCode(e.target.value)}
                                spellCheck={false}
                            />
                            {error && <div style={{ padding: 8, fontSize: 10, color: 'var(--danger)' }}>⚠ {error}</div>}
                        </div>
                    ) : (
                        <div className="code-editor" style={{ flex: 1, overflowY: 'auto' }}>
                            <table className="thermal-code-table">
                                <tbody>
                                    {codeLines.map((text, i) => {
                                        const ln = i + 1
                                        const lt = lineMap[ln]
                                        const heat = lt ? timeToHeat(lt.time_ms, maxTime) : 'heat-0'
                                        return (
                                            <tr key={ln}>
                                                <td className="line-num">{ln}</td>
                                                <td className="th-time">{lt ? `${lt.time_ms}ms` : ''}</td>
                                                <td className={`line-code ${heat}`} title={lt ? `${lt.time_ms}ms · ${lt.category}` : ''}>
                                                    {text || '\u00A0'}
                                                </td>
                                            </tr>
                                        )
                                    })}
                                </tbody>
                            </table>
                            <div style={{ padding: 8 }}>
                                <button className="btn-small" onClick={() => profile(code)}>RE-PROFILE</button>
                                <span style={{ marginLeft: 16, fontSize: 10, color: 'var(--muted)' }}>
                                    {lineTimes.length} lines profiled
                                </span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right: function costs + metrics */}
                <div className="thermal-sidebar">
                    <div className="panel-header">FUNCTION ENERGY DRAIN</div>
                    <div className="fn-list">
                        {fnCosts.length ? fnCosts.map(f => {
                            const max = fnCosts[0]?.energy || 1
                            return (
                                <div key={f.name} className="fn-item">
                                    <div className="fn-name">{f.name}</div>
                                    <div className="fn-bar-wrap">
                                        <div className="fn-bar" style={{ width: `${Math.min((f.energy / max) * 100, 100)}%` }} />
                                    </div>
                                    <span className="fn-energy">{f.energy}μWh</span>
                                </div>
                            )
                        }) : (
                            <div style={{ padding: 12, fontSize: 10, color: 'var(--muted)' }}>Profile code to see function costs.</div>
                        )}
                    </div>

                    <div className="panel-header" style={{ marginTop: 16 }}>EXECUTION METRICS</div>
                    <div className="heat-profile">
                        {[
                            { label: 'HOTTEST LINE', val: data ? `LINE ${lineTimes.sort((a, b) => b.time_ms - a.time_ms)[0]?.line || '—'}` : '—' },
                            { label: 'PEAK TIME', val: data ? `${maxTime}ms` : '—' },
                            { label: 'TOTAL ENERGY', val: data ? `${data.total_energy}μWh` : '—' },
                            { label: 'PEAK MEMORY', val: data ? `${data.peak_memory}MB` : '—' },
                            { label: 'HOT LINES', val: data ? `${lineTimes.filter(l => l.category === 'critical').length}` : '—' },
                            { label: 'FUNCTIONS', val: data ? `${fnCosts.length}` : '—' },
                        ].map(m => (
                            <div key={m.label} className="hp-cell">
                                <div className="hp-label">{m.label}</div>
                                <div className="hp-val">{m.val}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    )
}
