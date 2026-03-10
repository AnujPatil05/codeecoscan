import { useState } from 'react'
import Header from './components/Header.jsx'
import Editor from './components/Editor.jsx'
import EnergyGauge from './components/EnergyGauge.jsx'
import Breakdown from './components/Breakdown.jsx'
import Sparkline from './components/Sparkline.jsx'
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
    const { result, loading, error, analyze, scoreHistory } = useAnalysis()

    const assessment = result?.risk_assessment
    const features = result?.extracted_features

    const handleChange = (val) => {
        setCode(val)
        analyze(val)
    }

    return (
        <div className="app">
            <Header />

            <main className="workspace">
                {/* ── Left: Editor ── */}
                <section className="editor-pane">
                    <div className="pane-label">
                        INPUT.PY
                        <div className="pane-label__status">
                            <span
                                className={`status-dot ${loading ? 'active' : error ? 'error' : result ? 'active' : ''}`}
                            />
                            {loading ? 'ANALYZING CODE…' : error ? 'ERROR' : result ? 'READY' : 'IDLE'}
                        </div>
                    </div>

                    <div className="editor-wrapper">
                        <Editor value={code} onChange={handleChange} />
                    </div>

                    <div className="editor-footer">
                        <button
                            className="scan-btn"
                            onClick={() => analyze(code)}
                            disabled={loading || !code.trim()}
                        >
                            {loading ? '◌  ANALYZING…' : '⬡  SCAN CODE'}
                        </button>
                        {scoreHistory.length >= 2 && <Sparkline history={scoreHistory} />}
                    </div>

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
                                {loading ? 'SCANNING…' : 'Paste Python code and scan'}
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
