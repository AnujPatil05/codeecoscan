const TABS = [
    { id: 'command', label: 'COMMAND CENTER', num: '01' },
    { id: 'lens', label: 'LENS WORKSPACE', num: '02' },
    { id: 'thermal', label: 'THERMAL HEATMAP', num: '03' },
    { id: 'matrix', label: 'EMISSION MATRIX', num: '04' },
]

export default function Nav({ activeScreen, onSwitch }) {
    return (
        <nav id="nav">
            <div className="nav-logo">CODE<span>ECO</span>SCAN</div>
            <div className="nav-tabs">
                {TABS.map(t => (
                    <div
                        key={t.id}
                        className={`nav-tab${activeScreen === t.id ? ' active' : ''}`}
                        onClick={() => onSwitch(t.id)}
                    >
                        <span className="tab-num">{t.num}</span> {t.label}
                    </div>
                ))}
            </div>
            <div className="nav-right">
                <div className="nav-status"><span className="dot" />CONNECTED</div>
            </div>
        </nav>
    )
}
