import { useEffect, useRef } from 'react'
import { LENS_BREAKDOWN } from '../../data/mockData.js'

export default function ScoreBreakdown() {
    const barsRef = useRef([])

    useEffect(() => {
        // Animate bars from 0 to target width on mount
        const timers = barsRef.current.map((bar, i) => {
            if (!bar) return null
            const target = bar.dataset.target
            bar.style.width = '0%'
            return setTimeout(() => {
                bar.style.width = `${target}%`
            }, 100 + i * 80)
        })
        return () => timers.forEach(t => t && clearTimeout(t))
    }, [])

    return (
        <div className="lens-breakdown">
            <div className="panel-header">SCORE BREAKDOWN</div>
            <div className="breakdown-list">
                {LENS_BREAKDOWN.map((b, i) => (
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
