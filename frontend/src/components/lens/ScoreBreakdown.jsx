import { useEffect, useRef } from 'react'

export default function ScoreBreakdown({ items }) {
    const barsRef = useRef([])

    useEffect(() => {
        const timers = barsRef.current.map((bar, i) => {
            if (!bar) return null
            const target = parseFloat(bar.dataset.target) || 0
            bar.style.width = '0%'
            return setTimeout(() => { bar.style.width = `${target}%` }, 100 + i * 80)
        })
        return () => timers.forEach(t => t && clearTimeout(t))
    }, [items])

    return (
        <div className="lens-breakdown">
            <div className="panel-header">SCORE BREAKDOWN</div>
            <div className="breakdown-list">
                {items.map((b, i) => (
                    <div key={b.name} className="breakdown-item">
                        <div className="bi-top">
                            <div className="bi-name">{b.name}</div>
                            <div className={`bi-score ${b.cls}`}>{b.score}</div>
                        </div>
                        <div className="bi-bar-wrap">
                            <div
                                className="bi-bar"
                                ref={el => barsRef.current[i] = el}
                                data-target={b.barPct}
                                style={{
                                    width: '0%',
                                    background: b.barColor,
                                    boxShadow: b.barGlow || 'none',
                                }}
                            />
                        </div>
                        <div className="bi-desc">{b.desc}</div>
                    </div>
                ))}
            </div>
        </div>
    )
}
