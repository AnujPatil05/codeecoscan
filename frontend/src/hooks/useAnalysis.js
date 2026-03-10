import { useState, useCallback, useRef } from 'react'

const API_BASE = 'https://codeecoscan.onrender.com'
const DEBOUNCE_MS = 800

export default function useAnalysis() {
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const debounceRef = useRef(null)

    const analyze = useCallback(async (code) => {
        if (!code.trim()) return

        // Clear previous debounce
        if (debounceRef.current) clearTimeout(debounceRef.current)

        debounceRef.current = setTimeout(async () => {
            setLoading(true)
            setError(null)

            try {
                const res = await fetch(`${API_BASE}/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code }),
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
                    setResult(data)
                }
            } catch (err) {
                setError('Cannot reach API. Is it deployed?')
                setResult(null)
            } finally {
                setLoading(false)
            }
        }, DEBOUNCE_MS)
    }, [])

    return { result, loading, error, analyze }
}
