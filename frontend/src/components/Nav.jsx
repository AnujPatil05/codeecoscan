import { useState, useEffect } from 'react'
import TelemetryDot from './shared/TelemetryDot.jsx'

const TABS = [
    { id: 'command', label: 'COMMAND CENTER', num: '01' },
    { id: 'lens', label: 'LENS WORKSPACE', num: '02' },
    { id: 'thermal', label: 'THERMAL HEATMAP', num: '03' },
    { id: 'matrix', label: 'EMISSION MATRIX', num: '04' },
]

export default function Nav({ activeScreen, onSwitch }) {
    const [theme, setTheme] = useState('light')

    useEffect(() => {
        const saved = localStorage.getItem('theme') || 'light'
        setTheme(saved)
        if (saved === 'light') {
            document.documentElement.setAttribute('data-theme', 'light')
        } else {
            document.documentElement.removeAttribute('data-theme')
        }
    }, [])

    const toggleTheme = () => {
        const next = theme === 'dark' ? 'light' : 'dark'
        setTheme(next)
        localStorage.setItem('theme', next)
        if (next === 'light') {
            document.documentElement.setAttribute('data-theme', 'light')
        } else {
            document.documentElement.removeAttribute('data-theme')
        }
    }
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
                <div style={{ marginRight: 16, cursor: 'pointer', fontSize: 11, color: 'var(--muted)', display: 'flex', alignItems: 'center' }} onClick={toggleTheme}>
                    {theme === 'light' ? '☾ DARK' : '☼ LIGHT'}
                </div>
                <div className="nav-status">
                    <TelemetryDot /> CONNECTED
                </div>
            </div>
        </nav>
    )
}
