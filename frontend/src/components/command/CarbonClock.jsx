import { useCarbonClock } from '../../hooks/useClock.js'

export default function CarbonClock({ onInitiateLens }) {
    const display = useCarbonClock(4.892)

    return (
        <div className="carbon-clock-wrap">
            <div className="cmd-label">TOTAL CARBON DEBT — REPO: CODELOG-BACKEND</div>
            <div className="carbon-clock">{display}</div>
            <div className="carbon-clock-unit">kgCO₂ / YEAR — TICKING</div>
            <button className="cmd-scan-btn" onClick={onInitiateLens} style={{ marginTop: 20 }}>
                <span className="btn-icon">⊕</span> INITIATE LENS
            </button>
        </div>
    )
}
