import { useState, useCallback, useRef } from 'react'
import InputPanel from './InputPanel.jsx'
import LensHeader from './LensHeader.jsx'
import CodePanel from './CodePanel.jsx'
import ScoreBreakdown from './ScoreBreakdown.jsx'
import Suggestions from './Suggestions.jsx'
import { analyzeCode } from '../../api/client.js'
import useRepoSummary from '../../hooks/useRepoSummary.js'
import {
    breakdownFromAPI,
    heatMapFromIssues,
    tooltipMapFromIssues,
    codeLinesToDisplay,
    generateSuggestions,
} from '../../utils/analysisHelpers.js'

const DEBOUNCE_MS = 800

export default function LensWorkspace() {
    // ── Code analysis state ────────────────────────────────────────
    const [result, setResult] = useState(null)
    const [code, setCode] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const cacheRef = useRef({})
    const abortRef = useRef(null)
    const timerRef = useRef(null)

    // ── Repo scan state (via polling hook) ─────────────────────────
    const {
        data: repoData,
        loading: repoLoading,
        status: repoStatus,
        elapsed: repoElapsed,
        error: repoError,
        fetchSummary,
    } = useRepoSummary()

    // Combined loading / error for InputPanel
    const panelLoading = loading || repoLoading
    const panelError = error || repoError

    // ── Paste / file analyze ───────────────────────────────────────
    const analyze = useCallback(async (inputCode) => {
        setCode(inputCode)
        setError(null)

        if (cacheRef.current[inputCode]) {
            setResult(cacheRef.current[inputCode])
            setLoading(false)
            return
        }

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

    // ── Repo scan handler (called from InputPanel GITHUB REPO tab) ─
    const handleScanRepo = useCallback((repoUrl) => {
        setResult(null)   // clear existing code analysis
        setCode('')
        fetchSummary(repoUrl)
    }, [fetchSummary])

    // ── Derive display data ────────────────────────────────────────
    const assessment = result?.risk_assessment
    const features = result?.extracted_features
    const issues = result?.issues || []
    const heatMap = heatMapFromIssues(issues)
    const tipMap = tooltipMapFromIssues(issues)
    const codeLines = codeLinesToDisplay(code, heatMap, tipMap)
    const breakdown = result ? breakdownFromAPI(assessment?.risk_breakdown, features) : []
    const suggestions = result ? generateSuggestions(features, issues) : []

    const scoreNum = assessment?.energy_risk_score ?? null
    const riskCls = scoreNum == null ? '' : scoreNum >= 70 ? 'danger' : scoreNum >= 40 ? 'warn' : 'ok'

    // Repo-mode display
    const isRepoMode = repoLoading || !!repoData
    const repoScore = repoData?.energy_risk ?? null
    const repoRiskCls = repoScore == null ? '' : repoScore >= 70 ? 'danger' : repoScore >= 40 ? 'warn' : 'ok'

    // CodePanel content depends on mode
    const panelTitle = isRepoMode
        ? (repoLoading ? `▶ SCANNING REPO — ${repoStatus?.toUpperCase()} ${repoElapsed}s…` : `⊡ REPO — ${repoData?.repo_name}`)
        : (result ? `⚠ CODE ANALYSIS — ${assessment?.risk_level?.toUpperCase() || 'UNKNOWN'}` : '⊡ AWAITING INPUT')
    const panelTitleCls = isRepoMode ? repoRiskCls : (result ? riskCls : '')
    const panelScore = isRepoMode
        ? (repoScore != null ? `${repoScore} / 100` : '—')
        : (scoreNum != null ? `${scoreNum} / 100` : '—')
    const panelScoreCls = isRepoMode ? repoRiskCls : riskCls

    const emptyLines = [{ num: 1, rawText: '# Paste code and click ANALYZE ▶', heat: 'heat-0' }]

    // Repo mode code panel: show top files as lines
    const repoLines = repoData?.top_files?.length
        ? repoData.top_files.map((f, i) => ({
            num: i + 1,
            rawText: `${f.file.padEnd(40)} RISK: ${f.score}/100`,
            heat: f.score >= 70 ? 'heat-5' : f.score >= 40 ? 'heat-3' : 'heat-1',
        }))
        : emptyLines

    // Breakdown for repo mode
    const repoBreakdown = repoData ? [
        { label: 'REPO ENERGY RISK', value: repoData.energy_risk, max: 100, desc: `${repoData.files_scanned} files scanned` },
        { label: 'ENERGY / DAY', value: Math.min(repoData.energy_per_day * 10, 100), max: 100, desc: `${repoData.energy_per_day} Wh/day` },
        { label: 'HIGH RISK FILES', value: (repoData.alerts?.length / Math.max(repoData.files_scanned, 1)) * 100, max: 100, desc: `${repoData.alerts?.length} alerts` },
    ] : []

    const activeBreakdown = isRepoMode ? repoBreakdown : breakdown
    const activeSuggestions = isRepoMode
        ? (repoData?.alerts?.slice(0, 3).map(a => `${a.file}: ${a.issue}`) || [])
        : suggestions

    return (
        <>
            <LensHeader
                score={isRepoMode ? repoScore : scoreNum}
                file={isRepoMode ? repoData?.repo_name : (code ? 'input.py' : null)}
                live={isRepoMode ? null : result}
            />
            <div className="lens-body">
                <InputPanel
                    onAnalyze={analyze}
                    onScanRepo={handleScanRepo}
                    loading={panelLoading}
                    error={panelError}
                />

                <CodePanel
                    title={panelTitle}
                    titleCls={panelTitleCls}
                    score={panelScore}
                    scoreCls={panelScoreCls}
                    lines={isRepoMode ? repoLines : (codeLines.length ? codeLines : emptyLines)}
                />

                <div className="lens-breakdown">
                    <div className="panel-header">
                        {isRepoMode ? 'REPO SUMMARY' : 'SCORE BREAKDOWN'}
                    </div>
                    {(result || repoData) ? (
                        <>
                            <ScoreBreakdown items={activeBreakdown} />
                            <Suggestions items={activeSuggestions} />
                        </>
                    ) : (
                        <div style={{ padding: 16, fontSize: 11, color: 'var(--muted)' }}>
                            {repoLoading
                                ? `▶ ${repoStatus?.toUpperCase()} — ${repoElapsed}s elapsed…`
                                : 'Analyze code or scan a repo to see results.'}
                        </div>
                    )}
                </div>
            </div>
        </>
    )
}
