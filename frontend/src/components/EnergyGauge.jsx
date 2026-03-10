import { useState, useEffect, useRef } from 'react'

const LEVEL_CLASS = { Low: 'low', Moderate: 'moderate', High: 'high' }

/** Animate a number from `from` to `to` over `duration`ms, calling `onTick` each frame. */
function useCountUp(target, duration = 700) {
    const [display, setDisplay] = useState(target)
    const prev = useRef(target)
    const rafRef = useRef(null)

    useEffect(() => {
        const start = prev.current
        const startTime = performance.now()

        if (rafRef.current) cancelAnimationFrame(rafRef.current)

        const tick = (now) => {
            const elapsed = now - startTime
            const progress = Math.min(elapsed / duration, 1)
            // ease-out cubic
            const ease = 1 - Math.pow(1 - progress, 3)
            setDisplay(Math.round(start + (target - start) * ease))
            if (progress < 1) rafRef.current = requestAnimationFrame(tick)
            else prev.current = target
        }

        rafRef.current = requestAnimationFrame(tick)
        return () => cancelAnimationFrame(rafRef.current)
    }, [target, duration])

    return display
}

const TICKS = [100, 80, 60, 40, 20, 0]

export default function EnergyGauge({ assessment }) {
    const { energy_risk_score: score, risk_level } = assessment
    const cls = LEVEL_CLASS[risk_level] ?? 'low'
    const displayed = useCountUp(score)

    return (
        <div className="gauge-section">
            {/* Vertical meter with tick marks */}
            <div className="gauge-wrap">
                <div className="gauge-label-top">100</div>

                <div className="gauge-outer">
                    {/* Tick marks on the left */}
                    <div className="gauge-ticks-col">
                        {TICKS.map(t => (
                            <div className="gauge-tick-row" key={t}>
                                <span className="gauge-tick-label">{t}</span>
                                <span className="gauge-tick-line" />
                            </div>
                        ))}
                    </div>

                    {/* The bar */}
                    <div className="gauge-track">
                        <div
                            className={`gauge-fill ${cls}`}
                            style={{ height: `${score}%` }}
                        />
                    </div>
                </div>

                <div className="gauge-label">PWR</div>
            </div>

            {/* Score info */}
            <div className="gauge-info">
                <div className="gauge-context-label">ENERGY RISK</div>
                <div className="score-display">
                    <div className={`score-number ${cls}`}>{displayed}</div>
                    <div className="score-max">/ 100</div>
                    <div className={`risk-badge ${cls}`}>{risk_level}</div>
                </div>
            </div>
        </div>
    )
}
