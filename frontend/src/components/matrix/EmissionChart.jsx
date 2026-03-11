export default function EmissionChart() {
    return (
        <div className="chart-area">
            <svg width="100%" height="100%" viewBox="0 0 900 200" preserveAspectRatio="xMidYMid meet" style={{ display: 'block' }}>
                <defs>
                    <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#00FF41" stopOpacity="0.15" />
                        <stop offset="100%" stopColor="#00FF41" stopOpacity="0" />
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                        <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
                    </filter>
                </defs>

                {/* Y-axis label */}
                <text x="8" y="100" fill="#4A4A4A" fontFamily="JetBrains Mono" fontSize="10"
                    transform="rotate(-90, 8, 100)" textAnchor="middle">kgCO₂/yr</text>

                {/* Grid */}
                {[20, 60, 100, 140, 180].map(y => (
                    <line key={y} x1="40" y1={y} x2="880" y2={y} stroke="#4A4A4A" strokeWidth="0.5" />
                ))}

                {/* Y labels */}
                {[
                    { y: 23, t: '8.0' }, { y: 63, t: '6.0' }, { y: 103, t: '4.0' },
                    { y: 143, t: '2.0' }, { y: 183, t: '0' },
                ].map(l => (
                    <text key={l.y} x="36" y={l.y} fill="#4A4A4A" fontFamily="JetBrains Mono" fontSize="10" textAnchor="end">{l.t}</text>
                ))}

                {/* Area fill */}
                <polygon
                    points="40,50 160,55 260,80 330,65 430,90 530,105 620,115 700,122 800,128 880,131 880,180 40,180"
                    fill="url(#chartGrad)"
                />

                {/* Chart line (sharp, no curves) */}
                <polyline
                    points="40,50 160,55 260,80 330,65 430,90 530,105 620,115 700,122 800,128 880,131"
                    fill="none" stroke="#00FF41" strokeWidth="2" strokeLinejoin="miter"
                    filter="url(#glow)"
                />

                {/* Target line */}
                <line x1="40" y1="60" x2="880" y2="60" stroke="#FFB000" strokeWidth="1" strokeDasharray="4,4" opacity="0.5" />
                <text x="885" y="63" fill="#FFB000" fontFamily="JetBrains Mono" fontSize="9">TARGET</text>

                {/* Data points */}
                <circle cx="40" cy="50" r="4" fill="#FF003C" filter="url(#glow)" />
                <circle cx="260" cy="80" r="3" fill="#FFB000" />
                <circle cx="530" cy="105" r="3" fill="#FFB000" />
                <circle cx="880" cy="131" r="4" fill="#00FF41" filter="url(#glow)" />

                {/* X labels */}
                {[
                    { x: 40, t: 'MAR 4' }, { x: 160, t: 'MAR 5' }, { x: 280, t: 'MAR 6' },
                    { x: 400, t: 'MAR 7' }, { x: 520, t: 'MAR 8' }, { x: 640, t: 'MAR 9' },
                    { x: 760, t: 'MAR 10' },
                ].map(l => (
                    <text key={l.x} x={l.x} y="196" fill="#4A4A4A" fontFamily="JetBrains Mono" fontSize="9" textAnchor="middle">{l.t}</text>
                ))}
                <text x="880" y="196" fill="#00FF41" fontFamily="JetBrains Mono" fontSize="9" textAnchor="middle"
                    style={{ filter: 'drop-shadow(0 0 4px rgba(0,255,65,0.6))' }}>MAR 11</text>
            </svg>
        </div>
    )
}
