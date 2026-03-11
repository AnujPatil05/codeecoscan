import { useState, useCallback } from 'react'
import { analyzeRepo } from '../api/client.js'

/**
 * Hook for fetching repository summary.
 * Structure is ready for live API — currently wraps the /analyze_repo endpoint.
 */
export default function useRepoSummary() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const fetchSummary = useCallback(async (repoUrl) => {
        if (!repoUrl?.trim()) return
        setLoading(true)
        setError(null)
        try {
            const result = await analyzeRepo(repoUrl)
            setData(result)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }, [])

    return { data, loading, error, fetchSummary }
}
