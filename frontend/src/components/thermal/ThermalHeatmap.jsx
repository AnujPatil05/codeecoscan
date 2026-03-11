import ThermalCode from './ThermalCode.jsx'
import FunctionList from './FunctionList.jsx'
import HeatProfile from './HeatProfile.jsx'

export default function ThermalHeatmap() {
    return (
        <>
            <div className="thermal-header">
                <div className="thermal-title">THERMAL HEATMAP</div>
                <div className="thermal-file">▶ train.py — CRITICAL HOTSPOTS: 3</div>
                <div className="heat-legend">
                    <div className="hl-item">
                        <div className="hl-swatch" style={{ background: 'rgba(0,0,0,0)', border: '1px solid var(--muted)' }} />
                        EFFICIENT
                    </div>
                    <div className="hl-item">
                        <div className="hl-swatch" style={{ background: 'rgba(255,176,0,0.3)' }} />
                        WARNING
                    </div>
                    <div className="hl-item">
                        <div className="hl-swatch" style={{ background: 'rgba(255,0,60,0.4)' }} />
                        CRITICAL
                    </div>
                </div>
            </div>

            <div className="thermal-body">
                <ThermalCode />
                <div className="thermal-sidebar">
                    <div className="panel-header">FUNCTION ENERGY DRAIN</div>
                    <FunctionList />
                    <HeatProfile />
                </div>
            </div>
        </>
    )
}
