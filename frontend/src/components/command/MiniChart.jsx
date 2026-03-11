import { SPARKLINE_POINTS, SPARKLINE_POLYGON } from '../../data/mockData.js'

export default function MiniChart() {
    return (
        <div className="mini-chart">
            <div className="mini-chart-label">7-DAY TREND</div>
            <svg className="sparkline" viewBox="0 0 220 60" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="spGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#00FF41" stopOpacity="0.3" />
                        <stop offset="100%" stopColor="#00FF41" stopOpacity="0" />
                    </linearGradient>
                </defs>
                <line x1="0" y1="20" x2="220" y2="20" stroke="#4A4A4A" strokeWidth="0.5" />
                <line x1="0" y1="40" x2="220" y2="40" stroke="#4A4A4A" strokeWidth="0.5" />
                <polygon points={SPARKLINE_POLYGON} fill="url(#spGrad)" />
                <polyline
                    points={SPARKLINE_POINTS}
                    fill="none" stroke="#00FF41" strokeWidth="2"
                    strokeLinejoin="miter"
                    style={{ filter: 'drop-shadow(0 0 4px rgba(0,255,65,0.6))' }}
                />
                <circle cx="216" cy="18" r="3" fill="#00FF41"
                    style={{ filter: 'drop-shadow(0 0 4px rgba(0,255,65,0.8))' }}
                />
            </svg>
        </div>
    )
}
