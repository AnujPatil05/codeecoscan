import { useState, useCallback, useRef } from 'react'
import { analyzeRepo } from '../api/client.js'

/** Hook for scanning a GitHub repository. */
export default function useRepoSummary() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const abortRef = useRef(null)

    const fetchSummary = useCallback(async (repoUrl) => {
        if (!repoUrl?.trim()) return
        if (abortRef.current) abortRef.current.abort()
        abortRef.current = new AbortController()
        setLoading(true)
        setError(null)
        try {
            const result = await analyzeRepo(repoUrl, abortRef.current.signal)
            setData(result)
        } catch (err) {
            if (err.name === 'AbortError') return
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }, [])

    return { data, loading, error, fetchSummary }
}
