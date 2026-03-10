import { useState, useCallback, useRef } from 'react'

const API_BASE = 'https://codeecoscan.onrender.com'
const DEBOUNCE_MS = 800

export default function useAnalysis() {
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [scoreHistory, setHistory] = useState([])
    const debounceRef = useRef(null)
    const controllerRef = useRef(null)
    const cacheRef = useRef({})    // code → result cache

    const analyze = useCallback(async (code) => {
        if (!code.trim()) return

        if (debounceRef.current) clearTimeout(debounceRef.current)

        debounceRef.current = setTimeout(async () => {
            // ── Cache hit ──────────────────────────────────────
            if (cacheRef.current[code]) {
                setResult(cacheRef.current[code])
                setError(null)
                setLoading(false)
                return
            }

            // ── Cancel any in-flight request ───────────────────
            if (controllerRef.current) controllerRef.current.abort()
            controllerRef.current = new AbortController()

            setLoading(true)
            setError(null)

            try {
                const res = await fetch(`${API_BASE}/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code }),
                    signal: controllerRef.current.signal,
                })

                if (res.status === 400) {
                    const data = await res.json()
                    setError(`Syntax error: ${data.detail}`)
                    setResult(null)
                } else if (!res.ok) {
                    setError(`API error: ${res.status}`)
                    setResult(null)
                } else {
                    const data = await res.json()
                    cacheRef.current[code] = data          // store in cache
                    setResult(data)
                    setHistory(h => [...h.slice(-19), data.risk_assessment.energy_risk_score])
                }
            } catch (err) {
                if (err.name === 'AbortError') return
                setError('Cannot reach API. Is it deployed?')
                setResult(null)
            } finally {
                setLoading(false)
            }
        }, DEBOUNCE_MS)
    }, [])

    return { result, loading, error, analyze, scoreHistory }
}
