export default function LensHeader() {
    return (
        <div className="lens-header">
            <div className="lens-metric">
                <div className="lm-label">FILE</div>
                <div className="lm-val" style={{ color: 'var(--text)', fontSize: 13 }}>train.py</div>
            </div>
            <div className="lens-sep" />
            <div className="lens-metric">
                <div className="lm-label">ORIGINAL SCORE</div>
                <div className="lm-val red">92</div>
            </div>
            <div className="lens-sep" />
            <div className="lens-metric">
                <div className="lm-label">REFACTOR SCORE</div>
                <div className="lm-val green">23</div>
            </div>
            <div className="lens-sep" />
            <div className="delta-hud">
                <div>
                    <div className="delta-label">ENERGY DELTA</div>
                    <div className="delta-val">Δ -75%</div>
                </div>
            </div>
            <div className="lens-sep" />
            <div className="lens-metric">
                <div className="lm-label">CO₂ SAVED</div>
                <div className="lm-val green">0.031 kg/day</div>
            </div>
            <div className="lens-actions">
                <button className="btn-small">EXPORT DIFF</button>
                <button className="btn-small primary">APPLY REFACTOR</button>
            </div>
        </div>
    )
}
