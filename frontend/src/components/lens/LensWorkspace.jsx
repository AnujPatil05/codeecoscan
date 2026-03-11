import { useState, useCallback, useRef } from 'react'
import InputPanel from './InputPanel.jsx'
import LensHeader from './LensHeader.jsx'
import CodePanel from './CodePanel.jsx'
import ScoreBreakdown from './ScoreBreakdown.jsx'
import Suggestions from './Suggestions.jsx'
import { analyzeCode } from '../../api/client.js'
import {
    breakdownFromAPI,
    heatMapFromIssues,
    tooltipMapFromIssues,
    codeLinesToDisplay,
    generateSuggestions,
} from '../../utils/analysisHelpers.js'

const DEBOUNCE_MS = 800

export default function LensWorkspace() {
    const [result, setResult] = useState(null)    // API response
    const [code, setCode] = useState('')       // current analyzed code
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const cacheRef = useRef({})
    const abortRef = useRef(null)
    const timerRef = useRef(null)

    const analyze = useCallback(async (inputCode) => {
        setCode(inputCode)
        setError(null)

        // Cache hit
        if (cacheRef.current[inputCode]) {
            setResult(cacheRef.current[inputCode])
            setLoading(false)
            return
        }

        // Cancel in-flight
        if (abortRef.current) abortRef.current.abort()
        if (timerRef.current) clearTimeout(timerRef.current)
        abortRef.current = new AbortController()

        setLoading(true)
        timerRef.current = setTimeout(async () => {
            try {
                const data = await analyzeCode(inputCode, abortRef.current.signal)
                cacheRef.current[inputCode] = data
                setResult(data)
                setError(null)
            } catch (err) {
                if (err.name === 'AbortError') return
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }, DEBOUNCE_MS)
    }, [])

    // Derive display data from API result
    const assessment = result?.risk_assessment
    const features = result?.extracted_features
    const issues = result?.issues || []

    const heatMap = heatMapFromIssues(issues)
    const tipMap = tooltipMapFromIssues(issues)
    const codeLines = codeLinesToDisplay(code, heatMap, tipMap)
    const breakdown = result
        ? breakdownFromAPI(assessment?.risk_breakdown, features)
        : []
    const suggestions = result
        ? generateSuggestions(features, issues)
        : []

    const scoreNum = assessment?.energy_risk_score ?? null
    const riskCls = scoreNum == null ? '' : scoreNum >= 70 ? 'danger' : scoreNum >= 40 ? 'warn' : 'ok'

    const emptyLines = [{ num: 1, rawText: '# Paste code and click ANALYZE ▶', heat: 'heat-0' }]

    return (
        <>
            <LensHeader
                score={scoreNum}
                refactorScore={null}
                delta={null}
                file={code ? 'input.py' : null}
                live={result}
            />
            <div className="lens-body">
                {/* Input panel */}
                <InputPanel onAnalyze={analyze} loading={loading} error={error} />

                {/* Code panel with heatmap */}
                <CodePanel
                    title={
                        result
                            ? `⚠ CODE ANALYSIS — ${assessment?.risk_level?.toUpperCase() || 'UNKNOWN'}`
                            : '⊡ AWAITING INPUT'
                    }
                    titleCls={result ? (scoreNum >= 70 ? 'danger' : scoreNum >= 40 ? 'warn' : 'ok') : ''}
                    score={scoreNum != null ? `${scoreNum} / 100` : '—'}
                    scoreCls={riskCls}
                    lines={codeLines.length ? codeLines : emptyLines}
                />

                {/* Breakdown sidebar with suggestions */}
                <div className="lens-breakdown">
                    <div className="panel-header">SCORE BREAKDOWN</div>
                    {result ? (
                        <>
                            <ScoreBreakdown items={breakdown} />
                            <Suggestions items={suggestions} />
                        </>
                    ) : (
                        <div style={{ padding: 16, fontSize: 11, color: 'var(--muted)' }}>
                            Analyze code to see breakdown.
                        </div>
                    )}
                </div>
            </div>
        </>
    )
}
