import { TOP_FILES } from '../../data/mockData.js'
import MiniChart from './MiniChart.jsx'

export default function TopOffenders() {
    return (
        <div className="cmd-right">
            <div className="panel-header">TOP ENERGY OFFENDERS</div>
            <div className="top-files">
                {TOP_FILES.map(f => (
                    <div key={f.name} className="file-item">
                        <div className="file-name">{f.name}</div>
                        <div className="file-bar-wrap">
                            <div className="file-bar"
                                style={{
                                    width: `${f.score}%`,
                                    background: f.color,
                                    boxShadow: f.glow || 'none',
                                }}
                            />
                        </div>
                        <div className="file-meta">
                            <span style={{ fontSize: 10, color: 'var(--muted)' }}>RISK</span>
                            <span className="file-score"
                                style={{
                                    color: f.color,
                                    textShadow: f.glow || 'none',
                                }}>
                                {f.score} / 100
                            </span>
                        </div>
                    </div>
                ))}
            </div>
            <MiniChart />
        </div>
    )
}
