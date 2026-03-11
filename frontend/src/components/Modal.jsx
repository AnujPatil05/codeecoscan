/** Modal — shows a diff or info overlay. Content is passed as props. */
export default function Modal({ isOpen, onClose, title, children }) {
    if (!isOpen) return null

    return (
        <div
            className={`modal-overlay${isOpen ? ' open' : ''}`}
            onClick={e => { if (e.target === e.currentTarget) onClose() }}
        >
            <div className="modal-box">
                <div className="modal-header">
                    {title || 'ANALYSIS DETAILS'}
                    <button className="modal-close" onClick={onClose}>[ CLOSE ]</button>
                </div>
                <div style={{ padding: 16, fontFamily: 'var(--font-body)', fontSize: 12, overflowY: 'auto', maxHeight: 400 }}>
                    {children || (
                        <div style={{ color: 'var(--muted)' }}>No content.</div>
                    )}
                </div>
            </div>
        </div>
    )
}
