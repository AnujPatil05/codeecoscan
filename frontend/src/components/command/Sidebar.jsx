import { REPOS } from '../../data/mockData.js'

export default function Sidebar() {
    return (
        <div className="cmd-sidebar">
            <div className="cmd-sidebar-label">REPOSITORIES</div>
            {REPOS.map(r => (
                <div key={r.name} className={`cmd-sidebar-item${r.active ? ' active' : ''}`}>
                    <span className="si-icon">{r.active ? '▶' : '○'}</span> {r.name}
                </div>
            ))}

            <div className="cmd-sidebar-section-label">SYSTEM</div>
            <div className="cmd-sidebar-item"><span className="si-icon">◇</span> SETTINGS</div>
            <div className="cmd-sidebar-item"><span className="si-icon">◇</span> EXPORT REPORT</div>

            <div className="cmd-sidebar-bottom">
                <div className="sys-metric">CPU <span className="sys-metric-val">12%</span></div>
                <div className="sys-metric">MEM <span className="sys-metric-val">1.2GB</span></div>
                <div className="sys-metric">API <span className="sys-metric-val" style={{ color: 'var(--primary)' }}>LIVE</span></div>
            </div>
        </div>
    )
}
