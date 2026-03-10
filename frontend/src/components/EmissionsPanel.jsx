import { useState, useMemo } from 'react'

const PROFILES = [
    { id: 'laptop', label: 'Laptop', watts: 45 },
    { id: 'small_cloud_vm', label: 'Cloud VM', watts: 120 },
    { id: 'gpu_server', label: 'GPU Server', watts: 300 },
]

const CARBON_INTENSITY = 0.4   // kg CO₂/kWh default (IEA global avg)

function computeEmissions(watts, runtimeSec, runsPerDay) {
    const whPerRun = (watts * runtimeSec) / 3600
    const whPerDay = whPerRun * runsPerDay
    const co2PerDay = (whPerDay / 1000) * CARBON_INTENSITY
    return { whPerDay, co2PerDay }
}

export default function EmissionsPanel({ assessment }) {
    const [open, setOpen] = useState(false)
    const [profile, setProfile] = useState('laptop')
    const [runtime, setRuntime] = useState(60)
    const [runsPerDay, setRuns] = useState(10)

    const watts = PROFILES.find(p => p.id === profile)?.watts ?? 45

    const { whPerDay, co2PerDay } = useMemo(
        () => computeEmissions(watts, runtime, runsPerDay),
        [watts, runtime, runsPerDay]
    )

    return (
        <div className="emissions-section">
            <button
                className="emissions-toggle"
                onClick={() => setOpen(o => !o)}
            >
                ◈  Emissions Estimator
                <span className={`emissions-toggle__arrow ${open ? 'open' : ''}`}>▾</span>
            </button>

            {open && (
                <div className="emissions-body">
                    {/* Profile selector */}
                    <div>
                        <div className="breakdown-title" style={{ marginBottom: '0.5rem' }}>
                            Hardware Profile
                        </div>
                        <div className="emissions-grid">
                            {PROFILES.map(p => (
                                <button
                                    key={p.id}
                                    className={`profile-btn ${profile === p.id ? 'selected' : ''}`}
                                    onClick={() => setProfile(p.id)}
                                >
                                    {p.label}
                                    <br />
                                    <span style={{ fontSize: '0.55rem', opacity: 0.6 }}>{p.watts}W</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Runtime slider */}
                    <div className="slider-group">
                        <div className="slider-label">
                            Runtime / run
                            <span>{runtime}s</span>
                        </div>
                        <input
                            type="range" min={1} max={3600} step={1}
                            value={runtime}
                            onChange={e => setRuntime(Number(e.target.value))}
                        />
                    </div>

                    {/* Runs/day slider */}
                    <div className="slider-group">
                        <div className="slider-label">
                            Runs per day
                            <span>{runsPerDay}</span>
                        </div>
                        <input
                            type="range" min={1} max={1000} step={1}
                            value={runsPerDay}
                            onChange={e => setRuns(Number(e.target.value))}
                        />
                    </div>

                    {/* Results */}
                    <div className="emissions-result">
                        <div className="emissions-stat">
                            <div className="emissions-stat__label">Energy</div>
                            <div className="emissions-stat__value">{whPerDay.toFixed(2)}</div>
                            <div className="emissions-stat__unit">Wh / day</div>
                        </div>
                        <div className="emissions-stat">
                            <div className="emissions-stat__label">CO₂</div>
                            <div className="emissions-stat__value">{co2PerDay.toFixed(4)}</div>
                            <div className="emissions-stat__unit">kg / day</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
