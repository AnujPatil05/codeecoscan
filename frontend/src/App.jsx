import { useState } from 'react'
import Header from './components/Header.jsx'
import Editor from './components/Editor.jsx'
import EnergyGauge from './components/EnergyGauge.jsx'
import Breakdown from './components/Breakdown.jsx'
import EmissionsPanel from './components/EmissionsPanel.jsx'
import StatusBar from './components/StatusBar.jsx'
import useAnalysis from './hooks/useAnalysis.js'

const STARTER_CODE = `import torch
import pandas as pd

def train(data):
    results = []
    for batch in data:
        for sample in batch:
            processed = abs(sample)
            results.append(processed)
    return results
`

export default function App() {
    const [code, setCode] = useState(STARTER_CODE)
    const { result, loading, error, analyze } = useAnalysis()

    const assessment = result?.risk_assessment
    const features = result?.extracted_features

    return (
        <div className="app">
            <Header />

            <main className="workspace">
                {/* ── Left: Editor ── */}
                <section className="editor-pane">
                    <div className="pane-label">
                        input.py
                        <div className="pane-label__status">
                            <span
                                className={`status-dot ${loading ? 'active' : error ? 'error' : result ? 'active' : ''}`}
                            />
                            {loading ? 'scanning…' : error ? 'error' : result ? 'ready' : 'idle'}
                        </div>
                    </div>

                    <div className="editor-wrapper">
                        <Editor value={code} onChange={setCode} />
                    </div>

                    <button
                        className="scan-btn"
                        onClick={() => analyze(code)}
                        disabled={loading || !code.trim()}
                    >
                        {loading ? '◌  scanning' : '⬡  scan code'}
                    </button>

                    {error && <div className="error-msg">⚠ {error}</div>}
                </section>

                {/* ── Right: Diagnostics ── */}
                <section className="diagnostics-pane">
                    {assessment ? (
                        <>
                            <EnergyGauge assessment={assessment} />
                            <Breakdown assessment={assessment} />
                        </>
                    ) : (
                        <div className="empty-state">
                            <div className="empty-state__icon">◈</div>
                            <div className="empty-state__text">
                                Paste Python code and hit scan
                            </div>
                        </div>
                    )}
                </section>
            </main>

            {/* ── Bottom: Emissions ── */}
            <EmissionsPanel assessment={assessment} />

            {/* ── Status bar ── */}
            <StatusBar result={result} features={features} loading={loading} />
        </div>
    )
}
