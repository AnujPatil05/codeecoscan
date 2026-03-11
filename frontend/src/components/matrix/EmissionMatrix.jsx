import EmissionChart from './EmissionChart.jsx'
import CommitTable from './CommitTable.jsx'

export default function EmissionMatrix({ onOpenDiff }) {
    return (
        <>
            <div className="matrix-header">
                <div className="matrix-title">EMISSION MATRIX</div>
                <div className="ms-sep" />
                <div className="matrix-stat">
                    <div className="ms-label">TOTAL CO₂ ELIMINATED</div>
                    <div className="ms-val green">0.84 kg</div>
                </div>
                <div className="ms-sep" />
                <div className="matrix-stat">
                    <div className="ms-label">REFACTORS APPLIED</div>
                    <div className="ms-val green">12</div>
                </div>
                <div className="ms-sep" />
                <div className="matrix-stat">
                    <div className="ms-label">CURRENT DEBT</div>
                    <div className="ms-val red">4.89 kg/yr</div>
                </div>
                <div className="ms-sep" />
                <div className="matrix-stat">
                    <div className="ms-label">TREND</div>
                    <div className="ms-val green">↓ IMPROVING</div>
                </div>
                <div style={{ marginLeft: 'auto' }}>
                    <button className="btn-small primary">EXPORT CSV</button>
                </div>
            </div>

            <div className="matrix-body">
                <EmissionChart />
                <CommitTable onOpenDiff={onOpenDiff} />
            </div>
        </>
    )
}
