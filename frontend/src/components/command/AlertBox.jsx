import { ALERTS } from '../../data/mockData.js'

export default function AlertBox() {
    return (
        <div className="cmd-alert-box">
            <div className="alert-header">
                <div className="alert-blink" />
                ACTIVE CRITICAL ALERTS — {ALERTS.length}
            </div>
            {ALERTS.map((a, i) => (
                <div key={i} className="alert-item">
                    <span>{a.text}</span>
                    <span className={`alert-tag${a.warn ? ' warn' : ''}`}>{a.tag}</span>
                </div>
            ))}
        </div>
    )
}
