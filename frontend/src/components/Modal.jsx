import { DIFF_DATA } from '../data/mockData.js'

export default function Modal({ isOpen, onClose }) {
    if (!isOpen) return null

    return (
        <div className={`modal-overlay${isOpen ? ' open' : ''}`} onClick={(e) => { if (e.target === e.currentTarget) onClose() }}>
            <div className="modal-box">
                <div className="modal-header">
                    COMMIT DIFF — {DIFF_DATA.sha}
                    <button className="modal-close" onClick={onClose}>[ CLOSE ]</button>
                </div>
                <div>
                    {DIFF_DATA.lines.map((l, i) => (
                        <div key={i} className={`diff-line ${l.type}`}>{l.text}</div>
                    ))}
                </div>
                <div className="modal-impact">
                    ENERGY IMPACT: <span style={{ color: 'var(--danger)', fontFamily: 'var(--font-heading)' }}>{DIFF_DATA.impact}</span>&nbsp;&nbsp;
                    RISK RATING: <span style={{ color: 'var(--danger)' }}>{DIFF_DATA.risk}</span>
                </div>
            </div>
        </div>
    )
}
