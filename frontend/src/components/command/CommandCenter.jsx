import { useState } from 'react'
import { useCarbonClock } from '../../hooks/useClock.js'
import useRepoSummary from '../../hooks/useRepoSummary.js'

export default function CommandCenter({ onOpenDiff, onInitiateLens }) {
    const [repoUrl, setRepoUrl] = useState('')
    const { data, loading, status, elapsed, error, fetchSummary } = useRepoSummary()
    const clockDisplay = useCarbonClock(data?.energy_risk ? data.energy_risk * 0.049 : 4.892)

    const handleScan = () => { if (repoUrl.trim()) fetchSummary(repoUrl.trim()) }

    const scanLabel = loading
        ? (status === 'running' ? `▶ SCANNING… ${elapsed}s` : '▶ QUEUED…')
        : '▶ SCAN REPO'

    const topFiles = data?.top_files || []
    const alerts = data?.alerts || []
    const stats = [
        { label: 'ENERGY RISK SCORE', val: data?.energy_risk ?? '—', sub: `/ 100 — ${data ? (data.energy_risk >= 70 ? 'HIGH' : data.energy_risk >= 40 ? 'MODERATE' : 'LOW') : 'AWAITING SCAN'}`, cls: data?.energy_risk >= 70 ? 'danger' : data?.energy_risk >= 40 ? 'warn' : '' },
        { label: 'FILES SCANNED', val: data?.files_scanned ?? '—', sub: 'PYTHON FILES ANALYZED', cls: '' },
        { label: 'ENERGY / DAY', val: data?.energy_per_day ?? '—', sub: 'WH / DAY (ESTIMATE)', cls: 'warn' },
        { label: 'CO₂ SAVED', val: data?.co2_saved ?? '—', sub: 'KG SAVED THIS SESSION', cls: 'green' },
    ]

    return (
        <>
            {/* Sidebar */}
            <div className="cmd-sidebar">
                <div className="cmd-sidebar-label">REPOSITORY SCAN</div>
                <div style={{ padding: '0 12px 12px' }}>
                    <input
                        type="text"
                        style={{
                            width: '100%', background: 'var(--bg)', border: '1px solid var(--muted)',
                            color: 'var(--text)', fontFamily: 'var(--font-body)', fontSize: 11,
                            padding: '8px', outline: 'none', marginBottom: 8, boxSizing: 'border-box',
                        }}
                        placeholder="https://github.com/user/repo"
                        value={repoUrl}
                        onChange={e => setRepoUrl(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleScan()}
                    />
                    <button
                        className="analyze-btn"
                        style={{ fontSize: 10, padding: '8px' }}
                        onClick={handleScan}
                        disabled={loading || !repoUrl.trim()}
                    >
                        {scanLabel}
                    </button>
                    {loading && (
                        <div style={{ fontSize: 10, color: 'var(--primary)', marginTop: 6 }}>
                            ▶ {status?.toUpperCase()} — {elapsed}s elapsed
                        </div>
                    )}
                    {error && <div style={{ fontSize: 10, color: 'var(--danger)', marginTop: 6, lineHeight: 1.4 }}>⚠ {error}</div>}
                </div>

                <div className="cmd-sidebar-label" style={{ marginTop: 8 }}>RECENT</div>
                {data && (
                    <div className="cmd-sidebar-item active">
                        <span className="si-icon">▶</span> {data.repo_name}
                    </div>
                )}
                {!data && <div style={{ padding: '8px 16px', fontSize: 10, color: 'var(--muted)' }}>No scans yet.</div>}

                <div className="cmd-sidebar-bottom">
                    <div className="sys-metric">STATUS <span className="sys-metric-val" style={{ color: 'var(--primary)' }}>LIVE</span></div>
                    <div className="sys-metric">API <span className="sys-metric-val" style={{ color: 'var(--primary)' }}>CONNECTED</span></div>
                </div>
            </div>

            {/* Main area */}
            <div className="cmd-main">
                <div className="cmd-main-top">
                    <div className="carbon-clock-wrap">
                        <div className="cmd-label">CARBON DEBT — {data?.repo_name || 'SCAN A REPOSITORY'}</div>
                        <div className="carbon-clock">{clockDisplay}</div>
                        <div className="carbon-clock-unit">kgCO₂ / YEAR — TICKING</div>
                        <button className="cmd-scan-btn" onClick={onInitiateLens} style={{ marginTop: 20 }}>
                            <span className="btn-icon">⊕</span> OPEN LENS WORKSPACE
                        </button>
                    </div>

                    <div className="cmd-alert-box">
                        <div className="alert-header">
                            <div className="alert-blink" />
                            {alerts.length > 0 ? `ACTIVE ALERTS — ${alerts.length}` : 'NO ACTIVE ALERTS'}
                        </div>
                        {alerts.length > 0 ? alerts.slice(0, 5).map((a, i) => (
                            <div key={i} className="alert-item">
                                <span>{a.file}: {a.issue}</span>
                                <span className="alert-tag">HIGH</span>
                            </div>
                        )) : (
                            <div className="alert-item">
                                <span style={{ color: 'var(--muted)' }}>{loading ? scanLabel : 'Scan a repo to see energy alerts.'}</span>
                            </div>
                        )}
                    </div>
                </div>

                <div className="cmd-stats">
                    {stats.map((s, i) => (
                        <div key={i} className="stat-cell">
                            <div className="stat-label">{s.label}</div>
                            <div className={`stat-val${s.cls ? ` ${s.cls}` : ''}`}
                                style={s.cls === 'green' ? { color: 'var(--primary)', textShadow: 'var(--glow-primary)' } : undefined}>
                                {s.val}
                            </div>
                            <div className="stat-sub">{s.sub}</div>
                        </div>
                    ))}
                </div>

                <div className="cmd-log-area">
                    <div className="log-header">TOP ENERGY OFFENDERS — CLICK TO ANALYZE IN LENS</div>
                    {topFiles.length ? topFiles.map((f, i) => (
                        <div key={i} className="log-entry" onClick={onInitiateLens} style={{ cursor: 'pointer' }}>
                            <span className="log-ts">#{i + 1}</span>
                            <span className="log-sha">{f.score}/100</span>
                            <span className="log-msg">{f.file}</span>
                            <span className="log-author">{data?.repo_name}</span>
                            <span className={`log-delta ${f.score >= 70 ? 'up' : 'down'}`}>
                                {f.score >= 70 ? 'HIGH' : f.score >= 40 ? 'MOD' : 'LOW'}
                            </span>
                        </div>
                    )) : (
                        <div style={{ padding: '24px', fontSize: 11, color: 'var(--muted)', textAlign: 'center' }}>
                            {loading ? `▶ ${status?.toUpperCase()} — analyzing ${elapsed}s…` : 'Enter a GitHub repo URL and click SCAN REPO.'}
                        </div>
                    )}
                </div>
            </div>

            {/* Right panel */}
            <div className="cmd-right">
                <div className="panel-header">TOP ENERGY OFFENDERS</div>
                <div className="top-files">
                    {topFiles.slice(0, 6).map(f => {
                        const color = f.score >= 70 ? 'var(--danger)' : f.score >= 40 ? 'var(--warning)' : 'var(--primary)'
                        const glow = f.score >= 70 ? 'var(--glow-danger)' : f.score >= 40 ? 'var(--glow-warning)' : 'var(--glow-primary)'
                        return (
                            <div key={f.file} className="file-item">
                                <div className="file-name">{f.file}</div>
                                <div className="file-bar-wrap">
                                    <div className="file-bar" style={{ width: `${f.score}%`, background: color, boxShadow: glow }} />
                                </div>
                                <div className="file-meta">
                                    <span style={{ fontSize: 10, color: 'var(--muted)' }}>RISK</span>
                                    <span className="file-score" style={{ color, textShadow: glow }}>{f.score} / 100</span>
                                </div>
                            </div>
                        )
                    })}
                    {!topFiles.length && (
                        <div style={{ padding: 16, fontSize: 11, color: 'var(--muted)' }}>
                            {loading ? `${status?.toUpperCase()}…` : 'Scan a repo to see files.'}
                        </div>
                    )}
                </div>
                <div className="mini-chart">
                    <div className="mini-chart-label">ENERGY TREND</div>
                    <svg className="sparkline" viewBox="0 0 220 60" preserveAspectRatio="none">
                        <line x1="0" y1="20" x2="220" y2="20" stroke="#4A4A4A" strokeWidth="0.5" />
                        <line x1="0" y1="40" x2="220" y2="40" stroke="#4A4A4A" strokeWidth="0.5" />
                        {data ? (
                            <polyline points="0,45 36,40 72,35 108,28 144,25 180,22 216,18"
                                fill="none" stroke="#00FF41" strokeWidth="2" strokeLinejoin="miter"
                                style={{ filter: 'drop-shadow(0 0 4px rgba(0,255,65,0.6))' }} />
                        ) : (
                            <text x="110" y="35" fill="#4A4A4A" fontFamily="JetBrains Mono" fontSize="9" textAnchor="middle">NO DATA</text>
                        )}
                    </svg>
                </div>
            </div>
        </>
    )
}
