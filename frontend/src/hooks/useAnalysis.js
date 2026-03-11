import { useState, useCallback, useRef } from 'react'
import { analyzeCode } from '../api/client.js'

const DEBOUNCE_MS = 800

export default function useAnalysis() {
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const debounceRef = useRef(null)
    const controllerRef = useRef(null)
    const cacheRef = useRef({})

    const analyze = useCallback(async (code) => {
        if (!code?.trim()) return
        if (debounceRef.current) clearTimeout(debounceRef.current)

        debounceRef.current = setTimeout(async () => {
            if (cacheRef.current[code]) {
                setResult(cacheRef.current[code])
                setError(null)
                return
            }
            if (controllerRef.current) controllerRef.current.abort()
            controllerRef.current = new AbortController()
            setLoading(true)
            setError(null)

            try {
                const data = await analyzeCode(code, controllerRef.current.signal)
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
