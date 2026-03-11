import { useState, useCallback, useRef } from 'react'
import { analyzeCode } from '../api/client.js'

const DEBOUNCE_MS = 800

/** Hook for code analysis with debounce + cache + AbortController. */
export default function useAnalysis() {
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const cacheRef = useRef({})
    const abortRef = useRef(null)
    const timerRef = useRef(null)

    const analyze = useCallback(async (code) => {
        if (!code?.trim()) return
        setError(null)

        if (cacheRef.current[code]) {
            setResult(cacheRef.current[code])
            setLoading(false)
            return
        }

        if (abortRef.current) abortRef.current.abort()
        if (timerRef.current) clearTimeout(timerRef.current)
        abortRef.current = new AbortController()
        setLoading(true)

        timerRef.current = setTimeout(async () => {
            try {
                const data = await analyzeCode(code, abortRef.current.signal)
                cacheRef.current[code] = data
                setResult(data)
            } catch (err) {
                if (err.name === 'AbortError') return
                setError(err.message)
                setResult(null)
            } finally {
                setLoading(false)
            }
        }, DEBOUNCE_MS)
    }, [])

    return { result, loading, error, analyze }
}
