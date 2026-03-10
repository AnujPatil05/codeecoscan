export default function StatusBar({ result, features, loading }) {
    return (
        <footer className="status-bar">
            <div className="status-bar__item">
                API <span>codeecoscan.onrender.com</span>
            </div>
            {features && (
                <>
                    <div className="status-bar__item">
                        Loop depth <span>{features.max_loop_depth}</span>
                    </div>
                    <div className="status-bar__item">
                        Recursion <span>{features.has_recursion ? 'yes' : 'no'}</span>
                    </div>
                    <div className="status-bar__item">
                        Heavy imports <span>{features.heavy_imports_detected.length}</span>
                    </div>
                </>
            )}
            {loading && (
                <div className="status-bar__item" style={{ marginLeft: 'auto' }}>
                    <span>scanning…</span>
                </div>
            )}
            {!loading && !result && (
                <div className="status-bar__item" style={{ marginLeft: 'auto' }}>
                    <span style={{ color: 'var(--dim)' }}>awaiting input</span>
                </div>
            )}
        </footer>
    )
}
